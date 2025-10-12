"""
AI Tutor API
Handles document upload and AI-powered question answering for students
"""

import os
import uuid
import tempfile
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import openai
import PyPDF2
import docx
import io
import re

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# Initialize OpenAI
openai_api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("SUMMARY_API_KEY")

router = APIRouter(prefix="/api/ai-tutor", tags=["ai-tutor"])

class QuestionRequest(BaseModel):
    file_id: str
    question: str
    user_id: str

class AnswerResponse(BaseModel):
    answer: str
    context_chunks: List[str]
    tokens_used: int
    cost_usd: float

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from uploaded file based on file type"""
    try:
        if filename.lower().endswith('.pdf'):
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif filename.lower().endswith(('.doc', '.docx')):
            # Extract text from Word document
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        elif filename.lower().endswith('.txt'):
            # Extract text from plain text file
            return file_content.decode('utf-8')
        
        else:
            raise ValueError("Unsupported file type")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from file: {str(e)}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better context retrieval"""
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def find_relevant_chunks(chunks: List[str], question: str, max_chunks: int = 3) -> List[str]:
    """Find the most relevant chunks for the question using simple keyword matching"""
    # Simple keyword-based relevance scoring
    question_words = set(question.lower().split())
    
    chunk_scores = []
    for i, chunk in enumerate(chunks):
        chunk_words = set(chunk.lower().split())
        # Calculate overlap score
        overlap = len(question_words.intersection(chunk_words))
        score = overlap / len(question_words) if question_words else 0
        chunk_scores.append((score, i, chunk))
    
    # Sort by score and return top chunks
    chunk_scores.sort(reverse=True)
    return [chunk for _, _, chunk in chunk_scores[:max_chunks]]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """Upload and process a document for AI tutoring"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from file
        text_content = extract_text_from_file(file_content, file.filename)
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the file")
        
        # Create chunks
        chunks = chunk_text(text_content)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Store document in database
        document_record = {
            'id': file_id,
            'user_id': user_id,
            'filename': file.filename,
            'file_size': len(file_content),
            'text_content': text_content,
            'chunks': chunks,
            'chunk_count': len(chunks),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('ai_tutor_documents').insert(document_record).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to store document")
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "message": "Document uploaded and processed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about an uploaded document"""
    try:
        # Retrieve document from database
        doc_response = supabase.table('ai_tutor_documents').select('*').eq('id', request.file_id).single().execute()
        
        if not doc_response.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_response.data
        
        # Verify user owns the document
        if document['user_id'] != request.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Find relevant chunks
        chunks = document['chunks']
        relevant_chunks = find_relevant_chunks(chunks, request.question)
        
        # Prepare context for AI
        context = "\n\n".join(relevant_chunks)
        
        # Create the prompt
        prompt = f"""You are an AI tutor for students on the LearnSphere platform.

The student has uploaded a document. You are given the most relevant sections from that document (retrieved via embeddings search). 
Use ONLY the provided context to answer the student's question. 
If the answer is not present in the context, politely say that you cannot find it in the uploaded material.

---
📄 Context from uploaded file:
{context}

❓ Student's Question:
{request.question}

💡 Instructions:
- Answer step by step, in simple language.
- Highlight formulas, definitions, or examples.
- If multiple sections are relevant, summarize them clearly.
- Be encouraging and supportive in your tone.
- If you cannot find the answer in the context, suggest what the student might look for or ask instead.

Answer:"""

        # Call OpenAI API (updated for openai>=1.0.0)
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor that answers questions based on uploaded documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Calculate cost (approximate for gpt-3.5-turbo)
        cost_per_token = 0.000002  # $0.002 per 1K tokens
        cost_usd = tokens_used * cost_per_token
        
        # Log the interaction
        interaction_record = {
            'user_id': request.user_id,
            'document_id': request.file_id,
            'question': request.question,
            'answer': answer,
            'tokens_used': tokens_used,
            'cost_usd': cost_usd,
            'context_chunks_used': len(relevant_chunks),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        supabase.table('ai_tutor_interactions').insert(interaction_record).execute()
        
        # Log AI usage for admin tracking
        ai_usage_record = {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'tokens_used': tokens_used,
            'cost_usd': cost_usd,
            'request_type': 'ai_tutoring',
            'user_id': request.user_id,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        supabase.table('ai_usage_logs').insert(ai_usage_record).execute()
        
        return AnswerResponse(
            answer=answer,
            context_chunks=relevant_chunks,
            tokens_used=tokens_used,
            cost_usd=cost_usd
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Question answering error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@router.get("/documents/{user_id}")
async def get_user_documents(user_id: str):
    """Get all documents uploaded by a user"""
    try:
        response = supabase.table('ai_tutor_documents').select('id, filename, file_size, chunk_count, created_at').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        return {
            "success": True,
            "documents": response.data or []
        }
    
    except Exception as e:
        print(f"Get documents error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")

@router.delete("/documents/{file_id}")
async def delete_document(file_id: str, user_id: str):
    """Delete a document and its interactions"""
    try:
        # Verify user owns the document
        doc_response = supabase.table('ai_tutor_documents').select('user_id').eq('id', file_id).single().execute()
        
        if not doc_response.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc_response.data['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete interactions first
        supabase.table('ai_tutor_interactions').delete().eq('document_id', file_id).execute()
        
        # Delete document
        supabase.table('ai_tutor_documents').delete().eq('id', file_id).execute()
        
        return {"success": True, "message": "Document deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

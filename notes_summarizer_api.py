from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import pdfplumber
import PyPDF2

from summarizer_service import NotesSummarizerService
from auth_middleware import get_current_user


router = APIRouter(prefix="/api/notes", tags=["notes"])


class SummaryResponse(BaseModel):
    success: bool
    message: str
    summary: Optional[str] = None


async def _extract_text_with_pdfplumber(upload: UploadFile) -> str:
    try:
        # pdfplumber requires a file-like object; read into bytes and reopen
        content = await upload.read()
        from io import BytesIO

        text_accumulator: list[str] = []
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_accumulator.append(page_text)
        await upload.seek(0)
        return "\n".join(text_accumulator).strip()
    except Exception:
        # Fall back to PyPDF2 below
        await upload.seek(0)
        return ""


async def _extract_text_with_pypdf2(upload: UploadFile) -> str:
    try:
        content = await upload.read()
        from io import BytesIO

        reader = PyPDF2.PdfReader(BytesIO(content))
        text_chunks: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text:
                text_chunks.append(text)
        await upload.seek(0)
        return "\n".join(text_chunks).strip()
    except Exception:
        await upload.seek(0)
        return ""


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_notes(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Endpoint: Summarize Uploaded Notes (PDF)
    --------------------------------------------------------
    1. Accepts a student-uploaded PDF file (notes, textbooks, or references).
    2. Extracts raw text content using `pdfplumber` first, falls back to `PyPDF2`.
    3. Validates that the extracted text is non-empty and meaningful.
    4. Passes the extracted text into the Summarization Service with an
       academic-friendly prompt that ensures:
         - Output ~900 words (flexible ±200 words).
         - Simplified explanations for complex terms.
         - Covers all major sections, headings, examples, and definitions.
         - Student-friendly formatting (clear, structured, easy to revise).
         - Logical flow: introduction → key points → examples → conclusion.
    5. Returns a JSON response with success flag, message, and the generated summary.
    """

    try:
        # Validate file presence
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded.")

        # Validate file type
        if not (file.content_type and file.content_type.lower() == "application/pdf"):
            return SummaryResponse(success=False, message="Only PDF files are supported.")

        # Extract text from PDF
        text = await _extract_text_with_pdfplumber(file)
        if not text:
            text = await _extract_text_with_pypdf2(file)

        if not text or len(text.strip()) == 0:
            return SummaryResponse(
                success=False,
                message="Couldn't extract any text from the PDF. Please upload clearer notes."
            )

        # Summarize with enhanced academic-friendly prompt
        summarizer = NotesSummarizerService()
        summary = await summarizer.summarize(
            text,
            prompt=(
                "You are an AI academic summarizer. Your task is to create a detailed, "
                "well-structured, and student-friendly summary of the provided notes. "
                "The summary should be around 900 words (±200), covering all major concepts, "
                "definitions, examples, and explanations in a clear way. Avoid skipping "
                "important points. Simplify jargon, provide context where needed, and ensure "
                "that the flow is logical (introduction → main points → examples → conclusion). "
                "Format output in clear paragraphs and, where useful, include bullet points "
                "for definitions, formulas, or lists."
            )
        )

        if not summary:
            return SummaryResponse(
                success=False,
                message="Summarization service is unavailable or not configured."
            )

        return SummaryResponse(success=True, message="Summary generated successfully.", summary=summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

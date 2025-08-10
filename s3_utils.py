"""
AWS S3 utilities for LearnSphere course materials management.
"""

import os
import boto3
import logging
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile
import uuid
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Manager:
    """Manages AWS S3 operations for course materials."""
    
    def __init__(self):
        """Initialize S3 client with credentials from environment variables."""
        try:
            self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
            self.region = os.getenv('AWS_S3_REGION', 'us-east-1')
            
            if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
                raise ValueError("Missing required AWS credentials in environment variables")
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region
            )
            
            # Test connection
            self._test_connection()
            logger.info(f"S3Manager initialized successfully for bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize S3Manager: {str(e)}")
            raise HTTPException(status_code=500, detail=f"S3 configuration error: {str(e)}")
    
    def _test_connection(self):
        """Test S3 connection and bucket access."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise HTTPException(status_code=500, detail=f"S3 bucket '{self.bucket_name}' not found")
            elif error_code == '403':
                raise HTTPException(status_code=500, detail=f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                raise HTTPException(status_code=500, detail=f"S3 connection error: {str(e)}")
    
    def _generate_file_key(self, course_id: str, original_filename: str, file_type: str = "materials") -> str:
        """Generate a unique S3 key for the file."""
        # Extract file extension
        file_extension = os.path.splitext(original_filename)[1]
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}_{original_filename}"

        return f"courses/{course_id}/{file_type}/{filename}"

    def _generate_assignment_key(self, course_id: str, original_filename: str) -> str:
        """Generate a unique S3 key for assignment files."""
        return self._generate_file_key(course_id, original_filename, "assignments")

    def _generate_submission_key(self, course_id: str, assignment_id: str, student_id: str, original_filename: str) -> str:
        """Generate a unique S3 key for submission files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}_{original_filename}"

        return f"courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}/{filename}"
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type based on file extension."""
        extension = os.path.splitext(filename)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    async def upload_file(self, file: UploadFile, course_id: str) -> Dict[str, Any]:
        """
        Upload a file to S3 and return file metadata.
        
        Args:
            file: FastAPI UploadFile object
            course_id: ID of the course this material belongs to
            
        Returns:
            Dict containing file metadata including S3 URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Validate file size (max 100MB)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")
            
            # Generate S3 key
            s3_key = self._generate_file_key(course_id, file.filename, "materials")
            content_type = self._get_content_type(file.filename)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'course_id': course_id,
                    'original_filename': file.filename,
                    'upload_timestamp': datetime.now().isoformat()
                }
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully uploaded file {file.filename} to S3: {s3_key}")
            
            return {
                'file_name': file.filename,
                'file_url': file_url,
                's3_key': s3_key,
                'file_size': file_size,
                'file_type': content_type
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from S3 using its URL.
        
        Args:
            file_url: The S3 URL of the file to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            # Extract S3 key from URL
            s3_key = self._extract_s3_key_from_url(file_url)
            
            # Delete from S3
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            logger.info(f"Successfully deleted file from S3: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_url}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")
    
    def _extract_s3_key_from_url(self, file_url: str) -> str:
        """Extract S3 key from the file URL."""
        try:
            # Parse URL to extract key
            # Expected format: https://bucket-name.s3.region.amazonaws.com/key
            if f"{self.bucket_name}.s3.{self.region}.amazonaws.com/" in file_url:
                return file_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[1]
            else:
                raise ValueError("Invalid S3 URL format")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid file URL: {str(e)}")
    
    def generate_presigned_url(self, file_url: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for secure file access.
        
        Args:
            file_url: The S3 URL of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL string
        """
        try:
            s3_key = self._extract_s3_key_from_url(file_url)
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            return presigned_url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {file_url}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")
    
    def list_course_files(self, course_id: str) -> List[Dict[str, Any]]:
        """
        List all files for a specific course.
        
        Args:
            course_id: ID of the course
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            prefix = f"courses/{course_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{obj['Key']}"
                    files.append({
                        'key': obj['Key'],
                        'file_url': file_url,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })

            return files

        except Exception as e:
            logger.error(f"Failed to list files for course {course_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to list course files: {str(e)}")

    async def upload_assignment_file(self, file: UploadFile, course_id: str) -> Dict[str, Any]:
        """
        Upload an assignment file to S3.

        Args:
            file: The uploaded file
            course_id: ID of the course

        Returns:
            Dict containing file metadata including S3 URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Read file content
            file_content = await file.read()
            file_size = len(file_content)

            # Validate file size (max 10MB for assignments)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")

            # Generate S3 key for assignment
            s3_key = self._generate_assignment_key(course_id, file.filename)
            content_type = self._get_content_type(file.filename)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'course_id': course_id,
                    'file_type': 'assignment',
                    'original_filename': file.filename,
                    'upload_timestamp': datetime.now().isoformat()
                }
            )

            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

            logger.info(f"Successfully uploaded assignment file {file.filename} to S3: {s3_key}")

            return {
                'file_name': file.filename,
                'file_url': file_url,
                's3_key': s3_key,
                'file_size': file_size,
                'file_type': content_type
            }

        except Exception as e:
            logger.error(f"Failed to upload assignment file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    async def upload_submission_file(self, file: UploadFile, course_id: str, assignment_id: str, student_id: str) -> Dict[str, Any]:
        """
        Upload a student submission file to S3.

        Args:
            file: The uploaded file
            course_id: ID of the course
            assignment_id: ID of the assignment
            student_id: ID of the student

        Returns:
            Dict containing file metadata including S3 URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Read file content
            file_content = await file.read()
            file_size = len(file_content)

            # Validate file size (max 10MB for submissions)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")

            # Generate S3 key for submission
            s3_key = self._generate_submission_key(course_id, assignment_id, student_id, file.filename)
            content_type = self._get_content_type(file.filename)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'course_id': course_id,
                    'assignment_id': assignment_id,
                    'student_id': student_id,
                    'file_type': 'submission',
                    'original_filename': file.filename,
                    'upload_timestamp': datetime.now().isoformat()
                }
            )

            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"

            logger.info(f"Successfully uploaded submission file {file.filename} to S3: {s3_key}")

            return {
                'file_name': file.filename,
                'file_url': file_url,
                's3_key': s3_key,
                'file_size': file_size,
                'file_type': content_type
            }

        except Exception as e:
            logger.error(f"Failed to upload submission file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


# Global S3 manager instance
s3_manager = None

def get_s3_manager() -> S3Manager:
    """Get or create S3 manager instance."""
    global s3_manager
    if s3_manager is None:
        s3_manager = S3Manager()
    return s3_manager

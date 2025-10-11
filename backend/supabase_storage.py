"""
Supabase Storage utilities for LearnSphere file management.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, UploadFile
import uuid
from datetime import datetime
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseStorageManager:
    """Manages Supabase Storage operations for course materials."""
    
    def __init__(self):
        """Initialize Supabase client with credentials from environment variables."""
        try:
            self.supabase_url = os.getenv('SUPABASE_URL')
            self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not all([self.supabase_url, self.supabase_service_key]):
                raise ValueError("Missing required Supabase credentials in environment variables")
            
            self.supabase: Client = create_client(self.supabase_url, self.supabase_service_key)
            
            # Test connection
            self._test_connection()
            logger.info("SupabaseStorageManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SupabaseStorageManager: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Supabase configuration error: {str(e)}")
    
    def _test_connection(self):
        """Test Supabase connection."""
        try:
            # Try to list buckets to test connection
            response = self.supabase.storage.list_buckets()
            logger.info("Supabase connection test successful")
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Supabase connection error: {str(e)}")
    
    def _ensure_bucket_exists(self, bucket_name: str):
        """Ensure a storage bucket exists, create if it doesn't."""
        try:
            buckets = self.supabase.storage.list_buckets()
            
            # Handle different response formats from Supabase
            if hasattr(buckets, 'data'):
                bucket_list = buckets.data
            elif isinstance(buckets, list):
                bucket_list = buckets
            else:
                bucket_list = buckets
                
            # Extract bucket names safely
            bucket_names = []
            for bucket in bucket_list:
                if isinstance(bucket, dict) and 'name' in bucket:
                    bucket_names.append(bucket['name'])
                elif hasattr(bucket, 'name'):
                    bucket_names.append(bucket.name)
                elif hasattr(bucket, '__str__'):
                    # Handle SyncBucket objects
                    bucket_str = str(bucket)
                    if 'name=' in bucket_str:
                        # Extract name from string representation
                        name_start = bucket_str.find('name=') + 5
                        name_end = bucket_str.find(',', name_start)
                        if name_end == -1:
                            name_end = bucket_str.find(')', name_start)
                        if name_end > name_start:
                            bucket_names.append(bucket_str[name_start:name_end].strip("'"))
                        else:
                            bucket_names.append(bucket_str[name_start:].strip("'"))
            
            logger.info(f"Found buckets: {bucket_names}")
            
            if bucket_name not in bucket_names:
                logger.info(f"Creating bucket: {bucket_name}")
                try:
                    # Create bucket with proper parameters
                    self.supabase.storage.create_bucket(
                        id=bucket_name,
                        options={'public': True}
                    )
                    logger.info(f"Bucket {bucket_name} created successfully")
                except Exception as create_error:
                    logger.warning(f"Bucket creation failed (may already exist): {create_error}")
            else:
                logger.info(f"Bucket {bucket_name} already exists")
                
        except Exception as e:
            logger.error(f"Failed to ensure bucket {bucket_name} exists: {str(e)}")
            # Don't fail the operation if bucket creation fails
            pass
    
    def _generate_file_key(self, course_id: str, original_filename: str, file_type: str = "materials") -> str:
        """Generate a unique file key for storage."""
        # Extract file extension
        file_extension = os.path.splitext(original_filename)[1]
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}_{original_filename}"

        return f"courses/{course_id}/{file_type}/{filename}"

    def _generate_assignment_key(self, course_id: str, original_filename: str) -> str:
        """Generate a unique file key for assignment files."""
        return self._generate_file_key(course_id, original_filename, "assignments")

    def _generate_submission_key(self, course_id: str, assignment_id: str, student_id: str, original_filename: str) -> str:
        """Generate a unique file key for submission files."""
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
    
    async def upload_file(self, file: UploadFile, course_id: str, bucket_name: str = "course-materials") -> Dict[str, Any]:
        """
        Upload a file to Supabase Storage and return file metadata.
        
        Args:
            file: FastAPI UploadFile object
            course_id: ID of the course this material belongs to
            bucket_name: Name of the storage bucket
            
        Returns:
            Dict containing file metadata including public URL
        """
        try:
            # Basic validation
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            # Read file content directly
            file_content = await file.read()
            
            # Check if file is empty
            if not file_content:
                raise HTTPException(status_code=400, detail="File is empty")
            
            file_size = len(file_content)
            
            # Validate file size (max 100MB)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")
            
            # Ensure bucket exists
            self._ensure_bucket_exists(bucket_name)
            
            # Generate file key
            file_key = self._generate_file_key(course_id, file.filename, "materials")
            content_type = self._get_content_type(file.filename)
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(bucket_name).upload(file_key, file_content)
            
            # Check if upload was successful
            if hasattr(response, "status_code") and response.status_code != 200:
                raise HTTPException(status_code=500, detail="Upload failed")
            
            # Get public URL
            file_url = self.supabase.storage.from_(bucket_name).get_public_url(file_key)
            
            # Clean the URL by removing any query parameters that might cause issues
            if '?' in file_url:
                file_url = file_url.split('?')[0]
            
            logger.info(f"Successfully uploaded file {file.filename} to Supabase Storage: {file_key}")
            
            return {
                "file_name": file.filename,
                "file_url": file_url,
                "file_size": file_size,
                "file_type": content_type,
                "storage_path": file_key
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    async def upload_assignment_file(self, file: UploadFile, course_id: str) -> Dict[str, Any]:
        """
        Upload an assignment file to Supabase Storage.

        Args:
            file: The uploaded file
            course_id: ID of the course

        Returns:
            Dict containing file metadata including public URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Read file content directly
            file_content = await file.read()
            
            # Check if file is empty
            if not file_content:
                raise HTTPException(status_code=400, detail="File is empty")
            
            file_size = len(file_content)

            # Validate file size (max 10MB for assignments)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")

            # Ensure bucket exists
            self._ensure_bucket_exists("assignments")

            # Generate file key for assignment
            file_key = self._generate_assignment_key(course_id, file.filename)
            content_type = self._get_content_type(file.filename)

            # Upload to Supabase Storage
            response = self.supabase.storage.from_("assignments").upload(file_key, file_content)
            
            # Check if upload was successful
            if hasattr(response, "status_code") and response.status_code != 200:
                raise HTTPException(status_code=500, detail="Upload failed")
            
            # Get public URL
            file_url = self.supabase.storage.from_("assignments").get_public_url(file_key)
            
            # Clean the URL by removing any query parameters that might cause issues
            if '?' in file_url:
                file_url = file_url.split('?')[0]
            
            logger.info(f"Successfully uploaded assignment file {file.filename} to Supabase Storage: {file_key}")
            
            return {
                "file_name": file.filename,
                "file_url": file_url,
                "file_size": file_size,
                "file_type": content_type,
                "storage_path": file_key
            }

        except Exception as e:
            logger.error(f"Failed to upload assignment file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    async def upload_submission_file(self, file: UploadFile, course_id: str, assignment_id: str, student_id: str) -> Dict[str, Any]:
        """
        Upload a student submission file to Supabase Storage.

        Args:
            file: The uploaded file
            course_id: ID of the course
            assignment_id: ID of the assignment
            student_id: ID of the student

        Returns:
            Dict containing file metadata including public URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Read file content directly
            file_content = await file.read()
            
            # Check if file is empty
            if not file_content:
                raise HTTPException(status_code=400, detail="File is empty")
            
            file_size = len(file_content)

            # Validate file size (max 10MB for submissions)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")

            # Ensure bucket exists
            self._ensure_bucket_exists("assignments")

            # Generate file key for submission
            file_key = self._generate_submission_key(course_id, assignment_id, student_id, file.filename)
            content_type = self._get_content_type(file.filename)

            # Upload to Supabase Storage
            response = self.supabase.storage.from_("assignments").upload(file_key, file_content)
            
            # Check if upload was successful
            if hasattr(response, "status_code") and response.status_code != 200:
                raise HTTPException(status_code=500, detail="Upload failed")
            
            # Get public URL
            file_url = self.supabase.storage.from_("assignments").get_public_url(file_key)
            
            # Clean the URL by removing any query parameters that might cause issues
            if '?' in file_url:
                file_url = file_url.split('?')[0]
            
            logger.info(f"Successfully uploaded submission file {file.filename} to Supabase Storage: {file_key}")
            
            return {
                "file_name": file.filename,
                "file_url": file_url,
                "file_size": file_size,
                "file_type": content_type,
                "storage_path": file_key
            }

        except Exception as e:
            logger.error(f"Failed to upload submission file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    async def upload_course_thumbnail(self, file: UploadFile) -> Dict[str, Any]:
        """
        Upload a course thumbnail to Supabase Storage.

        Args:
            file: The uploaded thumbnail file

        Returns:
            Dict containing file metadata including public URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Read file content directly
            file_content = await file.read()
            
            # Check if file is empty
            if not file_content:
                raise HTTPException(status_code=400, detail="File is empty")
            
            file_size = len(file_content)

            # Validate file size (max 5MB for thumbnails)
            max_size = 5 * 1024 * 1024  # 5MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")

            # Ensure bucket exists
            self._ensure_bucket_exists("course-thumbnails")

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = os.path.splitext(file.filename)[1]
            filename = f"{timestamp}_{unique_id}_thumbnail{file_extension}"

            content_type = self._get_content_type(file.filename)

            # Upload to Supabase Storage
            response = self.supabase.storage.from_("course-thumbnails").upload(filename, file_content)
            
            # Check if upload was successful
            if hasattr(response, "status_code") and response.status_code != 200:
                raise HTTPException(status_code=500, detail="Upload failed")
            
            # Get public URL
            file_url = self.supabase.storage.from_("course-thumbnails").get_public_url(filename)
            
            logger.info(f"Successfully uploaded thumbnail {file.filename} to Supabase Storage: {filename}")
            
            return {
                "file_name": file.filename,
                "file_url": file_url,
                "file_size": file_size,
                "file_type": content_type,
                "storage_path": filename
            }

        except Exception as e:
            logger.error(f"Failed to upload thumbnail {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Thumbnail upload failed: {str(e)}")

    async def upload_profile_picture(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Upload a profile picture to Supabase Storage.

        Args:
            file: The uploaded profile picture file
            user_id: ID of the user

        Returns:
            Dict containing file metadata including public URL
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Read file content directly
            file_content = await file.read()
            
            # Check if file is empty
            if not file_content:
                raise HTTPException(status_code=400, detail="File is empty")
            
            file_size = len(file_content)

            # Validate file size (max 5MB for profile pictures)
            max_size = 5 * 1024 * 1024  # 5MB
            if file_size > max_size:
                raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {max_size // (1024*1024)}MB")

            # Ensure bucket exists
            self._ensure_bucket_exists("profile-pictures")

            # Generate unique filename with user folder
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{user_id}/profile{file_extension}"

            content_type = self._get_content_type(file.filename)

            # Upload to Supabase Storage
            response = self.supabase.storage.from_("profile-pictures").upload(unique_filename, file_content)
            
            # Check if upload was successful
            if hasattr(response, "status_code") and response.status_code != 200:
                raise HTTPException(status_code=500, detail="Upload failed")
            
            # Get public URL
            file_url = self.supabase.storage.from_("profile-pictures").get_public_url(unique_filename)
            
            logger.info(f"Successfully uploaded profile picture {file.filename} to Supabase Storage: {unique_filename}")
            
            return {
                "file_name": file.filename,
                "file_url": file_url,
                "file_size": file_size,
                "file_type": content_type,
                "storage_path": unique_filename
            }

        except Exception as e:
            logger.error(f"Failed to upload profile picture {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Profile picture upload failed: {str(e)}")

    async def upload_teacher_verification_document(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """
        Upload a teacher verification document (image/PDF) to Supabase Storage.

        Args:
            file: The uploaded verification document
            user_id: ID of the teacher (profile id)

        Returns:
            Dict containing file metadata including public URL
        """
        try:
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")

            # Check if file has already been read and reset if needed
            try:
                # Try to read a small amount to check if file pointer is at beginning
                test_content = await file.read(1)
                if test_content:
                    # File was readable, reset to beginning
                    await file.seek(0)
                else:
                    # File is empty or at end, reset to beginning
                    await file.seek(0)
            except:
                # If any error occurs, just reset to beginning
                await file.seek(0)

            file_content = await file.read()
            file_size = len(file_content)

            # Allow up to 15MB for verification docs
            max_size = 15 * 1024 * 1024
            if file_size > max_size:
                raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 15MB")

            # Ensure bucket exists
            bucket_name = "teacher-verifications"
            self._ensure_bucket_exists(bucket_name)

            # Store under user folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = os.path.splitext(file.filename)[1]
            storage_key = f"{user_id}/{timestamp}_{unique_id}{file_extension}"

            content_type = self._get_content_type(file.filename)

            # Upload to Supabase Storage
            response = self.supabase.storage.from_(bucket_name).upload(storage_key, file_content)
            
            # Check if upload was successful
            if hasattr(response, "status_code") and response.status_code != 200:
                raise HTTPException(status_code=500, detail="Upload failed")
            
            # Get public URL
            file_url = self.supabase.storage.from_(bucket_name).get_public_url(storage_key)
            
            logger.info(f"Uploaded teacher verification doc {file.filename} to {bucket_name}:{storage_key}")
            
            return {
                "file_name": file.filename,
                "file_url": file_url,
                "file_size": file_size,
                "file_type": content_type,
                "storage_path": storage_key
            }

        except Exception as e:
            logger.error(f"Failed to upload verification doc {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Verification document upload failed: {str(e)}")

    def delete_file(self, file_url: str, bucket_name: str) -> bool:
        """
        Delete a file from Supabase Storage using its URL.
        
        Args:
            file_url: The public URL of the file to delete
            bucket_name: Name of the storage bucket
            
        Returns:
            True if deletion was successful
        """
        try:
            # Extract file key from URL
            file_key = self._extract_file_key_from_url(file_url, bucket_name)
            
            # Delete from Supabase Storage
            response = self.supabase.storage.from_(bucket_name).remove([file_key])
            
            # Check if delete was successful (newer Supabase client returns different response structure)
            if hasattr(response, 'error') and response.error:
                logger.error(f"Failed to delete file: {response.error}")
                return False
            
            logger.info(f"Successfully deleted file from Supabase Storage: {file_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_url}: {str(e)}")
            return False
    
    def _extract_file_key_from_url(self, file_url: str, bucket_name: str) -> str:
        """Extract file key from the public URL."""
        try:
            # Parse URL to extract key
            # Expected format: https://project.supabase.co/storage/v1/object/public/bucket-name/key
            if f"/storage/v1/object/public/{bucket_name}/" in file_url:
                return file_url.split(f"/storage/v1/object/public/{bucket_name}/")[1]
            else:
                raise ValueError("Invalid Supabase Storage URL format")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid file URL: {str(e)}")
    
    def list_course_files(self, course_id: str, bucket_name: str = "course-materials") -> List[Dict[str, Any]]:
        """
        List all files for a specific course.
        
        Args:
            course_id: ID of the course
            bucket_name: Name of the storage bucket
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            prefix = f"courses/{course_id}/"
            
            response = self.supabase.storage.from_(bucket_name).list(path=prefix)
            
            # Check if list was successful (newer Supabase client returns different response structure)
            if hasattr(response, 'error') and response.error:
                logger.error(f"Failed to list files: {response.error}")
                return []
            
            files = []
            for file_info in response.data:
                if file_info['name'].startswith(prefix):
                    file_url = self.supabase.storage.from_(bucket_name).get_public_url(file_info['name'])
                    files.append({
                        'key': file_info['name'],
                        'file_url': file_url,
                        'size': file_info.get('metadata', {}).get('size', 0),
                        'last_modified': file_info.get('updated_at', '')
                    })

            return files

        except Exception as e:
            logger.error(f"Failed to list files for course {course_id}: {str(e)}")
            return []

    def get_file_download_url(self, file_url: str, bucket_name: str, expiration: int = 3600) -> str:
        """
        Generate a download URL for a file (same as public URL for Supabase).
        
        Args:
            file_url: The public URL of the file
            bucket_name: Name of the storage bucket
            expiration: URL expiration time in seconds (not used for Supabase public URLs)
            
        Returns:
            Download URL string
        """
        # For Supabase Storage, public URLs are already accessible
        # We can return the same URL or generate a signed URL if needed in the future
        return file_url


# Global storage manager instance
storage_manager = None

def get_storage_manager() -> SupabaseStorageManager:
    """Get or create storage manager instance."""
    global storage_manager
    if storage_manager is None:
        storage_manager = SupabaseStorageManager()
    return storage_manager

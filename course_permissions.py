"""
Course permissions and authorization utilities for LearnSphere.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from supabase import create_client, Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

class CoursePermissions:
    """Handles course-related permissions and authorization."""
    
    @staticmethod
    async def verify_course_exists(course_id: str) -> Dict[str, Any]:
        """
        Verify that a course exists and return its details.
        
        Args:
            course_id: UUID of the course
            
        Returns:
            Course details dictionary
            
        Raises:
            HTTPException: If course doesn't exist
        """
        try:
            response = supabase.table("courses").select("*").eq("id", course_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course with ID {course_id} not found"
                )
            
            return response.data[0]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying course existence: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify course existence"
            )
    
    @staticmethod
    async def verify_course_ownership(course_id: str, teacher_id: str) -> bool:
        """
        Verify that a teacher owns a specific course.
        
        Args:
            course_id: UUID of the course
            teacher_id: UUID of the teacher
            
        Returns:
            True if teacher owns the course
            
        Raises:
            HTTPException: If teacher doesn't own the course
        """
        try:
            course = await CoursePermissions.verify_course_exists(course_id)
            
            if course["teacher_id"] != teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access this course"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying course ownership: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify course ownership"
            )
    
    @staticmethod
    async def verify_student_enrollment(course_id: str, student_id: str) -> bool:
        """
        Verify that a student is enrolled in a specific course.
        
        Args:
            course_id: UUID of the course
            student_id: UUID of the student
            
        Returns:
            True if student is enrolled
            
        Raises:
            HTTPException: If student is not enrolled
        """
        try:
            # First verify course exists
            await CoursePermissions.verify_course_exists(course_id)
            
            # Check enrollment
            response = supabase.table("enrollments").select("*").eq("course_id", course_id).eq("student_id", student_id).eq("status", "active").execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not enrolled in this course"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying student enrollment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify course enrollment"
            )
    
    @staticmethod
    async def verify_user_exists(user_id: str) -> Dict[str, Any]:
        """
        Verify that a user exists and return their profile.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User profile dictionary
            
        Raises:
            HTTPException: If user doesn't exist
        """
        try:
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
            
            return response.data[0]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying user existence: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify user existence"
            )
    
    @staticmethod
    async def verify_teacher_role(user_id: str) -> Dict[str, Any]:
        """
        Verify that a user has teacher role.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User profile dictionary
            
        Raises:
            HTTPException: If user is not a teacher
        """
        try:
            user = await CoursePermissions.verify_user_exists(user_id)
            
            if user["role"] != "teacher":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only teachers can perform this action"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying teacher role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify teacher role"
            )
    
    @staticmethod
    async def verify_student_role(user_id: str) -> Dict[str, Any]:
        """
        Verify that a user has student role.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User profile dictionary
            
        Raises:
            HTTPException: If user is not a student
        """
        try:
            user = await CoursePermissions.verify_user_exists(user_id)
            
            if user["role"] != "student":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only students can perform this action"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying student role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify student role"
            )
    
    @staticmethod
    async def verify_material_exists(material_id: str) -> Dict[str, Any]:
        """
        Verify that a course material exists and return its details.
        
        Args:
            material_id: UUID of the material
            
        Returns:
            Material details dictionary
            
        Raises:
            HTTPException: If material doesn't exist
        """
        try:
            response = supabase.table("course_materials").select("*").eq("id", material_id).eq("is_active", True).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course material with ID {material_id} not found"
                )
            
            return response.data[0]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying material existence: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify material existence"
            )
    
    @staticmethod
    async def verify_material_ownership(material_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        Verify that a teacher owns a specific course material.
        
        Args:
            material_id: UUID of the material
            teacher_id: UUID of the teacher
            
        Returns:
            Material details dictionary
            
        Raises:
            HTTPException: If teacher doesn't own the material
        """
        try:
            material = await CoursePermissions.verify_material_exists(material_id)
            
            # Verify course ownership
            await CoursePermissions.verify_course_ownership(material["course_id"], teacher_id)
            
            return material
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying material ownership: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify material ownership"
            )

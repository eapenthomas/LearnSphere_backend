"""
Notification Scheduler Service for LearnSphere
Handles scheduled notifications for deadlines, reminders, and other time-based events
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from supabase import create_client, Client
import schedule
import time
import threading

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class NotificationScheduler:
    """Handles scheduled notification generation and delivery"""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start the notification scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("🔔 Notification Scheduler started")
    
    def stop(self):
        """Stop the notification scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("🔔 Notification Scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        # Schedule recurring tasks
        schedule.every(15).minutes.do(self.check_assignment_deadlines)
        schedule.every(15).minutes.do(self.check_quiz_deadlines)
        schedule.every(1).hour.do(self.check_overdue_assignments)
        schedule.every(1).hour.do(self.check_overdue_quizzes)
        schedule.every(6).hours.do(self.cleanup_expired_notifications)
        
        # Run initial checks
        self.check_assignment_deadlines()
        self.check_quiz_deadlines()
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def check_assignment_deadlines(self):
        """Check for assignment deadlines and create notifications"""
        try:
            # Get assignments due in the next 24 hours
            tomorrow = datetime.utcnow() + timedelta(days=1)
            today = datetime.utcnow()
            
            # Check assignments due soon (24 hours)
            assignments_due_soon = supabase.table("assignments_with_details").select("*").gte("due_date", today.isoformat()).lte("due_date", tomorrow.isoformat()).eq("status", "active").execute()
            
            for assignment in assignments_due_soon.data:
                self._create_assignment_deadline_notifications(assignment, "assignment_due_soon")
            
            # Check assignments due today (within next 12 hours)
            twelve_hours = datetime.utcnow() + timedelta(hours=12)
            assignments_due_today = supabase.table("assignments_with_details").select("*").gte("due_date", today.isoformat()).lte("due_date", twelve_hours.isoformat()).eq("status", "active").execute()
            
            for assignment in assignments_due_today.data:
                self._create_assignment_deadline_notifications(assignment, "assignment_due_today")
            
            print(f"✅ Checked assignment deadlines: {len(assignments_due_soon.data)} due soon, {len(assignments_due_today.data)} due today")
            
        except Exception as e:
            print(f"❌ Error checking assignment deadlines: {e}")
    
    def check_quiz_deadlines(self):
        """Check for quiz deadlines and create notifications"""
        try:
            # Get quizzes due in the next 24 hours
            tomorrow = datetime.utcnow() + timedelta(days=1)
            today = datetime.utcnow()
            
            # Check quizzes due soon (24 hours)
            quizzes_due_soon = supabase.table("quizzes").select("*").gte("end_time", today.isoformat()).lte("end_time", tomorrow.isoformat()).in_("status", ["active", "published"]).execute()
            
            for quiz in quizzes_due_soon.data:
                self._create_quiz_deadline_notifications(quiz, "quiz_due_soon")
            
            # Check quizzes due today (within next 12 hours)
            twelve_hours = datetime.utcnow() + timedelta(hours=12)
            quizzes_due_today = supabase.table("quizzes").select("*").gte("end_time", today.isoformat()).lte("end_time", twelve_hours.isoformat()).in_("status", ["active", "published"]).execute()
            
            for quiz in quizzes_due_today.data:
                self._create_quiz_deadline_notifications(quiz, "quiz_due_today")
            
            print(f"✅ Checked quiz deadlines: {len(quizzes_due_soon.data)} due soon, {len(quizzes_due_today.data)} due today")
            
        except Exception as e:
            print(f"❌ Error checking quiz deadlines: {e}")
    
    def check_overdue_assignments(self):
        """Check for overdue assignments and create notifications"""
        try:
            now = datetime.utcnow()
            
            # Get overdue assignments
            overdue_assignments = supabase.table("assignments_with_details").select("*").lt("due_date", now.isoformat()).eq("status", "active").execute()
            
            for assignment in overdue_assignments.data:
                self._create_assignment_deadline_notifications(assignment, "assignment_overdue")
            
            print(f"✅ Checked overdue assignments: {len(overdue_assignments.data)} overdue")
            
        except Exception as e:
            print(f"❌ Error checking overdue assignments: {e}")
    
    def check_overdue_quizzes(self):
        """Check for overdue quizzes and create notifications"""
        try:
            now = datetime.utcnow()
            
            # Get overdue quizzes
            overdue_quizzes = supabase.table("quizzes").select("*").lt("end_time", now.isoformat()).in_("status", ["active", "published"]).execute()
            
            for quiz in overdue_quizzes.data:
                self._create_quiz_deadline_notifications(quiz, "quiz_overdue")
            
            print(f"✅ Checked overdue quizzes: {len(overdue_quizzes.data)} overdue")
            
        except Exception as e:
            print(f"❌ Error checking overdue quizzes: {e}")
    
    def _create_assignment_deadline_notifications(self, assignment: Dict[str, Any], notification_type: str):
        """Create deadline notifications for assignment"""
        try:
            # Get enrolled students
            enrollments = supabase.table("enrollments").select("student_id").eq("course_id", assignment["course_id"]).eq("status", "active").execute()
            
            if not enrollments.data:
                return
            
            student_ids = [enrollment["student_id"] for enrollment in enrollments.data]
            
            # Get course and teacher info
            course_info = supabase.table("courses").select("title, teacher_id").eq("id", assignment["course_id"]).execute()
            teacher_info = supabase.table("profiles").select("full_name").eq("id", assignment["teacher_id"]).execute()
            
            course_title = course_info.data[0]["title"] if course_info.data else "Unknown Course"
            teacher_name = teacher_info.data[0]["full_name"] if teacher_info.data else "Unknown Teacher"
            
            # Create notifications for each student
            for student_id in student_ids:
                # Check if notification already exists
                existing = supabase.table("notifications").select("id").eq("user_id", student_id).eq("type", notification_type).eq("data->assignment_id", assignment["id"]).execute()
                
                if existing.data:
                    continue  # Skip if notification already exists
                
                # Determine priority and message
                priority = "high" if notification_type in ["assignment_due_today", "assignment_overdue"] else "medium"
                
                if notification_type == "assignment_due_soon":
                    message = f"Assignment '{assignment['title']}' in {course_title} is due in 24 hours. Don't forget to submit!"
                elif notification_type == "assignment_due_today":
                    message = f"Assignment '{assignment['title']}' in {course_title} is due today! Please submit soon."
                elif notification_type == "assignment_overdue":
                    message = f"Assignment '{assignment['title']}' in {course_title} is overdue. Please submit as soon as possible."
                
                # Create notification
                supabase.table("notifications").insert({
                    "user_id": student_id,
                    "type": notification_type,
                    "title": f"Assignment {notification_type.replace('_', ' ').title()}",
                    "message": message,
                    "data": {
                        "assignment_id": assignment["id"],
                        "course_id": assignment["course_id"],
                        "teacher_id": assignment["teacher_id"],
                        "due_date": assignment["due_date"],
                        "course_title": course_title,
                        "teacher_name": teacher_name
                    },
                    "priority": priority,
                    "action_url": "/assignments",
                    "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
                }).execute()
                
        except Exception as e:
            print(f"❌ Error creating assignment deadline notifications: {e}")
    
    def _create_quiz_deadline_notifications(self, quiz: Dict[str, Any], notification_type: str):
        """Create deadline notifications for quiz"""
        try:
            # Get enrolled students
            enrollments = supabase.table("enrollments").select("student_id").eq("course_id", quiz["course_id"]).eq("status", "active").execute()
            
            if not enrollments.data:
                return
            
            student_ids = [enrollment["student_id"] for enrollment in enrollments.data]
            
            # Get course and teacher info
            course_info = supabase.table("courses").select("title, teacher_id").eq("id", quiz["course_id"]).execute()
            teacher_info = supabase.table("profiles").select("full_name").eq("id", quiz["created_by"]).execute()
            
            course_title = course_info.data[0]["title"] if course_info.data else "Unknown Course"
            teacher_name = teacher_info.data[0]["full_name"] if teacher_info.data else "Unknown Teacher"
            
            # Create notifications for each student
            for student_id in student_ids:
                # Check if notification already exists
                existing = supabase.table("notifications").select("id").eq("user_id", student_id).eq("type", notification_type).eq("data->quiz_id", quiz["id"]).execute()
                
                if existing.data:
                    continue  # Skip if notification already exists
                
                # Determine priority and message
                priority = "high" if notification_type in ["quiz_due_today", "quiz_overdue"] else "medium"
                
                if notification_type == "quiz_due_soon":
                    message = f"Quiz '{quiz['title']}' in {course_title} ends in 24 hours. Make sure to complete it!"
                elif notification_type == "quiz_due_today":
                    message = f"Quiz '{quiz['title']}' in {course_title} ends today! Please complete it soon."
                elif notification_type == "quiz_overdue":
                    message = f"Quiz '{quiz['title']}' in {course_title} has ended. You may have missed it."
                
                # Create notification
                supabase.table("notifications").insert({
                    "user_id": student_id,
                    "type": notification_type,
                    "title": f"Quiz {notification_type.replace('_', ' ').title()}",
                    "message": message,
                    "data": {
                        "quiz_id": quiz["id"],
                        "course_id": quiz["course_id"],
                        "teacher_id": quiz["created_by"],
                        "end_time": quiz["end_time"],
                        "course_title": course_title,
                        "teacher_name": teacher_name
                    },
                    "priority": priority,
                    "action_url": "/student/quizzes",
                    "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
                }).execute()
                
        except Exception as e:
            print(f"❌ Error creating quiz deadline notifications: {e}")
    
    def cleanup_expired_notifications(self):
        """Clean up expired notifications"""
        try:
            result = supabase.table("notifications").delete().not_.is_("expires_at", "null").lt("expires_at", datetime.utcnow().isoformat()).execute()
            
            deleted_count = len(result.data) if result.data else 0
            print(f"🧹 Cleaned up {deleted_count} expired notifications")
            
        except Exception as e:
            print(f"❌ Error cleaning up expired notifications: {e}")
    
    def create_manual_notification(self, user_id: str, type: str, title: str, message: str, data: Dict[str, Any] = None, priority: str = "medium", action_url: str = None):
        """Create a manual notification"""
        try:
            result = supabase.table("notifications").insert({
                "user_id": user_id,
                "type": type,
                "title": title,
                "message": message,
                "data": data,
                "priority": priority,
                "action_url": action_url,
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Error creating manual notification: {e}")
            return None

# Global scheduler instance
notification_scheduler = NotificationScheduler()

# Start the scheduler when the module is imported
if __name__ != "__main__":
    notification_scheduler.start()

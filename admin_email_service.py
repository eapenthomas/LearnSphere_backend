"""
Admin Email Service
Handles email notifications for admin actions like user status changes and teacher approvals
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

async def send_user_status_email(user_id: str, is_active: bool, admin_name: str = "Administrator"):
    """Send email notification when user is enabled/disabled"""
    try:
        # Get user information
        user_response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        
        if not user_response.data:
            print(f"User {user_id} not found for status email")
            return False
        
        user = user_response.data
        
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured, skipping email")
            return False
        
        # Create email content based on status
        if is_active:
            subject = "🎉 Your LearnSphere Account Has Been Activated"
            status_text = "activated"
            status_color = "#10b981"
            message_text = "Your account has been successfully activated and you can now access all LearnSphere features."
            action_text = "Login to Your Account"
            action_url = "http://localhost:3000/login"
        else:
            subject = "⚠️ Your LearnSphere Account Has Been Suspended"
            status_text = "suspended"
            status_color = "#ef4444"
            message_text = "Your account has been temporarily suspended. Please contact support if you believe this is an error."
            action_text = "Contact Support"
            action_url = "mailto:support@learnsphere.com"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">Account Status Update</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">LearnSphere Account Notification</p>
                </div>
                
                <div style="padding: 30px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: #667eea; margin-top: 0;">Dear {user['full_name']},</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid {status_color}; margin: 20px 0;">
                        <h3 style="margin: 0; color: {status_color};">Account {status_text.title()}</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">{message_text}</p>
                    </div>
                    
                    <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #1976d2;">📋 Account Details</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li><strong>Email:</strong> {user['email']}</li>
                            <li><strong>Role:</strong> {user['role'].title()}</li>
                            <li><strong>Status:</strong> {status_text.title()}</li>
                            <li><strong>Updated by:</strong> {admin_name}</li>
                            <li><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{action_url}" style="background: {status_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">{action_text}</a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                        If you have any questions or concerns, please don't hesitate to contact our support team.
                    </p>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
                    <p>Best regards,<br>The LearnSphere Team</p>
                    <p style="margin-top: 20px;">
                        <a href="http://localhost:3000" style="color: #667eea;">LearnSphere</a> | 
                        <a href="mailto:support@learnsphere.com" style="color: #667eea;">Support</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create and send email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = user['email']
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"User status email sent to {user['email']} - Status: {status_text}")
        
        # Log the email notification
        try:
            supabase.table('email_notifications').insert({
                'recipient_id': user_id,
                'subject': subject,
                'content': html_body,
                'type': 'user_status_change',
                'status': 'sent',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as log_error:
            print(f"Failed to log email notification: {log_error}")
        
        return True
        
    except Exception as e:
        print(f"Error sending user status email: {e}")
        return False

async def send_teacher_approval_email(teacher_id: str, approved: bool, admin_name: str = "Administrator"):
    """Send email notification when teacher is approved/rejected"""
    try:
        # Get teacher information
        teacher_response = supabase.table('profiles').select('*').eq('id', teacher_id).single().execute()
        
        if not teacher_response.data:
            print(f"Teacher {teacher_id} not found for approval email")
            return False
        
        teacher = teacher_response.data
        
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured, skipping email")
            return False
        
        # Create email content based on approval status
        if approved:
            subject = "🎉 Welcome to LearnSphere - Teacher Account Approved!"
            status_text = "approved"
            status_color = "#10b981"
            message_text = "Congratulations! Your teacher account has been approved and you can now start creating courses and managing students."
            action_text = "Access Teacher Dashboard"
            action_url = "http://localhost:3000/teacher/dashboard"
            
            additional_info = """
            <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #0369a1;">🚀 Getting Started as a Teacher</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Create your first course</li>
                    <li>Upload course materials and resources</li>
                    <li>Create quizzes and assignments</li>
                    <li>Monitor student progress</li>
                    <li>Engage with students through forums</li>
                </ul>
            </div>
            """
        else:
            subject = "❌ LearnSphere Teacher Application Update"
            status_text = "not approved"
            status_color = "#ef4444"
            message_text = "We regret to inform you that your teacher account application has not been approved at this time."
            action_text = "Contact Support"
            action_url = "mailto:support@learnsphere.com"
            
            additional_info = """
            <div style="background: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #dc2626;">📞 Next Steps</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Contact our support team for more information</li>
                    <li>Review and update your application if needed</li>
                    <li>Reapply when you meet the requirements</li>
                </ul>
            </div>
            """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">Teacher Application Update</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">LearnSphere Teacher Portal</p>
                </div>
                
                <div style="padding: 30px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: #667eea; margin-top: 0;">Dear {teacher['full_name']},</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid {status_color}; margin: 20px 0;">
                        <h3 style="margin: 0; color: {status_color};">Application {status_text.title()}</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">{message_text}</p>
                    </div>
                    
                    {additional_info}
                    
                    <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #1976d2;">📋 Application Details</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li><strong>Name:</strong> {teacher['full_name']}</li>
                            <li><strong>Email:</strong> {teacher['email']}</li>
                            <li><strong>Status:</strong> {status_text.title()}</li>
                            <li><strong>Reviewed by:</strong> {admin_name}</li>
                            <li><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{action_url}" style="background: {status_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">{action_text}</a>
                    </div>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
                    <p>Best regards,<br>The LearnSphere Team</p>
                    <p style="margin-top: 20px;">
                        <a href="http://localhost:3000" style="color: #667eea;">LearnSphere</a> | 
                        <a href="mailto:support@learnsphere.com" style="color: #667eea;">Support</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create and send email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = teacher['email']
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"Teacher approval email sent to {teacher['email']} - Status: {status_text}")
        
        # Log the email notification
        try:
            supabase.table('email_notifications').insert({
                'recipient_id': teacher_id,
                'subject': subject,
                'content': html_body,
                'type': 'teacher_approval',
                'status': 'sent',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as log_error:
            print(f"Failed to log email notification: {log_error}")
        
        return True
        
    except Exception as e:
        print(f"Error sending teacher approval email: {e}")
        return False

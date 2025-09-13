import os
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Email service for sending OTP and other notifications"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "LearnSphere")
        
        # Validate configuration
        if not self.smtp_username or not self.smtp_password:
            print("⚠️ Warning: Email configuration not found. OTP emails will not be sent.")
            print("Please set SMTP_USERNAME and SMTP_PASSWORD in your .env file")
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    def create_otp_email_html(self, otp_code: str, user_name: str = "User") -> str:
        """Create HTML email template for OTP"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - LearnSphere</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .otp-code {{
                    background-color: #f1f5f9;
                    border: 2px dashed #3b82f6;
                    padding: 20px;
                    text-align: center;
                    margin: 30px 0;
                    border-radius: 8px;
                }}
                .otp-number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #1e40af;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background-color: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <h1 style="color: #1f2937; margin: 0;">Password Reset Request</h1>
                </div>
                
                <p>Hello {user_name},</p>
                
                <p>We received a request to reset your password for your LearnSphere account. Use the verification code below to proceed with resetting your password:</p>
                
                <div class="otp-code">
                    <p style="margin: 0 0 10px 0; font-weight: 600; color: #374151;">Your Verification Code:</p>
                    <div class="otp-number">{otp_code}</div>
                </div>
                
                <p>Enter this code on the password reset page to continue. This code will expire in <strong>10 minutes</strong> for security reasons.</p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong><br>
                    If you didn't request this password reset, please ignore this email. Your account remains secure.
                </div>
                
                <p>If you're having trouble with the password reset process, please contact our support team.</p>
                
                <div class="footer">
                    <p>This is an automated message from LearnSphere.<br>
                    Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_otp_email(self, to_email: str, otp_code: str, user_name: str = "User") -> bool:
        """Send OTP email to user"""
        try:
            if not self.smtp_username or not self.smtp_password:
                print(f"⚠️ Email not sent to {to_email} - SMTP configuration missing")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Password Reset Code: {otp_code} - LearnSphere"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Create HTML content
            html_content = self.create_otp_email_html(otp_code, user_name)
            
            # Create plain text version
            text_content = f"""
Password Reset - LearnSphere

Hello {user_name},

We received a request to reset your password for your LearnSphere account.

Your verification code is: {otp_code}

This code will expire in 10 minutes for security reasons.

If you didn't request this password reset, please ignore this email.

Best regards,
LearnSphere Team
            """.strip()
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ OTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send OTP email to {to_email}: {str(e)}")
            return False

    def send_event_notification(self, to_email: str, event_type: str, event_data: dict) -> bool:
        """Send event-based notifications"""
        try:
            if not self.smtp_username or not self.smtp_password:
                print("⚠️ Email configuration not available")
                return False

            # Create email content based on event type
            subject, html_content = self._create_event_email_content(event_type, event_data)

            if not subject or not html_content:
                print(f"⚠️ Unknown event type: {event_type}")
                return False

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"✅ Event notification sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send event notification: {e}")
            return False

    def _create_event_email_content(self, event_type: str, event_data: dict) -> tuple:
        """Create email content based on event type"""
        base_style = """
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
            .container { background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .logo { font-size: 28px; font-weight: bold; color: #4f46e5; margin-bottom: 10px; }
            .content { margin-bottom: 30px; }
            .button { display: inline-block; padding: 12px 24px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 0; }
            .footer { text-align: center; color: #666; font-size: 14px; margin-top: 30px; }
        </style>
        """

        if event_type == "assignment_submitted":
            subject = f"New Assignment Submission - {event_data.get('assignment_title', 'Assignment')}"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">LearnSphere</div>
                    <h2>New Assignment Submission</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('teacher_name', 'Teacher')},</p>
                    <p>A new assignment has been submitted for your review:</p>
                    <ul>
                        <li><strong>Assignment:</strong> {event_data.get('assignment_title', 'N/A')}</li>
                        <li><strong>Student:</strong> {event_data.get('student_name', 'N/A')}</li>
                        <li><strong>Course:</strong> {event_data.get('course_title', 'N/A')}</li>
                        <li><strong>Submitted:</strong> {event_data.get('submitted_at', 'N/A')}</li>
                    </ul>
                    <p>Please review the submission at your earliest convenience.</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "assignment_graded":
            subject = f"Assignment Graded - {event_data.get('assignment_title', 'Assignment')}"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">LearnSphere</div>
                    <h2>Assignment Graded</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('student_name', 'Student')},</p>
                    <p>Your assignment has been graded:</p>
                    <ul>
                        <li><strong>Assignment:</strong> {event_data.get('assignment_title', 'N/A')}</li>
                        <li><strong>Course:</strong> {event_data.get('course_title', 'N/A')}</li>
                        <li><strong>Grade:</strong> {event_data.get('grade', 'N/A')}</li>
                        <li><strong>Feedback:</strong> {event_data.get('feedback', 'No feedback provided')}</li>
                    </ul>
                    <p>Keep up the great work!</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "course_enrolled":
            subject = f"Welcome to {event_data.get('course_title', 'Course')}"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">LearnSphere</div>
                    <h2>Course Enrollment Confirmation</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('student_name', 'Student')},</p>
                    <p>Congratulations! You have successfully enrolled in:</p>
                    <ul>
                        <li><strong>Course:</strong> {event_data.get('course_title', 'N/A')}</li>
                        <li><strong>Instructor:</strong> {event_data.get('teacher_name', 'N/A')}</li>
                        <li><strong>Enrolled:</strong> {event_data.get('enrolled_at', 'N/A')}</li>
                    </ul>
                    <p>Start your learning journey today!</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "deadline_reminder":
            subject = f"Deadline Reminder - {event_data.get('item_title', 'Assignment/Quiz')}"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">LearnSphere</div>
                    <h2>Deadline Reminder</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('student_name', 'Student')},</p>
                    <p>This is a friendly reminder about an upcoming deadline:</p>
                    <ul>
                        <li><strong>Item:</strong> {event_data.get('item_title', 'N/A')}</li>
                        <li><strong>Type:</strong> {event_data.get('item_type', 'N/A')}</li>
                        <li><strong>Course:</strong> {event_data.get('course_title', 'N/A')}</li>
                        <li><strong>Due Date:</strong> {event_data.get('due_date', 'N/A')}</li>
                    </ul>
                    <p>Don't miss the deadline! Complete your work on time.</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        else:
            return None, None

        return subject, html_content
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.smtp_username and self.smtp_password)

# Global email service instance
email_service = EmailService()

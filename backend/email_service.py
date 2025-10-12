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

        elif event_type == "paid_course_created":
            teacher_name = event_data.get('teacher_name', 'Teacher')
            course_title = event_data.get('course_title', 'Course')
            price = event_data.get('price', 0)
            subject = f"New Paid Course Created 🚀 - {course_title}"
            html_content = f"""
            <html>
            <body style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:white;font-family:'Poppins',sans-serif;text-align:center;padding:40px;">
              <div style="background:rgba(255,255,255,0.1);border-radius:20px;padding:30px;max-width:500px;margin:auto;">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100"/>
                <h2>New Paid Course Created 🚀</h2>
                <p>Hi {teacher_name}, your course <b>{course_title}</b> has been created successfully.</p>
                <p>Students can now purchase access for ₹{price}.</p>
                <p style="font-size:12px;opacity:0.7;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
              </div>
            </body>
            </html>
            """

        elif event_type == "teacher_verification_approved":
            frontend_url = event_data.get('frontend_url', os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app'))
            name = event_data.get('full_name', 'Teacher')
            subject = "🎉 Welcome to LearnSphere Faculty Portal"
            html_content = f"""
            <html>
            <body style="background: linear-gradient(135deg, #141E30, #243B55); color: white; font-family: 'Poppins', sans-serif; text-align: center; padding: 40px;">
              <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; max-width: 500px; margin: auto; box-shadow: 0 0 20px rgba(255,255,255,0.15);">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100" alt="LearnSphere Logo"/>
                <h2 style="margin-top: 20px;">Welcome to LearnSphere Faculty Portal</h2>
                <p style="font-size: 16px;">🎉 Congratulations {name}! Your teacher account has been <b>verified and approved</b>.</p>
                <p>You can now access your Teacher Dashboard and start creating courses.</p>
                <a href="{frontend_url}/teacher/dashboard" style="display:inline-block; margin-top:20px; padding:10px 25px; background:linear-gradient(90deg, #4e54c8, #8f94fb); color:white; text-decoration:none; border-radius:8px;">Access Dashboard</a>
                <p style="margin-top:30px; font-size:12px; opacity:0.8;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
              </div>
            </body>
            </html>
            """

        elif event_type == "teacher_verification_rejected":
            frontend_url = event_data.get('frontend_url', os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app'))
            name = event_data.get('full_name', 'User')
            reason = event_data.get('reason', 'Please contact support for more information.')
            subject = "Teacher Application Update - LearnSphere"
            html_content = f"""
            <html>
            <body style="background: linear-gradient(135deg, #2D1B69, #11998e); color: white; font-family: 'Poppins', sans-serif; text-align: center; padding: 40px; margin: 0;">
              <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; max-width: 500px; margin: auto; box-shadow: 0 0 20px rgba(255,255,255,0.15); backdrop-filter: blur(10px);">
                <div style="margin-bottom: 20px;">
                  <div style="width: 80px; height: 80px; background: linear-gradient(45deg, #ff6b6b, #ee5a52); border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 36px;">⚠️</div>
                  <h1 style="margin: 0; font-size: 24px; color: #f5edd7;">LearnSphere</h1>
                </div>
                <h2 style="margin-top: 20px; color: #ffcccb; font-size: 20px;">Application Update</h2>
                <p style="font-size: 16px; line-height: 1.6; margin: 20px 0;">Dear <strong>{name}</strong>,</p>
                <p style="font-size: 14px; opacity: 0.9; margin: 15px 0;">We regret to inform you that your teacher account application requires additional review.</p>
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 20px 0; border-left: 4px solid #ff6b6b;">
                  <p style="font-size: 13px; margin: 0; opacity: 0.9;"><strong>Reason:</strong> {reason}</p>
                </div>
                <p style="font-size: 13px; opacity: 0.8; margin: 15px 0;">If you have any questions or would like to reapply, please contact our support team.</p>
                <a href="{frontend_url}/contact" style="display:inline-block; margin-top:20px; padding:10px 25px; background:linear-gradient(90deg, #ff6b6b, #ee5a52); color:white; text-decoration:none; border-radius:20px; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);">Contact Support</a>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                  <p style="font-size: 12px; opacity: 0.8; margin: 0;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
                </div>
              </div>
            </body>
            </html>
            """

        elif event_type == "teacher_pending_approval":
            name = event_data.get('full_name', 'Teacher')
            subject = "Teacher Registration Received - Pending Approval"
            html_content = f"""
            <html>
            <body style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-family: 'Poppins', sans-serif; text-align: center; padding: 40px; margin: 0;">
              <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; max-width: 500px; margin: auto; box-shadow: 0 0 20px rgba(255,255,255,0.15); backdrop-filter: blur(10px);">
                <div style="margin-bottom: 20px;">
                  <div style="width: 80px; height: 80px; background: linear-gradient(45deg, #f5edd7, #e8d5b7); border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 36px;">⏳</div>
                  <h1 style="margin: 0; font-size: 24px; color: #f5edd7;">LearnSphere</h1>
                </div>
                <h2 style="margin-top: 20px; color: #f5edd7; font-size: 20px;">Registration Received</h2>
                <p style="font-size: 16px; line-height: 1.6; margin: 20px 0;">Dear <strong>{name}</strong>,</p>
                <p style="font-size: 14px; opacity: 0.9; margin: 15px 0;">Thank you for your teacher registration! Your application has been received and is currently under review.</p>
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin: 20px 0; border-left: 4px solid #f5edd7;">
                  <p style="font-size: 13px; margin: 0; opacity: 0.9;">✅ ID verification passed<br>⏳ Awaiting admin approval</p>
                </div>
                <p style="font-size: 13px; opacity: 0.8; margin: 15px 0;">You will receive an email notification once your account has been reviewed. This typically takes 1-2 business days.</p>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                  <p style="font-size: 12px; opacity: 0.8; margin: 0;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
                </div>
              </div>
            </body>
            </html>
            """

        elif event_type == "teacher_verification_success":
            subject = f"Teacher Auto-Approved - {event_data.get('teacher_name', 'Teacher')}"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <h2 style="color: #10b981;">Teacher Auto-Approved</h2>
                </div>
                <div class="content">
                    <p>Hello Admin,</p>
                    <p>A new teacher has been automatically approved through OCR verification:</p>
                    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>👤 Teacher:</strong> {event_data.get('teacher_name', 'N/A')}</li>
                            <li><strong>🏫 Institution:</strong> {event_data.get('institution_name', 'N/A')}</li>
                            <li><strong>🤖 AI Confidence:</strong> {event_data.get('confidence', 'N/A')}%</li>
                            <li><strong>🆔 User ID:</strong> {event_data.get('user_id', 'N/A')}</li>
                            <li><strong>✅ Status:</strong> Auto-approved (No action required)</li>
                        </ul>
                    </div>
                    <p>The OCR verification passed with high confidence, so the account has been automatically approved and activated.</p>
                    <a href="{event_data.get('admin_dashboard_url', '#')}" class="button" style="background-color: #10b981;">View Dashboard</a>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "teacher_verification_failed":
            subject = "Teacher Verification Failed - Action Required"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <h2 style="color: #dc2626;">Verification Issue Detected</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('teacher_name', 'Teacher')},</p>
                    <p>We were unable to verify your teacher ID card through our automated system.</p>
                    <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #dc2626;"><strong>⚠️ Verification Details:</strong></p>
                        <p style="margin: 10px 0; color: #dc2626; font-weight: 500;">{event_data.get('failure_reason', 'Unable to verify ID card details')}</p>
                        <p style="margin: 5px 0; color: #dc2626; font-size: 14px;">Confidence Score: {event_data.get('confidence', 0)}%</p>
                    </div>
                    <div style="background-color: #f0f9ff; border: 1px solid #bae6fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #0369a1;"><strong>💡 Common Issues & Solutions:</strong></p>
                        <ul style="margin: 10px 0 0 20px; color: #0369a1;">
                            <li>Ensure your name on the ID matches your registration exactly</li>
                            <li>Check that institution name matches (case doesn't matter)</li>
                            <li>Make sure the ID card image is clear and readable</li>
                            <li>Verify the document shows your full name and institution</li>
                        </ul>
                    </div>
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Review your registration details and ID card information</li>
                        <li>Ensure the names and institution match</li>
                        <li>Take a clear, well-lit photo of your ID card</li>
                        <li>Re-upload your verification document</li>
                    </ol>
                    <a href="{event_data.get('reupload_url', '#')}" class="button" style="background-color: #dc2626;">Re-upload ID Card</a>
                </div>
                <div class="footer">
                    <p>If you continue to experience issues, please contact our support team.<br>
                    Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "teacher_verification_success_teacher":
            subject = "Teacher Account Approved - Welcome to LearnSphere!"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <h2 style="color: #10b981;">Welcome to LearnSphere!</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('teacher_name', 'Teacher')},</p>
                    <p>Congratulations! Your teacher ID card has been successfully verified and your account is now active.</p>
                    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #166534;"><strong>✅ Account Details:</strong></p>
                        <ul style="margin: 10px 0 0 20px; color: #166534;">
                            <li>OCR verification passed ({event_data.get('confidence', 'N/A')}% confidence)</li>
                            <li>Account approved and activated</li>
                            <li>Full teacher privileges granted</li>
                        </ul>
                    </div>
                    <p>You can now access your teacher dashboard and start creating courses!</p>
                    <a href="{event_data.get('dashboard_url', '#')}" class="button" style="background-color: #10b981;">Access Teacher Dashboard</a>
                </div>
                <div class="footer">
                    <p>Welcome to the LearnSphere teaching community!<br>
                    Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "teacher_manual_review":
            subject = f"Manual Teacher Verification Request - {event_data.get('teacher_name', 'Teacher')}"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <h2 style="color: #f59e0b;">Manual Verification Required</h2>
                </div>
                <div class="content">
                    <p>Hello Admin,</p>
                    <p>A new teacher has submitted documents for manual verification:</p>
                    <div style="background-color: #fef3c7; border: 1px solid #fcd34d; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>👤 Teacher:</strong> {event_data.get('teacher_name', 'N/A')}</li>
                            <li><strong>🏫 Institution:</strong> {event_data.get('institution_name', 'N/A')}</li>
                            <li><strong>🆔 User ID:</strong> {event_data.get('user_id', 'N/A')}</li>
                            <li><strong>📋 Status:</strong> Manual review required</li>
                        </ul>
                    </div>
                    <p>Please review the verification documents and approve or reject the application.</p>
                    <a href="{event_data.get('admin_dashboard_url', '#')}" class="button" style="background-color: #f59e0b;">Review Documents</a>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The LearnSphere Team</p>
                </div>
            </div>
            </body></html>
            """

        elif event_type == "teacher_manual_review_teacher":
            subject = "Teacher Verification Submitted - Manual Review"
            html_content = f"""
            <!DOCTYPE html><html><head>{base_style}</head><body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <h2 style="color: #f59e0b;">Manual Review Submitted</h2>
                </div>
                <div class="content">
                    <p>Hello {event_data.get('teacher_name', 'Teacher')},</p>
                    <p>You have failed automated verification, so your request has been submitted for manual review by our admin team.</p>
                    <div style="background-color: #fef3c7; border: 1px solid #fcd34d; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #92400e;"><strong>📋 Review Status:</strong></p>
                        <ul style="margin: 10px 0 0 20px; color: #92400e;">
                            <li>Automated verification failed</li>
                            <li>Manual review submitted</li>
                            <li>Admin approval required</li>
                        </ul>
                    </div>
                    <p>You will receive an email notification once your account has been reviewed. This typically takes 1-2 business days.</p>
                    <a href="{event_data.get('dashboard_url', '#')}" class="button" style="background-color: #f59e0b;">View Dashboard</a>
                </div>
                <div class="footer">
                    <p>Thank you for choosing LearnSphere!<br>
                    Best regards,<br>The LearnSphere Team</p>
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

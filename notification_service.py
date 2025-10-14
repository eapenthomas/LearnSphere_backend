"""
Professional Email Notification Service for LearnSphere
Handles teacher approval notifications and user status change notifications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
import json

class NotificationService:
    """Professional email notification service for admin operations"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "LearnSphere Admin Team")
        
        # Validate configuration
        if not self.smtp_username or not self.smtp_password:
            print("⚠️ Warning: Email configuration not found. Notifications will not be sent.")
            print("Please set SMTP_USERNAME and SMTP_PASSWORD in your .env file")
    
    def create_teacher_approval_email(self, teacher_name: str, admin_name: str = "Administrator") -> Dict[str, str]:
        """Create professional teacher approval email"""
        subject = "🎉 Teacher Account Approved - Welcome to LearnSphere!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Teacher Account Approved - LearnSphere</title>
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
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .success-badge {{
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .content {{
                    margin: 30px 0;
                }}
                .highlight {{
                    background-color: #f0f9ff;
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <div class="success-badge">✅ Account Approved</div>
                </div>
                
                <div class="content">
                    <h2 style="color: #1f2937; margin-bottom: 20px;">Congratulations, {teacher_name}!</h2>
                    
                    <p>We are delighted to inform you that your teacher account application has been <strong>approved</strong> by our administrative team.</p>
                    
                    <div class="highlight">
                        <h3 style="margin-top: 0; color: #3b82f6;">🚀 Your Account is Now Active</h3>
                        <p style="margin-bottom: 0;">You can now access all teacher features on the LearnSphere platform, including:</p>
                        <ul style="margin: 10px 0;">
                            <li>Create and manage courses</li>
                            <li>Upload educational content</li>
                            <li>Interact with students</li>
                            <li>Access teacher dashboard</li>
                        </ul>
                    </div>
                    
                    <p>To get started, please log in to your account using your registered credentials.</p>
                    
                    <div style="text-align: center;">
                        <a href="{os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')}/login" class="button">Access Your Account</a>
                    </div>
                    
                    <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                    
                    <p>Welcome to the LearnSphere community!</p>
                </div>
                
                <div class="footer">
                    <p><strong>Approved by:</strong> {admin_name}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e9ecef;">
                    <p>Best regards,<br><strong>LearnSphere Administrative Team</strong></p>
                    <p style="font-size: 12px; color: #9ca3af;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Teacher Account Approved - LearnSphere
        
        Congratulations, {teacher_name}!
        
        We are delighted to inform you that your teacher account application has been approved by our administrative team.
        
        Your Account is Now Active
        
        You can now access all teacher features on the LearnSphere platform, including:
        - Create and manage courses
        - Upload educational content
        - Interact with students
        - Access teacher dashboard
        
        To get started, please log in to your account using your registered credentials at:
        {os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')}/login
        
        If you have any questions or need assistance, please don't hesitate to contact our support team.
        
        Welcome to the LearnSphere community!
        
        Approved by: {admin_name}
        Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Best regards,
        LearnSphere Administrative Team
        
        This is an automated message. Please do not reply to this email.
        """
        
        return {
            "subject": subject,
            "html": html_content,
            "text": text_content
        }
    
    def create_teacher_rejection_email(self, teacher_name: str, reason: str, admin_name: str = "Administrator") -> Dict[str, str]:
        """Create professional teacher rejection email"""
        subject = "Teacher Account Application Update - LearnSphere"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Teacher Account Application Update - LearnSphere</title>
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
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .status-badge {{
                    background: linear-gradient(135deg, #f59e0b, #d97706);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .content {{
                    margin: 30px 0;
                }}
                .reason-box {{
                    background-color: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <div class="status-badge">📋 Application Update</div>
                </div>
                
                <div class="content">
                    <h2 style="color: #1f2937; margin-bottom: 20px;">Dear {teacher_name},</h2>
                    
                    <p>Thank you for your interest in joining LearnSphere as a teacher. We have carefully reviewed your application.</p>
                    
                    <p>We regret to inform you that we are unable to approve your teacher account application at this time.</p>
                    
                    <div class="reason-box">
                        <h3 style="margin-top: 0; color: #92400e;">📝 Reason for Decision:</h3>
                        <p style="margin-bottom: 0; font-style: italic;">"{reason}"</p>
                    </div>
                    
                    <p>We encourage you to address the concerns mentioned above and consider reapplying in the future. Our team is committed to maintaining high standards to ensure the best learning experience for our students.</p>
                    
                    <p>If you have any questions about this decision or would like guidance on how to strengthen a future application, please feel free to contact our support team.</p>
                    
                    <div style="text-align: center;">
                        <a href="mailto:support@learnsphere.com" class="button">Contact Support</a>
                    </div>
                    
                    <p>Thank you for your understanding and continued interest in LearnSphere.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Reviewed by:</strong> {admin_name}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e9ecef;">
                    <p>Best regards,<br><strong>LearnSphere Administrative Team</strong></p>
                    <p style="font-size: 12px; color: #9ca3af;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Teacher Account Application Update - LearnSphere
        
        Dear {teacher_name},
        
        Thank you for your interest in joining LearnSphere as a teacher. We have carefully reviewed your application.
        
        We regret to inform you that we are unable to approve your teacher account application at this time.
        
        Reason for Decision:
        "{reason}"
        
        We encourage you to address the concerns mentioned above and consider reapplying in the future. Our team is committed to maintaining high standards to ensure the best learning experience for our students.
        
        If you have any questions about this decision or would like guidance on how to strengthen a future application, please feel free to contact our support team at support@learnsphere.com.
        
        Thank you for your understanding and continued interest in LearnSphere.
        
        Reviewed by: {admin_name}
        Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Best regards,
        LearnSphere Administrative Team
        
        This is an automated message. Please do not reply to this email.
        """
        
        return {
            "subject": subject,
            "html": html_content,
            "text": text_content
        }

    def create_user_status_change_email(self, user_name: str, is_enabled: bool, admin_name: str = "Administrator") -> Dict[str, str]:
        """Create professional user status change email"""
        action = "Enabled" if is_enabled else "Disabled"
        status_emoji = "✅" if is_enabled else "⚠️"

        subject = f"Account Status Update - {action} - LearnSphere"

        # Create the conditional content for enabled vs disabled
        if is_enabled:
            what_this_means = '''
                    <p><strong>What this means:</strong></p>
                    <ul>
                        <li>You can now access your account normally</li>
                        <li>All platform features are available to you</li>
                        <li>You can log in using your existing credentials</li>
                    </ul>

                    <div style="text-align: center;">
                        <a href="{os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')}/login" class="button">Access Your Account</a>
                    </div>'''

            text_what_means = '''What this means:
        - You can now access your account normally
        - All platform features are available to you
        - You can log in using your existing credentials

        You can access your account at: {os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')}/login'''
        else:
            what_this_means = '''
                    <p><strong>What this means:</strong></p>
                    <ul>
                        <li>You will not be able to access your account</li>
                        <li>All platform features are temporarily unavailable</li>
                        <li>Your data remains secure and unchanged</li>
                    </ul>

                    <p>If you believe this action was taken in error or if you have any questions, please contact our support team immediately.</p>

                    <div style="text-align: center;">
                        <a href="mailto:support@learnsphere.com" class="button">Contact Support</a>
                    </div>'''

            text_what_means = '''What this means:
        - You will not be able to access your account
        - All platform features are temporarily unavailable
        - Your data remains secure and unchanged

        If you believe this action was taken in error or if you have any questions, please contact our support team at support@learnsphere.com.'''

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Status Update - LearnSphere</title>
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
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #3b82f6;
                    margin-bottom: 10px;
                }}
                .status-badge {{
                    background: linear-gradient(135deg, {'#10b981, #059669' if is_enabled else '#ef4444, #dc2626'});
                    color: white;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .content {{
                    margin: 30px 0;
                }}
                .info-box {{
                    background-color: {'#f0f9ff' if is_enabled else '#fef2f2'};
                    border-left: 4px solid {'#3b82f6' if is_enabled else '#ef4444'};
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                    color: white;
                    padding: 14px 28px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎓 LearnSphere</div>
                    <div class="status-badge">{status_emoji} Account {action}</div>
                </div>

                <div class="content">
                    <h2 style="color: #1f2937; margin-bottom: 20px;">Dear {user_name},</h2>

                    <p>We are writing to inform you that your LearnSphere account status has been updated by our administrative team.</p>

                    <div class="info-box">
                        <h3 style="margin-top: 0; color: {'#1e40af' if is_enabled else '#dc2626'};">🔄 Account Status Change</h3>
                        <p style="margin-bottom: 0;">Your account has been <strong>{action.lower()}</strong>.</p>
                    </div>

                    {what_this_means}

                    <p>If you have any questions or concerns about this change, please don't hesitate to reach out to our support team.</p>
                </div>

                <div class="footer">
                    <p><strong>Action taken by:</strong> {admin_name}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e9ecef;">
                    <p>Best regards,<br><strong>LearnSphere Administrative Team</strong></p>
                    <p style="font-size: 12px; color: #9ca3af;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Account Status Update - {action} - LearnSphere

        Dear {user_name},

        We are writing to inform you that your LearnSphere account status has been updated by our administrative team.

        Account Status Change:
        Your account has been {action.lower()}.

        {text_what_means}

        If you have any questions or concerns about this change, please don't hesitate to reach out to our support team.

        Action taken by: {admin_name}
        Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

        Best regards,
        LearnSphere Administrative Team

        This is an automated message. Please do not reply to this email.
        """

        return {
            "subject": subject,
            "html": html_content,
            "text": text_content
        }

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """Send email notification"""
        try:
            if not self.smtp_username or not self.smtp_password:
                print(f"⚠️ Email not sent to {to_email} - SMTP configuration missing")
                print("💡 Please configure SMTP_USERNAME and SMTP_PASSWORD in Render environment variables")
                return False

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Attach parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email with better error handling
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)

                print(f"✅ Email sent successfully to {to_email}: {subject}")
                return True
                
            except (smtplib.SMTPException, OSError, ConnectionError) as smtp_error:
                print(f"❌ SMTP Error sending to {to_email}: {smtp_error}")
                print(f"💡 Tip: For Gmail, use App Password instead of regular password")
                print(f"💡 Tip: Check SMTP settings: {self.smtp_server}:{self.smtp_port}")
                return False

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False

    def send_teacher_approval_notification(self, teacher_email: str, teacher_name: str, admin_name: str = "Administrator") -> bool:
        """Send teacher approval notification"""
        email_data = self.create_teacher_approval_email(teacher_name, admin_name)
        return self.send_email(teacher_email, email_data["subject"], email_data["html"], email_data["text"])

    def send_teacher_rejection_notification(self, teacher_email: str, teacher_name: str, reason: str, admin_name: str = "Administrator") -> bool:
        """Send teacher rejection notification"""
        email_data = self.create_teacher_rejection_email(teacher_name, reason, admin_name)
        return self.send_email(teacher_email, email_data["subject"], email_data["html"], email_data["text"])

    def send_user_status_change_notification(self, user_email: str, user_name: str, is_enabled: bool, admin_name: str = "Administrator") -> bool:
        """Send user status change notification"""
        email_data = self.create_user_status_change_email(user_name, is_enabled, admin_name)
        return self.send_email(user_email, email_data["subject"], email_data["html"], email_data["text"])


# Global instance
notification_service = NotificationService()

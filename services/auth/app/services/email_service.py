"""
Email service for sending verification and notification emails.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for authentication-related emails."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", 1025))  # Default to MailHog
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", "noreply@yourapp.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
    def _send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None):
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server
            if self.smtp_use_tls and self.smtp_port != 1025:  # Don't use TLS for MailHog
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            # Login if credentials provided
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification email."""
        verification_url = f"{self.frontend_url}/auth/verify?token={token}"
        
        subject = "Verify Your Email Address"
        
        plain_body = f"""
Welcome to our platform!

Please verify your email address by clicking the link below or copying the token:

Verification Link: {verification_url}

Token: {token}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The Team
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Verify Your Email</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #007bff; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px;
            margin: 20px 0;
        }}
        .token {{ 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-radius: 4px; 
            font-family: monospace;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to our platform!</h1>
        
        <p>Please verify your email address to complete your registration.</p>
        
        <p>
            <a href="{verification_url}" class="button">Verify Email Address</a>
        </p>
        
        <p>Or copy and paste this token:</p>
        <div class="token">{token}</div>
        
        <p><small>This link will expire in 24 hours.</small></p>
        
        <p><small>If you didn't create an account, please ignore this email.</small></p>
        
        <hr>
        <p><small>Best regards,<br>The Team</small></p>
    </div>
</body>
</html>
        """
        
        return self._send_email(email, subject, plain_body, html_body)
    
    def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{self.frontend_url}/auth/reset-password?token={token}"
        
        subject = "Password Reset Request"
        
        plain_body = f"""
Password Reset Request

We received a request to reset your password. If this was you, click the link below:

Reset Link: {reset_url}

Token: {token}

This link will expire in 15 minutes.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

Best regards,
The Team
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Password Reset Request</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 24px; 
            background-color: #dc3545; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px;
            margin: 20px 0;
        }}
        .token {{ 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-radius: 4px; 
            font-family: monospace;
            word-break: break-all;
        }}
        .warning {{ 
            background-color: #fff3cd; 
            border: 1px solid #ffeaa7; 
            padding: 10px; 
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Password Reset Request</h1>
        
        <p>We received a request to reset your password. If this was you, click the button below:</p>
        
        <p>
            <a href="{reset_url}" class="button">Reset Password</a>
        </p>
        
        <p>Or copy and paste this token:</p>
        <div class="token">{token}</div>
        
        <div class="warning">
            <strong>⚠️ Important:</strong> This link will expire in 15 minutes.
        </div>
        
        <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
        
        <hr>
        <p><small>Best regards,<br>The Team</small></p>
    </div>
</body>
</html>
        """
        
        return self._send_email(email, subject, plain_body, html_body)
    
    def send_welcome_email(self, email: str, name: Optional[str] = None) -> bool:
        """Send welcome email after successful verification."""
        display_name = name or email.split('@')[0]
        
        subject = "Welcome to our platform!"
        
        plain_body = f"""
Welcome {display_name}!

Your email has been successfully verified and your account is now active.

You can now log in and start using our platform.

If you have any questions, feel free to contact our support team.

Best regards,
The Team
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome!</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .success {{ 
            background-color: #d4edda; 
            border: 1px solid #c3e6cb; 
            padding: 15px; 
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome {display_name}! 🎉</h1>
        
        <div class="success">
            <strong>✅ Success!</strong> Your email has been successfully verified and your account is now active.
        </div>
        
        <p>You can now log in and start using our platform.</p>
        
        <p>If you have any questions, feel free to contact our support team.</p>
        
        <hr>
        <p><small>Best regards,<br>The Team</small></p>
    </div>
</body>
</html>
        """
        
        return self._send_email(email, subject, plain_body, html_body)


# Global email service instance
email_service = EmailService()

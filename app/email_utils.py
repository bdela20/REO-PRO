# Save this as: app/email_utils.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_welcome_email(user_email, user_name=None):
    """Send welcome email to new user"""
    
    # Email configuration from environment variables
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USERNAME)
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("Email credentials not configured in environment variables")
        return False
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Welcome to PropInsight Pro!'
    msg['From'] = f"PropInsight Pro <{FROM_EMAIL}>"
    msg['To'] = user_email
    
    # HTML version
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #667eea; margin: 0;">Welcome to PropInsight Pro!</h1>
            </div>
            
            <!-- Greeting -->
            <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {user_name or 'there'},</p>
            
            <p style="font-size: 16px; color: #555; line-height: 1.6; margin-bottom: 30px;">
                Thank you for joining PropInsight Pro! We're excited to have you as part of our community of real estate professionals.
            </p>
            
            <!-- Features -->
            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 30px;">
                <h2 style="color: #667eea; font-size: 20px; margin-top: 0;">Here's what you can do now:</h2>
                <ul style="font-size: 16px; color: #555; line-height: 1.8; margin: 0; padding-left: 20px;">
                    <li>🏠 Search and analyze properties with detailed insights</li>
                    <li>📊 Access market analytics and trends</li>
                    <li>💼 Manage your property portfolio</li>
                    <li>🔍 Get 5 free property searches to start</li>
                </ul>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 35px 0;">
                <a href="http://localhost:5001/dashboard" 
                   style="background-color: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 18px; font-weight: bold;">
                    Go to Dashboard
                </a>
            </div>
            
            <!-- Footer -->
            <hr style="border: 1px solid #eee; margin: 30px 0;">
            
            <div style="text-align: center;">
                <p style="font-size: 14px; color: #999; margin: 10px 0;">
                    Best regards,<br>
                    <strong>The PropInsight Pro Team</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_body = f"""
Welcome to PropInsight Pro!

Hi {user_name or 'there'},

Thank you for joining PropInsight Pro! We're excited to have you as part of our community.

Here's what you can do now:
- Search and analyze properties with detailed insights
- Access market analytics and trends
- Manage your property portfolio
- Get 5 free property searches to start

Get started: http://localhost:5001/dashboard

Best regards,
The PropInsight Pro Team
    """
    
    # Attach parts
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Welcome email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending welcome email to {user_email}: {e}")
        return False
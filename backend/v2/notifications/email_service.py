"""
Email Service - Phase 7

Handles email sending using SendGrid API.
"""

import logging
from typing import List, Dict, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using SendGrid API.
    
    Handles job match notifications, digests, and application updates.
    """
    
    def __init__(self, settings: Settings = None):
        """Initialize SendGrid client."""
        self.settings = settings or get_settings()
        
        if self.settings.sendgrid_api_key:
            self.client = SendGridAPIClient(self.settings.sendgrid_api_key)
            self.from_email = Email(self.settings.sendgrid_from_email, self.settings.sendgrid_from_name)
            logger.info("SendGrid client initialized")
        else:
            self.client = None
            logger.warning("SendGrid API key not configured. Emails will be logged only.")
    
    async def send_job_match_notification(
        self,
        to_email: str,
        user_name: str,
        job_matches: List[Dict[str, Any]]
    ) -> bool:
        """
        Send job match notification email.
        
        Args:
            to_email: Recipient email address
            user_name: User's name
            job_matches: List of matched jobs with details
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Build job list HTML
            job_list_html = ""
            for job in job_matches[:5]:  # Top 5 matches
                match_score = job.get("combined_score", 0) * 100
                job_list_html += f"""
                <div style="margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; background-color: #f9f9f9;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">
                        <a href="{job.get('url', '#')}" style="color: #2196F3; text-decoration: none;">
                            {job.get('title', 'Untitled')}
                        </a>
                    </h3>
                    <p style="margin: 5px 0; color: #666;">
                        <strong>{job.get('company', 'Unknown Company')}</strong> • {job.get('location', 'Remote')}
                    </p>
                    <p style="margin: 5px 0; color: #4CAF50;">
                        <strong>Match: {match_score:.0f}%</strong>
                    </p>
                    {f'<p style="margin: 5px 0; color: #666;">💰 ${job.get("salary_min", 0):,} - ${job.get("salary_max", 0):,}</p>' if job.get('salary_min') else ''}
                </div>
                """
            
            # Email HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #2196F3; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">✨ New Job Matches!</h1>
                </div>
                
                <div style="padding: 30px; background-color: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px;">Hi {user_name},</p>
                    
                    <p>We found <strong>{len(job_matches)} new job{'' if len(job_matches) == 1 else 's'}</strong> that match your resume! 🎯</p>
                    
                    {job_list_html}
                    
                    <div style="margin: 30px 0; text-align: center;">
                        <a href="http://localhost:8001/v2/docs" 
                           style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View All Matches
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 14px; color: #666;">
                        <strong>Tip:</strong> Bookmark jobs you're interested in and track your applications in your AlignCV dashboard.
                    </p>
                    
                    <p style="font-size: 12px; color: #999; margin-top: 30px;">
                        Don't want these notifications? <a href="#" style="color: #2196F3;">Manage your preferences</a>
                    </p>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                    <p>AlignCV - Smart Job Matching Powered by AI</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text fallback
            text_content = f"""
Hi {user_name},

We found {len(job_matches)} new job{'s' if len(job_matches) != 1 else ''} that match your resume!

"""
            for job in job_matches[:5]:
                match_score = job.get("combined_score", 0) * 100
                text_content += f"""
{job.get('title', 'Untitled')} at {job.get('company', 'Unknown')}
Match: {match_score:.0f}% | {job.get('location', 'Remote')}
Apply: {job.get('url', '#')}

"""
            
            text_content += """
View all matches at: http://localhost:8001/v2/docs

---
AlignCV - Smart Job Matching Powered by AI
"""
            
            # Send email
            if self.client:
                message = Mail(
                    from_email=self.from_email,
                    to_emails=To(to_email),
                    subject=f"✨ {len(job_matches)} New Job Match{'es' if len(job_matches) != 1 else ''} for You!",
                    plain_text_content=Content("text/plain", text_content),
                    html_content=Content("text/html", html_content)
                )
                
                response = self.client.send(message)
                logger.info(f"Email sent to {to_email}: Status {response.status_code}")
                return response.status_code in [200, 202]
            else:
                # Log email in development
                logger.info(f"[DEV MODE] Email to {to_email}:\n{text_content}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_digest_email(
        self,
        to_email: str,
        user_name: str,
        digest_type: str,
        summary: Dict[str, Any]
    ) -> bool:
        """
        Send digest email (daily/weekly summary).
        
        Args:
            to_email: Recipient email address
            user_name: User's name
            digest_type: 'daily' or 'weekly'
            summary: Summary statistics
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            new_jobs = summary.get("new_jobs", 0)
            new_matches = summary.get("new_matches", 0)
            applications = summary.get("applications", 0)
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #673AB7; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">📊 Your {digest_type.title()} Digest</h1>
                </div>
                
                <div style="padding: 30px; background-color: white; border: 1px solid #ddd; border-radius: 0 0 10px 10px;">
                    <p>Hi {user_name},</p>
                    
                    <p>Here's your {digest_type} job search summary:</p>
                    
                    <div style="margin: 30px 0;">
                        <div style="display: inline-block; margin: 10px 20px; text-align: center;">
                            <div style="font-size: 36px; font-weight: bold; color: #2196F3;">{new_jobs}</div>
                            <div style="color: #666;">New Jobs</div>
                        </div>
                        <div style="display: inline-block; margin: 10px 20px; text-align: center;">
                            <div style="font-size: 36px; font-weight: bold; color: #4CAF50;">{new_matches}</div>
                            <div style="color: #666;">New Matches</div>
                        </div>
                        <div style="display: inline-block; margin: 10px 20px; text-align: center;">
                            <div style="font-size: 36px; font-weight: bold; color: #FF9800;">{applications}</div>
                            <div style="color: #666;">Applications</div>
                        </div>
                    </div>
                    
                    <div style="margin: 30px 0; text-align: center;">
                        <a href="http://localhost:8001/v2/docs" 
                           style="background-color: #673AB7; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View Dashboard
                        </a>
                    </div>
                    
                    <p style="font-size: 12px; color: #999; margin-top: 30px;">
                        <a href="#" style="color: #2196F3;">Manage notification preferences</a>
                    </p>
                </div>
            </body>
            </html>
            """
            
            if self.client:
                message = Mail(
                    from_email=self.from_email,
                    to_emails=To(to_email),
                    subject=f"📊 Your {digest_type.title()} AlignCV Digest",
                    html_content=Content("text/html", html_content)
                )
                
                response = self.client.send(message)
                logger.info(f"Digest email sent to {to_email}: Status {response.status_code}")
                return response.status_code in [200, 202]
            else:
                logger.info(f"[DEV MODE] Digest email to {to_email}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send digest to {to_email}: {e}")
            return False

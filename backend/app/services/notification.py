import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.user import User

settings = get_settings()


class NotificationService:
    """Service for sending notifications."""

    def __init__(self):
        self.settings = get_settings()

    async def send_notification(
        self,
        user_id: str,
        subject: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a notification to the user."""
        db = SessionLocal()
        try:
            # Get user email from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.settings.EMAIL_USER
            msg["To"] = str(user.email)
            msg["Subject"] = subject

            # Add text content
            msg.attach(MIMEText(message, "plain"))

            # Add HTML content with analysis data if available
            if data:
                html_content = self._create_html_content(data)
                msg.attach(MIMEText(html_content, "html"))

            # Send email
            with smtplib.SMTP(
                self.settings.EMAIL_HOST, self.settings.EMAIL_PORT
            ) as server:
                server.starttls()
                server.login(self.settings.EMAIL_USER, self.settings.EMAIL_PASSWORD)
                server.send_message(msg)

        except Exception as e:
            # Log error but don't raise to prevent blocking the main flow
            print(f"Error sending notification: {str(e)}")
            db.rollback()
        finally:
            db.close()

    def _create_html_content(self, data: Dict[str, Any]) -> str:
        """Create HTML content for the email with analysis data."""
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
                    <tr>
                        <td align="center" style="padding: 20px 0;">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <tr>
                                    <td style="padding: 30px;">
                                        <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">Your Diabetes Analysis Results</h2>
                                        
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px; background-color: #f8f9fa; border-radius: 5px;">
                                            <tr>
                                                <td style="padding: 20px;">
                                                    <h3 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 18px;">Risk Assessment</h3>
                                                    <p style="margin: 0; color: #333333; font-size: 16px; line-height: 1.5;">{risk_assessment}</p>
                                                </td>
                                            </tr>
                                        </table>

                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
                                            <tr>
                                                <td>
                                                    <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">Recommendations</h3>
                                                    {recommendations}
                                                </td>
                                            </tr>
                                        </table>

                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
                                            <tr>
                                                <td>
                                                    <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">Preventive Measures</h3>
                                                    {preventive_measures}
                                                </td>
                                            </tr>
                                        </table>

                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px; background-color: #f8f9fa; border-radius: 5px;">
                                            <tr>
                                                <td style="padding: 20px;">
                                                    <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">Next Steps</h3>
                                                    <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.5;">
                                                        Please log in to your dashboard to view detailed analysis and 
                                                        interactive charts.
                                                    </p>
                                                    <table cellpadding="0" cellspacing="0" border="0">
                                                        <tr>
                                                            <td style="background-color: #4CAF50; border-radius: 5px;">
                                                                <a href="{dashboard_url}" style="display: inline-block; padding: 12px 24px; color: #ffffff; text-decoration: none; font-weight: bold; font-size: 16px;">
                                                                    View Dashboard
                                                                </a>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """

        # Format recommendations
        recommendations_html = ""
        for rec in data.get("recommendations", []):
            recommendations_html += f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 8px;">
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 12px; border-radius: 4px; border-left: 4px solid #4CAF50;">
                            <p style="margin: 0; color: #333333; font-size: 16px; line-height: 1.5;">{rec}</p>
                        </td>
                    </tr>
                </table>
            """

        # Format preventive measures
        preventive_measures_html = ""
        for measure in data.get("preventive_measures", []):
            preventive_measures_html += f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 8px;">
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 12px; border-radius: 4px; border-left: 4px solid #2196F3;">
                            <p style="margin: 0; color: #333333; font-size: 16px; line-height: 1.5;">{measure}</p>
                        </td>
                    </tr>
                </table>
            """

        # Fill in the template
        html = html.format(
            risk_assessment=data.get("risk_assessment", ""),
            recommendations=recommendations_html,
            preventive_measures=preventive_measures_html,
            dashboard_url=data.get("dashboard_url", ""),
        )

        return html

    async def _send_slack(self, message: Dict[str, Any]) -> None:
        """Send notification via Slack."""
        # TODO: Implement Slack integration
        print("Slack notification:", message)

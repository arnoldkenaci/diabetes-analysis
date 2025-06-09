import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.models.diabetes import UserAttempt
from app.services.base import BaseService

settings = get_settings()


class NotificationService(BaseService[UserAttempt]):
    """Service for sending notifications."""

    def __init__(self):
        super().__init__(UserAttempt)
        self.settings = get_settings()

    async def send_notification(
        self,
        user_id: str,
        subject: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a notification to the user."""
        try:
            # Get user email from database
            with self.get_session() as db:
                user = (
                    db.query(UserAttempt).filter(UserAttempt.user_id == user_id).first()
                )
                if not user:
                    raise ValueError(f"User {user_id} not found")

                # Create email message
                msg = MIMEMultipart()
                msg["From"] = self.settings.SMTP_USER
                msg["To"] = user.email
                msg["Subject"] = subject

                # Add text content
                msg.attach(MIMEText(message, "plain"))

                # Add HTML content with analysis data if available
                if data:
                    html_content = self._create_html_content(data)
                    msg.attach(MIMEText(html_content, "html"))

                # Send email
                with smtplib.SMTP(
                    self.settings.SMTP_HOST, self.settings.SMTP_PORT
                ) as server:
                    server.starttls()
                    server.login(self.settings.SMTP_USER, self.settings.SMTP_PASSWORD)
                    server.send_message(msg)

        except Exception as e:
            # Log error but don't raise to prevent blocking the main flow
            print(f"Error sending notification: {str(e)}")

    def _create_html_content(self, data: Dict[str, Any]) -> str:
        """Create HTML content for the email with analysis data."""
        html = """
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .section { margin-bottom: 20px; }
                    .chart { margin: 20px 0; }
                    .recommendation { background-color: #f5f5f5; padding: 10px; margin: 5px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Your Diabetes Analysis Results</h2>
                    
                    <div class="section">
                        <h3>Key Findings</h3>
                        <p>Analyzed {data_points} data points</p>
                    </div>

                    <div class="section">
                        <h3>Risk Factors</h3>
                        {risk_factors}
                    </div>

                    <div class="section">
                        <h3>Recommendations</h3>
                        {recommendations}
                    </div>

                    <div class="section">
                        <h3>Next Steps</h3>
                        <p>Please log in to your dashboard to view detailed analysis and interactive charts.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        # Format risk factors
        risk_factors_html = ""
        for factor in data.get("risk_factors", []):
            risk_factors_html += f"""
            <div class="recommendation">
                <strong>{factor['factor']}</strong>: {factor['value']} (Threshold: {factor['threshold']})
            </div>
            """

        # Format recommendations
        recommendations_html = ""
        for rec in data.get("recommendations", []):
            recommendations_html += f'<div class="recommendation">{rec}</div>'

        # Fill in the template
        html = html.format(
            data_points=data.get("data_points", 0),
            risk_factors=risk_factors_html,
            recommendations=recommendations_html,
        )

        return html

    async def _send_email(self, message: Dict[str, Any]) -> None:
        """Send notification via email."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.settings.EMAIL_USER
            msg["To"] = self.settings.EMAIL_RECIPIENT
            msg["Subject"] = "Diabetes Analysis Alert"

            # Format message body
            body = self._format_email_body(message)
            msg.attach(MIMEText(body, "html"))

            # Connect to SMTP server
            with smtplib.SMTP(
                self.settings.EMAIL_HOST, self.settings.EMAIL_PORT
            ) as server:
                server.starttls()
                server.login(self.settings.EMAIL_USER, self.settings.EMAIL_PASSWORD)
                server.send_message(msg)

            print("Email notification sent successfully")
        except Exception as e:
            print(f"Failed to send email notification: {e}")

    def _format_email_body(self, message: Dict[str, Any]) -> str:
        """Format email body with HTML."""
        timestamp = message.get("timestamp", "")
        notification_type = message.get("type", "")
        priority = message.get("priority", "normal")

        html = f"""
        <html>
            <body>
                <h2>Diabetes Analysis Alert</h2>
                <p>Timestamp: {timestamp}</p>
                <p>Type: {notification_type}</p>
                <p>Priority: {priority}</p>
                
                <div style="
                    padding: 20px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                    margin: 20px 0;
                ">
                    {message.get("message", "")}
                </div>

                <p>
                    <a href="http://localhost:3000/dashboard" style="
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 20px;
                    ">
                        View Dashboard
                    </a>
                </p>
            </body>
        </html>
        """
        return html

    async def _send_slack(self, message: Dict[str, Any]) -> None:
        """Send notification via Slack."""
        # TODO: Implement Slack integration
        print("Slack notification:", message)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from app.core.config import get_settings

settings = get_settings()


class NotificationService:
    """Service for sending notifications."""

    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.EMAIL_USER
        self.sender_password = settings.EMAIL_PASSWORD
        self.recipient_email = settings.EMAIL_RECIPIENT

    async def send_notification(self, message: Dict[str, Any]) -> None:
        """Send notification based on configured channel."""
        if settings.NOTIFICATION_CHANNEL == "email":
            await self._send_email(message)
        elif settings.NOTIFICATION_CHANNEL == "slack":
            await self._send_slack(message)
        else:
            print(f"Unsupported notification channel: {settings.NOTIFICATION_CHANNEL}")

    async def _send_email(self, message: Dict[str, Any]) -> None:
        """Send notification via email."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            msg["Subject"] = "Diabetes Analysis Alert"

            # Format message body
            body = self._format_email_body(message)
            msg.attach(MIMEText(body, "html"))

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print("Email notification sent successfully")
        except Exception as e:
            print(f"Failed to send email notification: {e}")

    def _format_email_body(self, message: Dict[str, Any]) -> str:
        """Format email body with HTML."""
        insights = message.get("insights", {})
        risk_factors = insights.get("risk_factors", {})
        recommendations = message.get("recommendations", [])
        timestamp = message.get("timestamp", "")

        # Create dashboard URL with timestamp
        dashboard_url = f"http://localhost:3000/dashboard?timestamp={timestamp}"

        html = f"""
        <html>
            <body>
                <h2>Diabetes Analysis Alert</h2>
                <p>Timestamp: {timestamp}</p>
                
                <h3>Risk Factors</h3>
                <ul>
                    <li>High Glucose: {'Yes' if risk_factors.get('high_glucose') else 'No'}</li>
                    <li>Obesity: {'Yes' if risk_factors.get('obesity') else 'No'}</li>
                </ul>

                <h3>Age Risk</h3>
                <p>{insights.get('age_risk', 'No significant age risk detected')}</p>

                <h3>BMI Risk</h3>
                <p>{insights.get('bmi_risk', 'No significant BMI risk detected')}</p>

                <h3>Recommendations</h3>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in recommendations)}
                </ul>

                <p>
                    <a href="{dashboard_url}" style="
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 20px;
                    ">
                        View Detailed Analysis
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

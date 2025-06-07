from unittest.mock import MagicMock, patch

import pytest
from app.core.config import get_settings
from app.services.notification import NotificationService

settings = get_settings()


@pytest.mark.asyncio
async def test_email_notification():
    """Test email notification."""
    service = NotificationService()
    message = {
        "insights": {
            "risk_factors": {"high_glucose": True, "obesity": False},
            "age_risk": "Moderate risk for age group",
            "bmi_risk": "Normal BMI range",
        },
        "recommendations": [
            "Monitor glucose levels regularly",
            "Maintain current exercise routine",
        ],
        "timestamp": "2024-02-20T10:00:00",
    }

    with patch("smtplib.SMTP") as mock_smtp:
        # Configure mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test email notification
        await service.send_notification(message)

        # Verify SMTP was called correctly
        mock_smtp.assert_called_once_with(service.smtp_server, service.smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            service.sender_email, service.sender_password
        )
        mock_server.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_slack_notification():
    """Test Slack notification."""
    service = NotificationService()
    message = {
        "insights": {
            "risk_factors": {"high_glucose": True, "obesity": False},
            "age_risk": "Moderate risk for age group",
            "bmi_risk": "Normal BMI range",
        },
        "recommendations": [
            "Monitor glucose levels regularly",
            "Maintain current exercise routine",
        ],
        "timestamp": "2024-02-20T10:00:00",
    }

    # Test Slack notification
    await service.send_notification(message)
    # Currently just prints to console, so no assertions needed


@pytest.mark.asyncio
async def test_notification_error_handling():
    """Test notification error handling."""
    service = NotificationService()
    message = {}  # Empty message to test error handling

    # Test that notifications don't raise exceptions
    await service.send_notification(message)


@pytest.mark.asyncio
async def test_email_formatting():
    """Test email body formatting."""
    service = NotificationService()
    message = {
        "insights": {
            "risk_factors": {"high_glucose": True, "obesity": False},
            "age_risk": "Moderate risk for age group",
            "bmi_risk": "Normal BMI range",
        },
        "recommendations": [
            "Monitor glucose levels regularly",
            "Maintain current exercise routine",
        ],
        "timestamp": "2024-02-20T10:00:00",
    }

    html_body = service._format_email_body(message)

    # Verify HTML content
    assert "<html>" in html_body
    assert "<body>" in html_body
    assert "Diabetes Analysis Alert" in html_body
    assert "Risk Factors" in html_body
    assert "High Glucose: Yes" in html_body
    assert "Obesity: No" in html_body
    assert "Moderate risk for age group" in html_body
    assert "Normal BMI range" in html_body
    assert "Monitor glucose levels regularly" in html_body
    assert "Maintain current exercise routine" in html_body
    assert "View Detailed Analysis" in html_body
    assert "http://localhost:3000/dashboard?timestamp=" in html_body

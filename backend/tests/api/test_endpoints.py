from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "risk_assessment": "Based on the analysis, there are significant risk factors present...",
        "recommendations": [
            "Implement regular health screenings",
            "Focus on lifestyle modifications",
            "Monitor glucose levels closely",
        ],
        "preventive_measures": [
            "Regular exercise program",
            "Balanced diet plan",
            "Stress management techniques",
        ],
    }


def test_get_data(db_session, sample_data):
    """Test getting data endpoint."""
    response = client.get("/api/v1/data")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  # Should return all records
    assert all(isinstance(record["glucose"], int) for record in data)
    assert all(isinstance(record["bmi"], float) for record in data)
    assert all(isinstance(record["age"], int) for record in data)


def test_analyze(db_session, sample_data, mock_llm_response):
    """Test analyze endpoint."""
    with patch("app.services.llm.get_llm_recommendations") as mock_llm:
        mock_llm.return_value = mock_llm_response

        response = client.get("/api/v1/analyze")
        assert response.status_code == 200
        analysis = response.json()

        # Check for expected fields in the new structure
        assert "anomalies" in analysis
        assert "average_age" in analysis
        assert "average_bmi" in analysis
        assert "average_glucose" in analysis

        # Verify anomalies structure
        anomalies = analysis["anomalies"]
        assert "age" in anomalies
        assert "bmi" in anomalies
        assert "glucose" in anomalies

        # Verify averages are numeric
        assert isinstance(analysis["average_age"], (int, float))
        assert isinstance(analysis["average_bmi"], (int, float))
        assert isinstance(analysis["average_glucose"], (int, float))

        # Verify LLM was called with correct parameters
        mock_llm.assert_called_once()
        args = mock_llm.call_args[0]
        assert (
            len(args) == 6
        )  # total_records, positive_cases, positive_rate, avg_glucose, avg_bmi, avg_age
        assert all(isinstance(arg, (int, float)) for arg in args)


def test_insights(db_session, sample_data, mock_llm_response):
    """Test insights endpoint."""
    with patch("app.services.llm.get_llm_recommendations") as mock_llm:
        mock_llm.return_value = mock_llm_response

        response = client.get("/api/v1/insights")
        assert response.status_code == 200
        insights = response.json()

        # Check for expected fields in the new structure
        assert "age_groups" in insights
        assert "bmi_risk" in insights

        # Verify age groups structure
        age_groups = insights["age_groups"]
        assert isinstance(age_groups, list)
        assert len(age_groups) > 0
        assert all("age_range" in group for group in age_groups)
        assert all("count" in group for group in age_groups)
        assert all("diabetes_rate" in group for group in age_groups)

        # Verify BMI risk assessment
        assert isinstance(insights["bmi_risk"], str)

        # Verify LLM was called with correct parameters
        mock_llm.assert_called_once()
        args = mock_llm.call_args[0]
        assert (
            len(args) == 6
        )  # total_records, positive_cases, positive_rate, avg_glucose, avg_bmi, avg_age
        assert all(isinstance(arg, (int, float)) for arg in args)


def test_error_handling():
    """Test error handling in endpoints."""
    # Test invalid endpoint
    response = client.get("/api/v1/invalid")
    assert response.status_code == 404

    # Test invalid method
    response = client.post("/api/v1/data")
    assert response.status_code == 405

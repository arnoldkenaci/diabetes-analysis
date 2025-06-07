from unittest.mock import patch

import pytest
from app.services.analysis import AnalysisService


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


@pytest.mark.asyncio
async def test_get_filtered_data(db_session, sample_data):
    """Test getting filtered data."""
    service = AnalysisService(db=db_session)
    data = await service.get_filtered_data()
    assert len(data) > 0  # Should return all records
    assert all(hasattr(record, "glucose") for record in data)
    assert all(hasattr(record, "bmi") for record in data)
    assert all(hasattr(record, "age") for record in data)


@pytest.mark.asyncio
async def test_run_analysis(db_session, sample_data, mock_llm_response):
    """Test running analysis."""
    with patch("app.services.llm.get_llm_recommendations") as mock_llm:
        mock_llm.return_value = mock_llm_response

        service = AnalysisService(db=db_session)
        analysis = await service.run_analysis()

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


@pytest.mark.asyncio
async def test_anomaly_detection(db_session, sample_data, mock_llm_response):
    """Test anomaly detection."""
    with patch("app.services.llm.get_llm_recommendations") as mock_llm:
        mock_llm.return_value = mock_llm_response

        service = AnalysisService(db=db_session)
        analysis = await service.run_analysis()

        anomalies = analysis["anomalies"]

        # Verify age anomalies
        age_anomalies = anomalies["age"]
        assert isinstance(age_anomalies, list)
        if age_anomalies:  # If there are anomalies
            assert all("deviation" in anomaly for anomaly in age_anomalies)
            assert all("record_id" in anomaly for anomaly in age_anomalies)
            assert all("value" in anomaly for anomaly in age_anomalies)

        # Verify BMI anomalies
        bmi_anomalies = anomalies["bmi"]
        assert isinstance(bmi_anomalies, list)
        if bmi_anomalies:  # If there are anomalies
            assert all("deviation" in anomaly for anomaly in bmi_anomalies)
            assert all("record_id" in anomaly for anomaly in bmi_anomalies)
            assert all("value" in anomaly for anomaly in bmi_anomalies)

        # Verify glucose anomalies
        glucose_anomalies = anomalies["glucose"]
        assert isinstance(glucose_anomalies, list)
        if glucose_anomalies:  # If there are anomalies
            assert all("deviation" in anomaly for anomaly in glucose_anomalies)
            assert all("record_id" in anomaly for anomaly in glucose_anomalies)
            assert all("value" in anomaly for anomaly in glucose_anomalies)


@pytest.mark.asyncio
async def test_average_calculations(db_session, sample_data, mock_llm_response):
    """Test average calculations."""
    with patch("app.services.llm.get_llm_recommendations") as mock_llm:
        mock_llm.return_value = mock_llm_response

        service = AnalysisService(db=db_session)
        analysis = await service.run_analysis()

        # Verify averages are within reasonable ranges
        assert 0 <= analysis["average_age"] <= 100
        assert 10 <= analysis["average_bmi"] <= 50
        assert 50 <= analysis["average_glucose"] <= 300


@pytest.mark.asyncio
async def test_risk_assessment(db_session, sample_data):
    """Test risk assessment."""
    service = AnalysisService(db=db_session)
    analysis = await service.run_analysis()

    risk_assessment = analysis["risk_assessment"]
    assert isinstance(risk_assessment, str)
    assert len(risk_assessment) > 0


@pytest.mark.asyncio
async def test_recommendations(db_session, sample_data):
    """Test recommendations generation."""
    service = AnalysisService(db=db_session)
    analysis = await service.run_analysis()

    recommendations = analysis["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert all(isinstance(rec, str) for rec in recommendations)


@pytest.mark.asyncio
async def test_llm_error_handling(db_session, sample_data):
    """Test LLM error handling."""
    with patch("app.services.llm.get_llm_recommendations") as mock_llm:
        mock_llm.side_effect = Exception("LLM service error")

        service = AnalysisService(db=db_session)
        analysis = await service.run_analysis()

        # Verify analysis still returns basic metrics even if LLM fails
        assert "anomalies" in analysis
        assert "average_age" in analysis
        assert "average_bmi" in analysis
        assert "average_glucose" in analysis

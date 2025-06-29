import logging
import time
from functools import lru_cache
from typing import Any, Dict, Tuple

from app.core.config import get_settings
from huggingface_hub import InferenceClient

settings = get_settings()
logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Hugging Face's models."""

    def __init__(self):
        self.client = InferenceClient(
            provider="nebius", api_key=settings.HUGGINGFACE_API_KEY
        )
        self.rate_limit = 5  # requests per minute
        self.last_request_time = 0

    def _rate_limit(self) -> None:
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < (60 / self.rate_limit):
            time.sleep((60 / self.rate_limit) - time_since_last)
        self.last_request_time = time.time()

    def _make_hashable(self, data: Dict[str, Any]) -> Tuple:
        """Convert dictionary to hashable format for caching."""

        def convert_to_hashable(obj):
            if isinstance(obj, dict):
                return tuple(
                    sorted((k, convert_to_hashable(v)) for k, v in obj.items())
                )
            elif isinstance(obj, list):
                return tuple(convert_to_hashable(item) for item in obj)
            else:
                return obj

        return convert_to_hashable(data)

    @lru_cache(maxsize=100)
    def get_analysis_recommendations(self, data_tuple: Tuple) -> Dict[str, Any]:
        """Generate comprehensive analysis recommendations."""
        self._rate_limit()
        data = dict(data_tuple)

        prompt = (
            "Based on the following diabetes dataset analysis:\n"
            f"- Total Records: {data.get('total_records', 0)}\n"
            f"- Positive Cases: {data.get('positive_cases', 0)}\n"
            f"- Positive Rate: {data.get('positive_rate', 0):.1f}%\n"
            f"- Average Glucose: {data.get('avg_glucose', 0):.1f}\n"
            f"- Average BMI: {data.get('avg_bmi', 0):.1f}\n"
            f"- Average Age: {data.get('avg_age', 0):.1f}\n\n"
            "Please provide a comprehensive analysis in the following format, keeping each section concise and email-friendly:\n\n"
            "1. Risk Assessment:\n"
            "[Provide a clear, concise 2-3 sentence assessment of the overall risk level. "
            "Use simple language and avoid medical jargon. Focus on key concerns that are "
            "easy to understand and actionable.]\n\n"
            "2. Key Recommendations:\n"
            "[Provide 3-5 specific, actionable recommendations. Each recommendation should:\n"
            "- Be clear and concise (1-2 sentences)\n"
            "- Start with an action verb\n"
            "- Be practical and implementable\n"
            "- Focus on lifestyle changes and preventive measures\n"
            "- Avoid complex medical terminology]\n\n"
            "3. Preventive Measures:\n"
            "[Provide 3-5 specific preventive measures. Each measure should:\n"
            "- Be easy to understand and implement\n"
            "- Include specific, measurable actions\n"
            "- Focus on daily habits and routines\n"
            "- Be realistic and achievable\n"
            "- Include timeframes where relevant]\n\n"
            "Important formatting guidelines:\n"
            "- Keep all text concise and easy to read\n"
            "- Use simple, clear language\n"
            "- Avoid medical jargon unless necessary\n"
            "- Make all points actionable and specific\n"
            "- Focus on practical, daily-life changes\n"
            "- Ensure each section is self-contained and clear\n"
            "- Keep recommendations and measures to 1-2 lines each\n"
            "- Use positive, encouraging language\n\n"
            "Focus on evidence-based, actionable insights that can help prevent "
            "or manage diabetes, while keeping the content accessible and easy to understand "
            "for non-medical readers."
        )

        try:
            completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[{"role": "user", "content": prompt}],
            )

            if completion and completion.choices:
                content = completion.choices[0].message.content

                if content is not None:
                    # Parse the response
                    sections = content.split("\n\n")
                else:
                    sections = []  # Handle case where content is None

                risk_assessment = ""
                recommendations = []
                preventive_measures = []

                current_section = None
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue

                    if "Risk Assessment:" in section:
                        current_section = "risk"
                        risk_assessment = (
                            section.replace("Risk Assessment:", "")
                            .replace("1.", "")
                            .strip()
                            .replace("**", "")
                        )
                    elif "Key Recommendations:" in section:
                        current_section = "recommendations"
                        section_content = (
                            section.replace("Key Recommendations:", "")
                            .replace("2.", "")
                            .strip()
                        )
                        # Extract lines that look like recommendations
                        recommendations.extend(
                            [
                                line.strip("- ").strip("* ").strip().replace("**", "")
                                for line in section_content.split("\n")
                                if line.strip().startswith("-")
                                or line.strip().startswith("*")
                            ]
                        )
                    elif "Preventive Measures:" in section:
                        current_section = "measures"
                        section_content = (
                            section.replace("Preventive Measures:", "")
                            .replace("3.", "")
                            .strip()
                        )
                        # Extract lines that look like preventive measures
                        preventive_measures.extend(
                            [
                                line.strip("- ").strip("* ").strip().replace("**", "")
                                for line in section_content.split("\n")
                                if line.strip().startswith("-")
                                or line.strip().startswith("*")
                            ]
                        )
                    elif current_section == "recommendations":
                        # If the section does not start with a new marker,
                        # assume it's part of the current list
                        recommendations.extend(
                            [
                                line.strip("- ").strip("* ").strip().replace("**", "")
                                for line in section.split("\n")
                                if line.strip()
                                and (
                                    line.strip().startswith("-")
                                    or line.strip().startswith("*")
                                    or current_section == "recommendations"
                                )
                            ]
                        )
                    elif current_section == "measures":
                        # If the section does not start with a new marker,
                        # assume it's part of the current list
                        preventive_measures.extend(
                            [
                                line.strip("- ").strip("* ").strip().replace("**", "")
                                for line in section.split("\n")
                                if line.strip()
                                and (
                                    line.strip().startswith("-")
                                    or line.strip().startswith("*")
                                    or current_section == "measures"
                                )
                            ]
                        )

                # Clean up empty strings from the lists
                recommendations = [rec for rec in recommendations if rec]
                preventive_measures = [
                    measure for measure in preventive_measures if measure
                ]

                return {
                    "risk_assessment": risk_assessment,
                    "recommendations": recommendations,
                    "preventive_measures": preventive_measures,
                }

            return {
                "risk_assessment": "Unable to generate risk assessment at this time.",
                "recommendations": [
                    "Consult with healthcare providers for personalized "
                    "recommendationsdd",
                    "Monitor blood glucose levels regularly",
                    "Maintain a healthy lifestyle",
                    "Follow a balanced diet",
                    "Engage in regular physical activity",
                ],
                "preventive_measures": [
                    "Regular health check-ups",
                    "Maintain healthy weight",
                    "Regular exercise",
                    "Balanced diet",
                    "Stress management",
                ],
            }

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "risk_assessment": f"Error generating analysis: {str(e)}",
                "recommendations": ["Please try again later"],
                "preventive_measures": ["Please try again later"],
            }


# Create a singleton instance
llm_service = LLMService()


def get_llm_recommendations(
    total_records: int,
    positive_cases: int,
    positive_rate: float,
    avg_glucose: float,
    avg_bmi: float,
    avg_age: float,
) -> Dict[str, Any]:
    """Get LLM recommendations for the analysis data."""
    data = {
        "total_records": total_records,
        "positive_cases": positive_cases,
        "positive_rate": positive_rate,
        "avg_glucose": avg_glucose,
        "avg_bmi": avg_bmi,
        "avg_age": avg_age,
    }
    return llm_service.get_analysis_recommendations(llm_service._make_hashable(data))

from typing import Dict, Any, List, Tuple
import time
from functools import lru_cache
import logging
from huggingface_hub import InferenceClient
from app.core.config import get_settings

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
    def generate_summary(self, data_tuple: Tuple) -> str:
        """Generate a natural language summary of the analysis."""
        self._rate_limit()

        # Convert tuple back to dict
        data = dict(data_tuple)

        prompt = (
            "Based on the following diabetes analysis data, "
            "provide a concise summary:\n"
            f"Risk Factors:\n"
            f"- High Glucose: {data.get('high_glucose', False)}\n"
            f"- Obesity: {data.get('obesity', False)}\n"
            f"Age Risk: {data.get('age_risk', 'None')}\n"
            f"BMI Risk: {data.get('bmi_risk', 'None')}\n\n"
            "Please provide a 2-3 sentence summary focusing on "
            "the most significant findings."
        )

        try:
            completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[{"role": "user", "content": prompt}],
            )

            if completion and completion.choices:
                return completion.choices[0].message.content
            return "No text generated"

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error generating text: {str(e)}"

    @lru_cache(maxsize=100)
    def generate_recommendations(self, data_tuple: Tuple) -> List[str]:
        """Generate actionable recommendations based on the analysis."""
        self._rate_limit()

        # Convert tuple back to dict
        data = dict(data_tuple)

        prompt = (
            "Based on the following diabetes analysis data, "
            "provide 2-3 specific, actionable recommendations in a structured format:\n"
            f"Risk Factors:\n"
            f"- High Glucose: {data.get('high_glucose', False)}\n"
            f"- Obesity: {data.get('obesity', False)}\n"
            f"Age Risk: {data.get('age_risk', 'None')}\n"
            f"BMI Risk: {data.get('bmi_risk', 'None')}\n\n"
            "Format each recommendation as follows:\n"
            "### [Number]. [Title]\n"
            "[Brief explanation of why this is important]\n"
            "**Actions:**\n"
            "- [Specific action 1]\n"
            "- [Specific action 2]\n"
            "- [Specific action 3]\n\n"
            "Please provide practical, specific recommendations "
            "that can be implemented. Include evidence-based advice "
            "and clear, actionable steps."
        )

        try:
            completion = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3-0324",
                messages=[{"role": "user", "content": prompt}],
            )

            if completion and completion.choices:
                # Get the full response
                content = completion.choices[0].message.content

                # Split into sections based on ### headers
                sections = content.split("###")
                sections = [s.strip() for s in sections if s.strip()]

                # Format each section
                formatted_sections = []
                for section in sections:
                    # Split into title and content
                    lines = section.split("\n", 1)
                    if len(lines) == 2:
                        title, content = lines
                        # Format the section
                        formatted = f"### {title.strip()}\n{content.strip()}"
                        formatted_sections.append(formatted)

                return formatted_sections
            return ["No recommendations generated"]

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return [f"Error generating recommendations: {str(e)}"]

from typing import Dict, Any

class RainPredictionSkill:
    """Skill: Modular procedure for rain prediction analysis."""
    def __init__(self, rain_threshold: float = 0.5):
        self.rain_threshold = rain_threshold

    def check(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        - Call weather API (data provided)
        - Extract rainfall probability
        - Compare with threshold
        """
        # In a real scenario, this would use more complex logic or API calls
        rain_expected = weather_data.get("rain_expected", False)
        # Mocking a probability for the sake of the skill logic
        probability = 0.8 if rain_expected else 0.1

        should_delay = probability >= self.rain_threshold

        return {
            "rain_probability": probability,
            "should_delay_irrigation": should_delay,
            "threshold_used": self.rain_threshold
        }

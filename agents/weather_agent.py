from .base import BaseAgent
from typing import Dict, Any

class WeatherSubagent(BaseAgent):
    """
    Purpose: Understand external conditions.
    Answers: “Will it rain soon?”
    """
    def __init__(self):
        super().__init__("WeatherSubagent")

    def analyze(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        rain_expected = weather_data.get("rain_expected", False)
        temperature = weather_data.get("temperature", 20)
        time_of_day = weather_data.get("time_of_day", 12)

        # High evaporation risk if hot and during the day
        high_evaporation = temperature > 30 and (8 <= time_of_day <= 18)

        return {
            "rain_expected": rain_expected,
            "temperature": temperature,
            "high_evaporation": high_evaporation,
            "can_wait_for_rain": rain_expected and temperature < 35,
            "summary": "Rain expected" if rain_expected else "No rain expected"
        }

import logging
import json
import time
from typing import Dict, Any

class SmartIrrigationAgent:
    """
    Autonomous agent for managing smart irrigation.
    """
    def __init__(self, api_client=None, threshold_dry: int = 40, threshold_extremely_dry: int = 20, threshold_wet: int = 70):
        self.api_client = api_client
        self.threshold_dry = threshold_dry
        self.threshold_extremely_dry = threshold_extremely_dry
        self.threshold_wet = threshold_wet
        self.logger = logging.getLogger(self.__class__.__name__)

    def _analyze_soil(self, moisture: float) -> str:
        if moisture < self.threshold_dry:
            return "dry"
        elif self.threshold_dry <= moisture <= self.threshold_wet:
            return "optimal"
        else:
            return "wet"

    def _is_recent_watering(self, last_watered: str) -> bool:
        """
        Naive parser for last_watered strings like '2 hours ago'.
        """
        if not last_watered:
            return False

        lowered = last_watered.lower()
        if "minute" in lowered:
            return True
        if "hour" in lowered:
            try:
                # Extracts the number from 'X hours ago'
                parts = lowered.split()
                if parts:
                    hours = int(parts[0])
                    return hours < 4 # Consider < 4 hours as recent
            except (ValueError, IndexError):
                pass
        return False

    def decide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decision-making logic based on provided data.
        """
        soil_moisture = data.get("soil_moisture", 50)
        temperature = data.get("temperature", 20)
        rain_expected = data.get("rain_expected", False)
        last_watered = data.get("last_watered", "unknown")

        soil_status = self._analyze_soil(soil_moisture)

        decision = "OFF"
        reason = ""
        confidence = "high"

        if soil_status == "wet":
            decision = "OFF"
            reason = f"Soil is wet ({soil_moisture}% moisture). No watering needed."
        elif soil_status == "optimal":
            decision = "OFF"
            reason = f"Soil moisture ({soil_moisture}%) is at an optimal level."
        elif soil_status == "dry":
            if rain_expected:
                if soil_moisture < self.threshold_extremely_dry:
                    decision = "ON"
                    reason = f"Soil is extremely dry ({soil_moisture}%). Watering is necessary despite expected rain."
                else:
                    decision = "OFF"
                    if self._is_recent_watering(last_watered):
                        reason = "Soil is dry but rain is expected soon and plants were recently watered. Avoiding unnecessary watering."
                    else:
                        reason = "Soil is dry but rain is expected soon. Avoiding unnecessary watering."
            else:
                # No rain expected
                if self._is_recent_watering(last_watered):
                    decision = "OFF"
                    reason = f"Soil is dry but it was recently watered ({last_watered}). Waiting for moisture to soak in."
                else:
                    decision = "ON"
                    reason = "Soil is dry and no rain is expected."
                    if temperature > 30:
                        reason += f" High temperature ({temperature}°C) increases evaporation risk."

        return {
            "decision": decision,
            "reason": reason,
            "confidence": confidence
        }

    def run_once(self) -> Dict[str, Any]:
        """
        Fetches data from APIs, makes a decision, and acts.
        """
        if not self.api_client:
            raise ValueError("API client not configured.")

        try:
            soil_data = self.api_client.get_soil_data()
            weather_data = self.api_client.get_weather()

            # Combine data
            input_data = {**soil_data, **weather_data}

            result = self.decide(input_data)
            self.api_client.post_pump(result["decision"])

            return result
        except Exception as e:
            self.logger.error(f"Error in agent run: {e}")
            return {
                "decision": "OFF",
                "reason": f"Agent error: {str(e)}",
                "confidence": "low"
            }

import logging
import json
import time
import datetime
import os
from typing import Dict, Any, List

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

class SoilAgent(BaseAgent):
    def __init__(self, threshold_dry: int = 40, threshold_extremely_dry: int = 20, threshold_wet: int = 70):
        super().__init__("SoilAgent")
        self.threshold_dry = threshold_dry
        self.threshold_extremely_dry = threshold_extremely_dry
        self.threshold_wet = threshold_wet

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        moisture = data.get("soil_moisture", 50)
        humidity = data.get("humidity", 50)

        status = "optimal"
        if moisture < self.threshold_dry:
            status = "dry"
            if moisture < self.threshold_extremely_dry:
                status = "extremely_dry"
        elif moisture > self.threshold_wet:
            status = "wet"

        return {
            "moisture": moisture,
            "humidity": humidity,
            "status": status,
            "needs_water": status in ["dry", "extremely_dry"]
        }

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("WeatherAgent")

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        rain_expected = data.get("rain_expected", False)
        temperature = data.get("temperature", 20)
        time_of_day = data.get("time_of_day", 12)

        # High evaporation risk if hot and during the day
        high_evaporation = temperature > 30 and (8 <= time_of_day <= 18)

        return {
            "rain_expected": rain_expected,
            "temperature": temperature,
            "high_evaporation": high_evaporation,
            "can_wait_for_rain": rain_expected and temperature < 35
        }

class CoordinationAgent(BaseAgent):
    def __init__(self, api_client=None):
        super().__init__("CoordinationAgent")
        self.api_client = api_client
        self.soil_agent = SoilAgent()
        self.weather_agent = WeatherAgent()
        self.knowledge_base_path = "knowledge_base.json"

    def _is_recent_watering(self, last_watered: str) -> bool:
        if not last_watered:
            return False
        lowered = last_watered.lower()
        if "minute" in lowered:
            return True
        if "hour" in lowered:
            try:
                parts = lowered.split()
                if parts:
                    hours = int(parts[0])
                    return hours < 4
            except (ValueError, IndexError):
                pass
        return False

    def decide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        soil_results = self.soil_agent.analyze(data)
        weather_results = self.weather_agent.analyze(data)
        last_watered = data.get("last_watered", "unknown")

        decision = "OFF"
        reasons = []
        confidence = "high"

        if soil_results["status"] == "wet":
            decision = "OFF"
            reasons.append(f"Soil is wet ({soil_results['moisture']}%).")
        elif soil_results["status"] == "optimal":
            decision = "OFF"
            reasons.append(f"Soil moisture is optimal ({soil_results['moisture']}%).")
        elif soil_results["needs_water"]:
            if weather_results["can_wait_for_rain"] and soil_results["status"] != "extremely_dry":
                decision = "OFF"
                reasons.append("Soil is dry but rain is expected soon. Conserving water.")
            elif self._is_recent_watering(last_watered):
                decision = "OFF"
                reasons.append(f"Soil is dry but it was recently watered ({last_watered}). Waiting for absorption.")
            else:
                decision = "ON"
                reasons.append(f"Soil is {soil_results['status']} and no immediate relief from weather.")
                if weather_results["high_evaporation"]:
                    reasons.append("High evaporation risk detected.")

        return {
            "decision": decision,
            "reason": " ".join(reasons),
            "confidence": confidence,
            "metadata": {
                "soil": soil_results,
                "weather": weather_results,
                "timestamp": time.time()
            }
        }

    def run_once(self) -> Dict[str, Any]:
        if not self.api_client:
            raise ValueError("API client not configured.")

        try:
            soil_data = self.api_client.get_soil_data()
            weather_data = self.api_client.get_weather()
            input_data = {**soil_data, **weather_data}

            # Evaluate previous actions before deciding
            self._evaluate_effectiveness()

            result = self.decide(input_data)
            self.api_client.post_pump(result["decision"])

            self._log_insight(input_data, result)

            return result
        except Exception as e:
            self.logger.error(f"Error in agent run: {e}")
            return {
                "decision": "OFF",
                "reason": f"Agent error: {str(e)}",
                "confidence": "low"
            }

    def _evaluate_effectiveness(self):
        """
        Looks at history to see if previous watering actions were effective.
        """
        if not hasattr(self.api_client, 'get_history'):
            return

        history = self.api_client.get_history()
        if len(history) < 2:
            return

        # Simple check: if last action was PUMP_ON, did moisture increase?
        last_event = history[-1]
        if last_event["action"] == "PUMP_ON":
            current_moisture = self.api_client.get_soil_data()["soil_moisture"]
            prev_moisture = last_event["sensors"]["moisture"]

            improvement = current_moisture - prev_moisture
            self.logger.info(f"Feedback Loop: Last watering improvement: {improvement}% moisture.")

            if improvement <= 0:
                self.logger.warning("Feedback Loop: Watering detected but no moisture improvement. Possible sensor or pump issue.")

    def _log_insight(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """Store insights for future model 'inheritance'."""
        insight = {
            "input": input_data,
            "decision": result["decision"],
            "reason": result["reason"],
            "timestamp": datetime.datetime.now().isoformat()
        }
        try:
            insights = []
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, "r") as f:
                    try:
                        insights = json.load(f)
                    except json.JSONDecodeError:
                        pass

            insights.append(insight)
            # Keep a rolling window of insights
            if len(insights) > 500:
                insights = insights[-500:]

            with open(self.knowledge_base_path, "w") as f:
                json.dump(insights, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to log insight: {e}")

# Maintain backward compatibility for main.py
class SmartIrrigationAgent(CoordinationAgent):
    pass

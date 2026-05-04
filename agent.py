import logging
import json
import time
import datetime
import os
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

class WeatherSubagent(BaseAgent):
    """Purpose: Understand external conditions."""
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

class SoilIntelligenceAgent(BaseAgent):
    """Purpose: Analyze soil behavior over time."""
    def __init__(self, threshold_dry: int = 40, threshold_extremely_dry: int = 20, threshold_wet: int = 70):
        super().__init__("SoilIntelligenceAgent")
        self.threshold_dry = threshold_dry
        self.threshold_extremely_dry = threshold_extremely_dry
        self.threshold_wet = threshold_wet

    def analyze(self, soil_data: Dict[str, Any], history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        moisture = soil_data.get("soil_moisture", 50)

        status = "optimal"
        if moisture < self.threshold_dry:
            status = "dry"
            if moisture < self.threshold_extremely_dry:
                status = "extremely_dry"
        elif moisture > self.threshold_wet:
            status = "wet"

        # Detect drying patterns if history is available
        trend = "stable"
        if history and len(history) >= 2:
            recent_moistures = [h.get("sensors", {}).get("moisture", 50) for h in history[-3:]]
            if len(recent_moistures) >= 2:
                diff = recent_moistures[-1] - recent_moistures[0]
                if diff < -2:
                    trend = "drying_fast"
                elif diff < 0:
                    trend = "drying"
                elif diff > 2:
                    trend = "hydrating_fast"
                elif diff > 0:
                    trend = "hydrating"

        return {
            "moisture": moisture,
            "status": status,
            "trend": trend,
            "needs_water": status in ["dry", "extremely_dry"]
        }

class IrrigationDecisionAgent(BaseAgent):
    """Purpose: Decide watering strategy."""
    def __init__(self):
        super().__init__("IrrigationDecisionAgent")

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

    def decide(self, soil_info: Dict[str, Any], weather_info: Dict[str, Any], last_watered: str) -> Dict[str, Any]:
        decision = "OFF"
        reasons = []
        confidence = "high"

        if soil_info["status"] == "wet":
            decision = "OFF"
            reasons.append(f"Soil is wet ({soil_info['moisture']}%).")
        elif soil_info["status"] == "optimal":
            decision = "OFF"
            reasons.append(f"Soil moisture is optimal ({soil_info['moisture']}%).")
        elif soil_info["needs_water"]:
            if weather_info["can_wait_for_rain"] and soil_info["status"] != "extremely_dry":
                decision = "OFF"
                reasons.append("Soil is dry but rain is expected soon. Conserving water.")
            elif self._is_recent_watering(last_watered):
                decision = "OFF"
                reasons.append(f"Soil is dry but it was recently watered ({last_watered}). Waiting for absorption.")
            else:
                decision = "ON"
                reasons.append(f"Soil is {soil_info['status']} and no immediate relief from weather.")
                if weather_info["high_evaporation"]:
                    reasons.append("High evaporation risk detected due to heat.")
                if soil_info["trend"] == "drying_fast":
                    reasons.append("Soil is drying fast.")

        return {
            "decision": decision,
            "reason": " ".join(reasons),
            "confidence": confidence
        }

class LearningAgent(BaseAgent):
    """Purpose: Improve system over time, build knowledge base."""
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        super().__init__("LearningAgent")
        self.knowledge_base_path = knowledge_base_path

    def learn(self, input_data: Dict[str, Any], result: Dict[str, Any], history: List[Dict[str, Any]]):
        """Compares action vs outcome and stores insights."""
        insight = {
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "decision": result["decision"],
            "reason": result["reason"]
        }

        # Evaluate previous action effectiveness if available
        if history and len(history) >= 1:
            last_event = history[-1]
            if last_event["action"] == "PUMP_ON":
                current_moisture = input_data.get("soil_moisture", 0)
                prev_moisture = last_event.get("sensors", {}).get("moisture", 0)
                improvement = current_moisture - prev_moisture
                insight["effectiveness"] = {
                    "moisture_gain": improvement,
                    "status": "effective" if improvement > 0 else "ineffective"
                }
                if improvement <= 0:
                    self.logger.warning(f"Ineffective watering detected. Gain: {improvement}%")

        self._save_insight(insight)

    def _save_insight(self, insight: Dict[str, Any]):
        try:
            insights = []
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, "r") as f:
                    try:
                        insights = json.load(f)
                    except json.JSONDecodeError:
                        pass

            insights.append(insight)
            if len(insights) > 500:
                insights = insights[-500:]

            with open(self.knowledge_base_path, "w") as f:
                json.dump(insights, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to log insight: {e}")

class DeviceControlAgent(BaseAgent):
    """Purpose: Interface with ESP32 / Mock API."""
    def __init__(self, api_client):
        super().__init__("DeviceControlAgent")
        self.api_client = api_client

    def get_telemetry(self) -> Dict[str, Any]:
        soil_data = self.api_client.get_soil_data()
        weather_data = self.api_client.get_weather()
        history = []
        if hasattr(self.api_client, 'get_history'):
            history = self.api_client.get_history()

        return {
            "soil": soil_data,
            "weather": weather_data,
            "history": history
        }

    def execute_command(self, decision: str):
        if self.api_client:
            self.api_client.post_pump(decision)

class MissionControlAgent(BaseAgent):
    """Main Agent: The Mission Controller. Coordinates subagents."""
    def __init__(self, api_client=None):
        super().__init__("MissionControlAgent")
        self.device_control = DeviceControlAgent(api_client)
        self.weather_subagent = WeatherSubagent()
        self.soil_intelligence = SoilIntelligenceAgent()
        self.decision_subagent = IrrigationDecisionAgent()
        self.learning_agent = LearningAgent()

    def run_once(self) -> Dict[str, Any]:
        try:
            # 1. Receive data from Device (ESP32)
            telemetry = self.device_control.get_telemetry()
            soil_data = telemetry["soil"]
            weather_data = telemetry["weather"]
            history = telemetry["history"]

            # 2. Subagents Analyze
            weather_info = self.weather_subagent.analyze(weather_data)
            soil_info = self.soil_intelligence.analyze(soil_data, history)

            # 3. Decision Subagent decides
            last_watered = soil_data.get("last_watered", "unknown")
            result = self.decision_subagent.decide(soil_info, weather_info, last_watered)

            # 4. Device Control executes
            self.device_control.execute_command(result["decision"])

            # 5. Learning Subagent records outcome
            input_context = {**soil_data, **weather_data}
            self.learning_agent.learn(input_context, result, history)

            # Include metadata for transparency
            result["metadata"] = {
                "soil": soil_info,
                "weather": weather_info,
                "timestamp": time.time()
            }

            return result

        except Exception as e:
            self.logger.error(f"Error in Mission Control: {e}")
            return {
                "decision": "OFF",
                "reason": f"System error: {str(e)}",
                "confidence": "low"
            }

    def decide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Direct decision method for testing and compatibility."""
        weather_info = self.weather_subagent.analyze(data)
        soil_info = self.soil_intelligence.analyze(data)
        last_watered = data.get("last_watered", "unknown")
        return self.decision_subagent.decide(soil_info, weather_info, last_watered)

# Maintain backward compatibility for main.py and test_agent.py
class SmartIrrigationAgent(MissionControlAgent):
    pass

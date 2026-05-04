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

# --- Skills (Reusable Procedures) ---

class Skill:
    def __init__(self, name: str):
        self.name = name

class RainPredictionSkill(Skill):
    """Skill: Call weather logic and compare with threshold."""
    def execute(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        rain_expected = weather_data.get("rain_expected", False)
        temp = weather_data.get("temperature", 20)
        return {
            "will_rain": rain_expected,
            "can_wait": rain_expected and temp < 35
        }

class WateringProcedureSkill(Skill):
    """Skill: Check moisture threshold and define watering duration."""
    def execute(self, soil_data: Dict[str, Any], moisture_threshold: int) -> Dict[str, Any]:
        # Support both 'moisture' and 'soil_moisture' keys
        moisture = soil_data.get("moisture", soil_data.get("soil_moisture", 50))
        if moisture < moisture_threshold:
            duration = 30 if moisture < 20 else 15
            return {"action": "ON", "duration": duration}
        return {"action": "OFF", "duration": 0}

class LearningUpdateSkill(Skill):
    """Skill: Compare before/after moisture and store efficiency."""
    def execute(self, history: List[Dict[str, Any]], current_moisture: int) -> Optional[Dict[str, Any]]:
        if not history:
            return None
        last_event = history[-1]
        if last_event.get("action") == "PUMP_ON":
            prev_moisture = last_event.get("sensors", {}).get("moisture", 0)
            improvement = current_moisture - prev_moisture
            return {
                "gain": improvement,
                "score": 1.0 if improvement > 0 else 0.0
            }
        return None

# --- Specialized Agents ---

class WeatherSubagent(BaseAgent):
    def __init__(self):
        super().__init__("WeatherSubagent")
        self.rain_skill = RainPredictionSkill("RainCheck")

    def analyze(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        prediction = self.rain_skill.execute(weather_data)
        temperature = weather_data.get("temperature", 20)
        time_of_day = weather_data.get("time_of_day", 12)

        high_evaporation = temperature > 30 and (8 <= time_of_day <= 18)

        return {
            "rain_expected": prediction["will_rain"],
            "can_wait_for_rain": prediction["can_wait"],
            "high_evaporation": high_evaporation,
            "temperature": temperature
        }

class SoilIntelligenceAgent(BaseAgent):
    def __init__(self, threshold_dry: int = 40, threshold_extremely_dry: int = 20):
        super().__init__("SoilIntelligenceAgent")
        self.threshold_dry = threshold_dry
        self.threshold_extremely_dry = threshold_extremely_dry

    def analyze(self, soil_data: Dict[str, Any], history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        moisture = soil_data.get("soil_moisture", 50)

        status = "optimal"
        if moisture < self.threshold_dry:
            status = "dry"
            if moisture < self.threshold_extremely_dry:
                status = "extremely_dry"
        elif moisture > 70:
            status = "wet"

        trend = "stable"
        if history and len(history) >= 2:
            recent = [h.get("sensors", {}).get("moisture", 50) for h in history[-3:]]
            diff = recent[-1] - recent[0]
            if diff < -2: trend = "drying_fast"
            elif diff < 0: trend = "drying"
            elif diff > 2: trend = "hydrating_fast"

        return {
            "moisture": moisture,
            "status": status,
            "trend": trend,
            "needs_water": status in ["dry", "extremely_dry"]
        }

class IrrigationDecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("IrrigationDecisionAgent")
        self.watering_skill = WateringProcedureSkill("WateringProc")

    def decide(self, soil_info: Dict[str, Any], weather_info: Dict[str, Any], last_watered: str, knowledge_base: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Inherit intelligence: Check if we have learned that 6am or certain temps are best
        learned_bias = "none"
        if knowledge_base:
            # Simple inheritance: if we have many ineffective waterings in high temp, increase caution
            ineffective = [k for k in knowledge_base[-20:] if k.get("effectiveness", {}).get("status") == "ineffective"]
            if len(ineffective) > 3:
                learned_bias = "high_evaporation_caution"

        procedure = self.watering_skill.execute(soil_info, 40)

        decision = procedure["action"]
        reasons = []

        if soil_info["status"] == "wet":
            decision = "OFF"
            reasons.append("Soil is already wet.")
        elif soil_info["status"] == "optimal":
            decision = "OFF"
            reasons.append("Soil moisture is optimal.")
        elif soil_info["needs_water"]:
            if weather_info["can_wait_for_rain"] and soil_info["status"] != "extremely_dry":
                decision = "OFF"
                reasons.append("Conserving water; rain expected.")
            elif "minute" in last_watered.lower():
                decision = "OFF"
                reasons.append("Recently watered; waiting for absorption.")
            else:
                decision = "ON"
                reasons.append(f"Soil is {soil_info['status']}.")
                if weather_info["high_evaporation"]:
                    reasons.append("High evaporation risk.")
                    if learned_bias == "high_evaporation_caution":
                        reasons.append("Bias: Previous waterings in these conditions were ineffective.")

        return {
            "decision": decision,
            "reason": " ".join(reasons),
            "confidence": "high",
            "duration": procedure["duration"] if decision == "ON" else 0
        }

class LearningAgent(BaseAgent):
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        super().__init__("LearningAgent")
        self.kb_path = knowledge_base_path
        self.update_skill = LearningUpdateSkill("Update")

    def get_knowledge(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r") as f:
                try: return json.load(f)
                except: return []
        return []

    def learn(self, input_data: Dict[str, Any], result: Dict[str, Any], history: List[Dict[str, Any]]):
        efficiency = self.update_skill.execute(history, input_data.get("soil_moisture", 0))

        insight = {
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "decision": result["decision"],
            "reason": result["reason"],
            "effectiveness": {"status": "effective" if efficiency and efficiency["score"] > 0 else "unknown", "gain": efficiency["gain"] if efficiency else 0}
        }

        insights = self.get_knowledge()
        insights.append(insight)
        with open(self.kb_path, "w") as f:
            json.dump(insights[-500:], f, indent=2)

class DeviceControlAgent(BaseAgent):
    def __init__(self, api_client):
        super().__init__("DeviceControlAgent")
        self.api_client = api_client

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "soil": self.api_client.get_soil_data(),
            "weather": self.api_client.get_weather(),
            "history": self.api_client.get_history() if hasattr(self.api_client, 'get_history') else []
        }

    def execute(self, decision: str):
        if self.api_client: self.api_client.post_pump(decision)

class MissionControlAgent(BaseAgent):
    """NASA Mission Control - Coordinates everything."""
    def __init__(self, api_client=None):
        super().__init__("MissionControlAgent")
        self.device = DeviceControlAgent(api_client)
        self.weather = WeatherSubagent()
        self.soil = SoilIntelligenceAgent()
        self.decision = IrrigationDecisionAgent()
        self.learner = LearningAgent()

    def run_once(self) -> Dict[str, Any]:
        telemetry = self.device.get_telemetry()

        # Inherit Intelligence from knowledge base
        kb = self.learner.get_knowledge()

        weather_info = self.weather.analyze(telemetry["weather"])
        soil_info = self.soil.analyze(telemetry["soil"], telemetry["history"])

        result = self.decision.decide(
            soil_info,
            weather_info,
            telemetry["soil"].get("last_watered", "unknown"),
            kb
        )

        self.device.execute(result["decision"])
        self.learner.learn({**telemetry["soil"], **telemetry["weather"]}, result, telemetry["history"])

        result["metadata"] = {"soil": soil_info, "weather": weather_info, "timestamp": time.time()}
        return result

    def decide(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility."""
        w = self.weather.analyze(data)
        s = self.soil.analyze(data)
        return self.decision.decide(s, w, data.get("last_watered", "unknown"))

class SmartIrrigationAgent(MissionControlAgent):
    pass

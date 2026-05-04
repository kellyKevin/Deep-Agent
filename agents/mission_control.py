import time
from typing import Dict, Any

from .base import BaseAgent
from .weather_agent import WeatherSubagent
from .soil_agent import SoilIntelligenceSubagent
from .decision_agent import IrrigationDecisionSubagent
from .learning_agent import LearningSubagent
from .device_agent import DeviceControlSubagent

from skills.watering_skill import WateringProcedureSkill
from skills.rain_check_skill import RainPredictionSkill
from skills.learning_skill import LearningUpdateSkill

class MissionControlAgent(BaseAgent):
    """
    Main Agent: The Mission Controller.
    NASA mission control in Interstellar.
    Receives data from ESP32.
    Decides what needs to happen.
    Delegates tasks to subagents.
    """
    def __init__(self, api_client=None):
        super().__init__("MissionControlAgent")
        # Subagents
        self.device_control = DeviceControlSubagent(api_client)
        self.weather_subagent = WeatherSubagent()
        self.soil_intelligence = SoilIntelligenceSubagent()
        self.decision_subagent = IrrigationDecisionSubagent()
        self.learning_subagent = LearningSubagent()

        # Skills
        self.watering_skill = WateringProcedureSkill(self.device_control)
        self.rain_check_skill = RainPredictionSkill()
        self.learning_skill = LearningUpdateSkill(self.learning_subagent)

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

            # Use Skill for additional weather check
            rain_analysis = self.rain_check_skill.check(weather_data)
            weather_info["rain_probability"] = rain_analysis["rain_probability"]

            # 3. Decision Subagent decides (Inheriting intelligence from past insights)
            insights = self.learning_subagent.get_insights()
            last_watered = soil_data.get("last_watered", "unknown")
            result = self.decision_subagent.decide(soil_info, weather_info, last_watered, insights)

            # 4. Skills/Device Control executes
            if result["decision"] == "ON":
                # Use the Watering Skill for more complex procedure than just ON/OFF
                skill_result = self.watering_skill.execute(duration_seconds=10)
                result["skill_execution"] = skill_result
            else:
                self.device_control.execute_command("OFF")

            # 5. Learning Skill records outcome
            input_context = {**soil_data, **weather_data}
            self.learning_skill.update(input_context, result, history)

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
        # For simple decide, we skip insights inheritance for now to match old tests or simplify
        return self.decision_subagent.decide(soil_info, weather_info, last_watered)

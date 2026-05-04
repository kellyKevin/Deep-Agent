from .base import BaseAgent
from typing import Dict, Any, List

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

    def decide(self, soil_info: Dict[str, Any], weather_info: Dict[str, Any], last_watered: str, insights: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        decision = "OFF"
        reasons = []
        confidence = "high"

        # Intelligence Inheritance: Adjust strategy based on past effectiveness
        strategy_adjustment = ""
        if insights:
            ineffective_count = sum(1 for i in insights[-10:] if i.get("effectiveness", {}).get("status") == "ineffective")
            if ineffective_count > 3:
                strategy_adjustment = " (Adjusted: Increased threshold due to recent ineffectiveness)"
                # In a real scenario, we might dynamicall adjust thresholds here

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
                reasons.append(f"Soil is {soil_info['status']} and no immediate relief from weather.{strategy_adjustment}")
                if weather_info["high_evaporation"]:
                    reasons.append("High evaporation risk detected due to heat.")
                if soil_info["trend"] == "drying_fast":
                    reasons.append("Soil is drying fast.")

        return {
            "decision": decision,
            "reason": " ".join(reasons),
            "confidence": confidence
        }

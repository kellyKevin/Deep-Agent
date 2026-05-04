from .base import BaseAgent
from typing import Dict, Any, List

class IrrigationDecisionSubagent(BaseAgent):
    """
    Purpose: Decide watering strategy.
    Combines: Soil data, Weather prediction.
    Outputs: Water now, Delay, Skip.
    """
    def __init__(self):
        super().__init__("IrrigationDecisionSubagent")
        self.base_threshold_dry = 40

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
        current_threshold = self.base_threshold_dry
        strategy_adjustment = ""
        if insights:
            effective_actions = [i for i in insights if "effectiveness" in i]
            if effective_actions:
                ineffective_count = sum(1 for i in effective_actions[-10:] if i["effectiveness"]["status"] == "ineffective")
                if ineffective_count > 3:
                    # If watering isn't effective, maybe we should water earlier (higher threshold)
                    current_threshold += 5
                    strategy_adjustment = f" (Intelligence Inherited: Increased dry threshold to {current_threshold}% due to recent ineffectiveness)"

        if soil_info["status"] == "wet":
            decision = "OFF"
            reasons.append(f"Soil is wet ({soil_info['moisture']}%).")
        elif soil_info["moisture"] >= current_threshold and soil_info["status"] != "extremely_dry":
            decision = "OFF"
            reasons.append(f"Soil moisture is sufficient ({soil_info['moisture']}% vs threshold {current_threshold}%).")
        elif soil_info["needs_water"] or soil_info["moisture"] < current_threshold:
            if weather_info["can_wait_for_rain"] and soil_info["status"] != "extremely_dry":
                decision = "OFF"
                reasons.append("Soil is dry but rain is expected soon. Conserving water.")
            elif self._is_recent_watering(last_watered):
                decision = "OFF"
                reasons.append(f"Soil is dry but it was recently watered ({last_watered}). Waiting for absorption.")
            else:
                decision = "ON"
                reasons.append(f"Soil requires hydration ({soil_info['status']}). {strategy_adjustment}")
                if weather_info["high_evaporation"]:
                    reasons.append("High evaporation risk detected due to heat.")
                if soil_info["trend"] == "drying_fast":
                    reasons.append("Soil is drying fast.")

        return {
            "decision": decision,
            "reason": " ".join(reasons),
            "confidence": confidence,
            "threshold_used": current_threshold
        }

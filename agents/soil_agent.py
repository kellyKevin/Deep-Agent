from .base import BaseAgent
from typing import Dict, Any, List

class SoilIntelligenceSubagent(BaseAgent):
    """
    Purpose: Analyze soil behavior over time.
    Answers: “How fast does this soil lose water?”
    """
    def __init__(self, threshold_dry: int = 40, threshold_extremely_dry: int = 20, threshold_wet: int = 70):
        super().__init__("SoilIntelligenceSubagent")
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
        drying_rate = 0.0
        if history and len(history) >= 2:
            # Simple rate calculation: change in moisture per event
            recent_moistures = [h.get("sensors", {}).get("moisture", 50) for h in history[-5:]]
            if len(recent_moistures) >= 2:
                diff = recent_moistures[-1] - recent_moistures[0]
                drying_rate = abs(diff) / len(recent_moistures)
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
            "drying_rate": drying_rate,
            "needs_water": status in ["dry", "extremely_dry"]
        }

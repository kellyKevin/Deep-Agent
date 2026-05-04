import datetime
import json
import os
from .base import BaseAgent
from typing import Dict, Any, List, Optional

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
            insights = self.get_insights()
            insights.append(insight)
            if len(insights) > 500:
                insights = insights[-500:]

            with open(self.knowledge_base_path, "w") as f:
                json.dump(insights, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to log insight: {e}")

    def get_insights(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def get_efficiency_report(self) -> Dict[str, Any]:
        """Calculates efficiency scores from history."""
        insights = self.get_insights()
        if not insights:
            return {"score": 0.5, "status": "no_data"}

        effective_count = sum(1 for i in insights if i.get("effectiveness", {}).get("status") == "effective")
        total_actions = sum(1 for i in insights if "effectiveness" in i)

        score = effective_count / total_actions if total_actions > 0 else 0.5
        return {
            "score": score,
            "total_actions": total_actions,
            "effective_actions": effective_count
        }

import unittest
import json
import os
import sys

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import SmartIrrigationAgent

class TestSmartIrrigationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SmartIrrigationAgent()

    def test_example_scenario(self):
        data = {
            "soil_moisture": 35,
            "temperature": 28,
            "rain_expected": True,
            "last_watered": "2 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "OFF")
        self.assertIn("rain is expected", result["reason"])

    def test_dry_no_rain(self):
        data = {
            "soil_moisture": 30,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("Soil requires hydration", result["reason"])

    def test_extremely_dry_with_rain(self):
        data = {
            "soil_moisture": 15,
            "temperature": 28,
            "rain_expected": True,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("extremely_dry", result["reason"])

    def test_optimal_moisture(self):
        data = {
            "soil_moisture": 50,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "5 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "OFF")

    def test_recently_watered_dry(self):
        data = {
            "soil_moisture": 30,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "30 minutes ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "OFF")
        self.assertIn("recently watered", result["reason"])

    def test_hot_weather_dry_soil(self):
        data = {
            "soil_moisture": 30,
            "temperature": 35,
            "rain_expected": False,
            "last_watered": "10 hours ago",
            "time_of_day": 14
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("High evaporation risk detected", result["reason"])

    def test_soil_trend_analysis(self):
        from agents.soil_agent import SoilIntelligenceSubagent
        soil_agent = SoilIntelligenceSubagent()

        # Scenario: Soil is drying
        history = [
            {"sensors": {"moisture": 45}},
            {"sensors": {"moisture": 44}},
            {"sensors": {"moisture": 43}}
        ]
        result = soil_agent.analyze({"soil_moisture": 43}, history)
        self.assertEqual(result["trend"], "drying")

        # Scenario: Soil is drying fast
        history = [
            {"sensors": {"moisture": 50}},
            {"sensors": {"moisture": 47}},
            {"sensors": {"moisture": 44}}
        ]
        result = soil_agent.analyze({"soil_moisture": 44}, history)
        self.assertEqual(result["trend"], "drying_fast")

    def test_learning_agent_insight_storage(self):
        import os
        import json
        from agents.learning_agent import LearningSubagent

        kb_path = "test_knowledge_base.json"
        if os.path.exists(kb_path):
            os.remove(kb_path)

        learning_agent = LearningSubagent(knowledge_base_path=kb_path)

        input_data = {"soil_moisture": 30}
        result = {"decision": "ON", "reason": "Dry"}
        # Needs > 2% gain for effective
        history = [{"action": "PUMP_ON", "sensors": {"moisture": 25}}]

        learning_agent.learn(input_data, result, history)

        self.assertTrue(os.path.exists(kb_path))
        with open(kb_path, "r") as f:
            insights = json.load(f)
            self.assertEqual(len(insights), 1)
            self.assertEqual(insights[0]["effectiveness"]["moisture_gain"], 5)
            self.assertEqual(insights[0]["effectiveness"]["status"], "effective")

        os.remove(kb_path)

    def test_intelligence_inheritance(self):
        from agents.decision_agent import IrrigationDecisionSubagent
        decision_agent = IrrigationDecisionSubagent()

        # Mock insights with many ineffective actions
        insights = [
            {"effectiveness": {"status": "ineffective"}} for _ in range(5)
        ]

        # Soil is at 42% (Optimal > 40%)
        soil_info = {"status": "optimal", "moisture": 42, "needs_water": False, "trend": "stable"}
        weather_info = {"can_wait_for_rain": False, "high_evaporation": False}

        # Without insights, it should be OFF
        result_no_insights = decision_agent.decide(soil_info, weather_info, "10 hours ago")
        self.assertEqual(result_no_insights["decision"], "OFF")

        # With insights, threshold should increase to 45%, so 42% is now "requires hydration"
        result_with_insights = decision_agent.decide(soil_info, weather_info, "10 hours ago", insights)
        self.assertEqual(result_with_insights["decision"], "ON")
        self.assertIn("Intelligence Inherited", result_with_insights["reason"])

if __name__ == "__main__":
    unittest.main()

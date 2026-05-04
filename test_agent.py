import unittest
import json
import os
from agent import SmartIrrigationAgent, RainPredictionSkill, WateringProcedureSkill, LearningUpdateSkill

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
        self.assertIn("rain expected", result["reason"])

    def test_dry_no_rain(self):
        data = {
            "soil_moisture": 30,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("Soil is dry", result["reason"])

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
        self.assertIn("Recently watered", result["reason"])

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
        self.assertIn("High evaporation risk", result["reason"])

    def test_skills_individually(self):
        rain_skill = RainPredictionSkill("RainCheck")
        res = rain_skill.execute({"rain_expected": True, "temperature": 25})
        self.assertTrue(res["will_rain"])
        self.assertTrue(res["can_wait"])

        water_skill = WateringProcedureSkill("Watering")
        res = water_skill.execute({"soil_moisture": 15}, 40)
        self.assertEqual(res["action"], "ON")
        self.assertEqual(res["duration"], 30)

    def test_intelligence_inheritance(self):
        kb_path = "test_kb_inheritance.json"
        if os.path.exists(kb_path): os.remove(kb_path)

        # Mock a knowledge base with 4 ineffective waterings
        kb = []
        for _ in range(4):
            kb.append({
                "effectiveness": {"status": "ineffective"}
            })

        data_soil = {"moisture": 30, "status": "dry", "needs_water": True, "trend": "stable"}
        data_weather = {"can_wait_for_rain": False, "high_evaporation": True}

        # Use decision agent directly
        from agent import IrrigationDecisionAgent
        decision_agent = IrrigationDecisionAgent()
        result = decision_agent.decide(data_soil, data_weather, "10 hours ago", kb)

        self.assertIn("Bias: Previous waterings in these conditions were ineffective", result["reason"])

    def test_learning_agent_insight_storage(self):
        kb_path = "test_kb.json"
        if os.path.exists(kb_path): os.remove(kb_path)

        from agent import LearningAgent
        learning_agent = LearningAgent(knowledge_base_path=kb_path)

        input_data = {"soil_moisture": 30}
        result = {"decision": "ON", "reason": "Dry"}
        history = [{"action": "PUMP_ON", "sensors": {"moisture": 25}}]

        learning_agent.learn(input_data, result, history)

        self.assertTrue(os.path.exists(kb_path))
        with open(kb_path, "r") as f:
            insights = json.load(f)
            self.assertEqual(len(insights), 1)
            self.assertEqual(insights[0]["effectiveness"]["gain"], 5)

        os.remove(kb_path)

if __name__ == "__main__":
    unittest.main()

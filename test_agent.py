import unittest
import json
from agent import SmartIrrigationAgent

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
        self.assertIn("Rain is expected soon", result["reason"])
        self.assertEqual(result["confidence"], "high")

    def test_dry_no_rain(self):
        data = {
            "soil_moisture": 30,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("Soil is dry and needs watering", result["reason"])

    def test_dry_hot_no_rain(self):
        data = {
            "soil_moisture": 30,
            "temperature": 35,
            "rain_expected": False,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("High temperature", result["reason"])

    def test_extremely_dry_with_rain(self):
        data = {
            "soil_moisture": 15,
            "temperature": 28,
            "rain_expected": True,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("extremely dry", result["reason"])

    def test_optimal_moisture(self):
        data = {
            "soil_moisture": 50,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "5 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "OFF")
        self.assertIn("optimal", result["reason"])

    def test_wet_moisture(self):
        data = {
            "soil_moisture": 80,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "1 hour ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "OFF")
        self.assertIn("wet", result["reason"])

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

    def test_historical_insight_ineffective(self):
        data = {
            "soil_moisture": 30,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "10 hours ago",
            "insights": [
                {"type": "watering_effectiveness", "improvement": 2, "timestamp": "2023-01-01T12:00:00"}
            ]
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("Historical data suggests watering is not very effective", result["reason"])

    def test_feedback_loop(self):
        from mock_api import MockIrrigationAPI
        import time

        api = MockIrrigationAPI()
        api.rain_expected = False
        api.last_watered = "10 hours ago"
        agent = SmartIrrigationAgent(api)

        # 1. Soil is dry
        api.log_sensor_data(30, 25)

        # 2. Agent decides to water
        agent.run()
        self.assertEqual(api.pump_state, "ON")

        # 3. Simulate time pass and soil moisture change
        # We need to ensure the timestamp of next sensor reading is later
        # Mocking time might be better but for this simple test:
        time.sleep(0.01)
        api.log_sensor_data(33, 25) # 3% improvement

        # 4. Run feedback loop evaluation
        agent.evaluate_last_action()

        insights = api.get_insights()
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]["improvement"], 3)

if __name__ == "__main__":
    unittest.main()

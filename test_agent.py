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
        self.assertIn("rain is expected", result["reason"])
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
        self.assertIn("Soil is dry and no rain is expected", result["reason"])

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

if __name__ == "__main__":
    unittest.main()

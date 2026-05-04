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

    def test_dry_no_rain(self):
        data = {
            "soil_moisture": 30,
            "temperature": 25,
            "rain_expected": False,
            "last_watered": "10 hours ago"
        }
        result = self.agent.decide(data)
        self.assertEqual(result["decision"], "ON")
        self.assertIn("Soil is dry and no immediate relief", result["reason"])

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

if __name__ == "__main__":
    unittest.main()

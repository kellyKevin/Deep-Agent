import json
from datetime import datetime, timedelta

class MockIrrigationAPI:
    def __init__(self):
        self.soil_moisture = 35
        self.temperature = 28
        self.rain_expected = True
        self.last_watered = "2 hours ago"
        self.pump_state = "OFF"
        self.history = []
        self.insights = []

    def get_soil_data(self):
        return {
            "soil_moisture": self.soil_moisture,
            "temperature": self.temperature,
            "last_watered": self.last_watered
        }

    def get_weather(self):
        return {
            "rain_expected": self.rain_expected,
            "temperature": self.temperature
        }

    def post_pump(self, state):
        if state not in ["ON", "OFF"]:
            return {"error": "Invalid state"}, 400

        # Log the action
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "pump",
            "state": state,
            "soil_moisture_before": self.soil_moisture
        })

        self.pump_state = state
        return {"status": f"Pump turned {state}"}

    def log_sensor_data(self, soil_moisture, temperature):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "sensor_reading",
            "soil_moisture": soil_moisture,
            "temperature": temperature
        })
        self.soil_moisture = soil_moisture
        self.temperature = temperature

    def get_history(self):
        return self.history

    def add_insight(self, insight):
        self.insights.append(insight)

    def get_insights(self):
        return self.insights

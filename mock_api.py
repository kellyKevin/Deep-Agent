import json

class MockIrrigationAPI:
    def __init__(self):
        self.soil_moisture = 35
        self.temperature = 28
        self.rain_expected = True
        self.last_watered = "2 hours ago"
        self.pump_state = "OFF"

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
        self.pump_state = state
        return {"status": f"Pump turned {state}"}

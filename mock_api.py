import datetime

class MockIrrigationAPI:
    def __init__(self):
        self.soil_moisture = 35
        self.temperature = 28
        self.humidity = 60
        self.rain_expected = True
        self.last_watered = "2 hours ago"
        self.pump_state = "OFF"
        self.history = []

    def get_soil_data(self):
        return {
            "soil_moisture": self.soil_moisture,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "last_watered": self.last_watered,
            "timestamp": datetime.datetime.now().isoformat()
        }

    def get_weather(self):
        # Time of day simulation: Hour of the day
        hour = datetime.datetime.now().hour
        return {
            "rain_expected": self.rain_expected,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "time_of_day": hour,
            "forecast": "Cloudy" if self.rain_expected else "Sunny"
        }

    def post_pump(self, state):
        if state not in ["ON", "OFF"]:
            return {"error": "Invalid state"}, 400

        previous_state = self.pump_state
        self.pump_state = state

        # Log the action
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": f"PUMP_{state}",
            "previous_state": previous_state,
            "sensors": {
                "moisture": self.soil_moisture,
                "temp": self.temperature
            }
        }
        self.history.append(event)

        # Simulate some moisture increase if pump is ON
        if state == "ON":
            self.soil_moisture = min(100, self.soil_moisture + 5)
            self.last_watered = "0 minutes ago"

        return {"status": f"Pump turned {state}", "event": event}

    def get_history(self):
        return self.history

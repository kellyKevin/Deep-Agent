from .base import BaseAgent
from typing import Dict, Any

class DeviceControlSubagent(BaseAgent):
    """
    Purpose: Interface with ESP32.
    Sends commands: ON/OFF pump.
    Receives sensor data.
    """
    def __init__(self, api_client):
        super().__init__("DeviceControlSubagent")
        self.api_client = api_client

    def get_telemetry(self) -> Dict[str, Any]:
        if not self.api_client:
            return {"soil": {}, "weather": {}, "history": []}

        soil_data = self.api_client.get_soil_data()
        weather_data = self.api_client.get_weather()
        history = []
        if hasattr(self.api_client, 'get_history'):
            history = self.api_client.get_history()

        return {
            "soil": soil_data,
            "weather": weather_data,
            "history": history
        }

    def execute_command(self, decision: str):
        if self.api_client:
            self.api_client.post_pump(decision)

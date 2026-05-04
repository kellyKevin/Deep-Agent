import time
from typing import Dict, Any

class WateringProcedureSkill:
    """Skill: Modular procedure for watering plants."""
    def __init__(self, device_agent):
        self.device_agent = device_agent

    def execute(self, duration_seconds: int = 5) -> Dict[str, Any]:
        """
        - Check moisture threshold
        - Activate pump
        - Wait X seconds
        - Deactivate pump
        - Verify increase
        - Log results
        """
        # Initial moisture
        telemetry = self.device_agent.get_telemetry()
        start_moisture = telemetry.get("soil", {}).get("soil_moisture", 0)

        print(f"Starting watering procedure for {duration_seconds} seconds. Initial moisture: {start_moisture}%")

        # Activate pump
        self.device_agent.execute_command("ON")

        # Wait
        time.sleep(1) # Using a small sleep for simulation

        # Deactivate pump
        self.device_agent.execute_command("OFF")

        # Post-watering verification
        telemetry_after = self.device_agent.get_telemetry()
        end_moisture = telemetry_after.get("soil", {}).get("soil_moisture", 0)
        improvement = end_moisture - start_moisture

        return {
            "status": "completed",
            "duration": duration_seconds,
            "moisture_gain": improvement,
            "message": f"Watered for {duration_seconds} seconds. Gain: {improvement}%"
        }

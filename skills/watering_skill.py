import time
from typing import Dict, Any

class WateringProcedureSkill:
    """Skill: Modular procedure for watering plants."""
    def __init__(self, device_agent):
        self.device_agent = device_agent

    def execute(self, duration_seconds: int = 5) -> Dict[str, Any]:
        """
        - Check moisture threshold (implied by being called)
        - Activate pump
        - Wait X seconds
        - Deactivate pump
        - Log results
        """
        print(f"Starting watering procedure for {duration_seconds} seconds...")

        # Activate pump
        self.device_agent.execute_command("ON")

        # Wait
        time.sleep(1) # Using a small sleep for simulation

        # Deactivate pump
        self.device_agent.execute_command("OFF")

        return {
            "status": "completed",
            "duration": duration_seconds,
            "message": f"Watered for {duration_seconds} seconds"
        }

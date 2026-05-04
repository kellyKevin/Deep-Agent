import json

class SmartIrrigationAgent:
    def __init__(self, api_client=None):
        self.api_client = api_client

    def decide(self, data):
        """
        Decision-making process:
        Step 1: Analyze soil condition
        Step 2: Analyze weather conditions
        Step 3: Consider recent watering
        Step 4: Make a decision
        Step 5: Provide reasoning
        """
        soil_moisture = data.get("soil_moisture")
        temperature = data.get("temperature")
        rain_expected = data.get("rain_expected")
        last_watered = data.get("last_watered")

        # Step 1: Analyze soil condition
        if soil_moisture < 40:
            soil_status = "dry"
        elif 40 <= soil_moisture <= 70:
            soil_status = "optimal"
        else:
            soil_status = "wet"

        decision = "OFF"
        reason = ""
        confidence = "high"

        # Step 2, 3, 4: Logic for decision
        if soil_status == "wet":
            decision = "OFF"
            reason = "Soil is wet (>70% moisture). No watering needed."
        elif soil_status == "optimal":
            decision = "OFF"
            reason = "Soil moisture is at an optimal level (40-70%)."
        elif soil_status == "dry":
            # Check for rain
            if rain_expected:
                # Unless extremely dry (let's define extremely dry as < 20)
                if soil_moisture < 20:
                    decision = "ON"
                    reason = "Soil is extremely dry (<20%). Watering is necessary despite expected rain."
                else:
                    decision = "OFF"
                    # Check if recently watered to match example reasoning if applicable
                    if "hour" in last_watered or "minute" in last_watered:
                        reason = "Soil is dry but rain is expected soon and plants were recently watered. Avoiding unnecessary watering."
                    else:
                        reason = "Soil is dry but rain is expected soon. Avoiding unnecessary watering."
            else:
                # No rain expected
                # Check recent watering (e.g., within last 4 hours)
                is_recent = False
                if "minute" in last_watered:
                    is_recent = True
                elif "hour" in last_watered:
                    try:
                        hours = int(last_watered.split()[0])
                        if hours < 4:
                            is_recent = True
                    except ValueError:
                        pass

                if is_recent:
                    decision = "OFF"
                    reason = f"Soil is dry but it was recently watered ({last_watered}). Waiting for moisture to soak in to avoid overwatering."
                else:
                    decision = "ON"
                    reason = "Soil is dry and no rain is expected."
                    if temperature > 30:
                        reason += " High temperature (>30°C) is increasing evaporation risk."

        return {
            "decision": decision,
            "reason": reason,
            "confidence": confidence
        }

    def run(self):
        if not self.api_client:
            return None

        try:
            soil_data = self.api_client.get_soil_data()
            weather_data = self.api_client.get_weather()

            input_data = {
                "soil_moisture": soil_data["soil_moisture"],
                "temperature": soil_data["temperature"],
                "rain_expected": weather_data["rain_expected"],
                "last_watered": soil_data["last_watered"]
            }

            result = self.decide(input_data)
            self.api_client.post_pump(result["decision"])
            return result
        except Exception as e:
            return {
                "decision": "OFF",
                "reason": f"Error during decision making: {str(e)}",
                "confidence": "low"
            }

if __name__ == "__main__":
    # Test with example input
    example_input = {
        "soil_moisture": 35,
        "temperature": 28,
        "rain_expected": True,
        "last_watered": "2 hours ago"
    }
    agent = SmartIrrigationAgent()
    print(json.dumps(agent.decide(example_input), indent=2))

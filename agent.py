import json
from datetime import datetime

class WeatherAgent:
    def analyze(self, data):
        rain_expected = data.get("rain_expected")
        temperature = data.get("temperature")

        recommendation = "NEUTRAL"
        reason = ""

        if rain_expected:
            recommendation = "OFF"
            reason = "Rain is expected soon."
        elif temperature > 30:
            recommendation = "ON"
            reason = "High temperature (>30°C) increases evaporation risk."

        return {"recommendation": recommendation, "reason": reason}

class SoilAgent:
    def analyze(self, data):
        soil_moisture = data.get("soil_moisture")
        last_watered = data.get("last_watered")

        if soil_moisture < 20:
            status = "CRITICAL"
        elif soil_moisture < 40:
            status = "DRY"
        elif 40 <= soil_moisture <= 70:
            status = "OPTIMAL"
        else:
            status = "WET"

        recommendation = "NEUTRAL"
        reason = ""

        if status == "WET":
            recommendation = "OFF"
            reason = "Soil is already wet."
        elif status == "OPTIMAL":
            recommendation = "OFF"
            reason = "Soil moisture is at an optimal level."
        elif status == "CRITICAL":
            recommendation = "ON"
            reason = "Soil is extremely dry (<20%)."
        elif status == "DRY":
            # Check if recently watered
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
                recommendation = "OFF"
                reason = f"Soil is dry but it was recently watered ({last_watered})."
            else:
                recommendation = "ON"
                reason = "Soil is dry and needs watering."

        return {"recommendation": recommendation, "reason": reason, "status": status}

class SmartIrrigationAgent:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.weather_agent = WeatherAgent()
        self.soil_agent = SoilAgent()

    def evaluate_last_action(self):
        """
        Feedback Loop: Evaluate if the last watering action was effective.
        """
        if not self.api_client:
            return

        history = self.api_client.get_history()
        if not history:
            return

        # Find the last pump ON action and its subsequent sensor reading
        last_pump_on = None
        for entry in reversed(history):
            if entry.get("action") == "pump" and entry.get("state") == "ON":
                last_pump_on = entry
                break

        if last_pump_on:
            # Look for sensor reading after this pump action
            pump_time = datetime.fromisoformat(last_pump_on["timestamp"])
            moisture_before = last_pump_on["soil_moisture_before"]

            for entry in history:
                if entry.get("action") == "sensor_reading":
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time > pump_time:
                        moisture_after = entry["soil_moisture"]
                        improvement = moisture_after - moisture_before

                        insight = {
                            "type": "watering_effectiveness",
                            "improvement": improvement,
                            "timestamp": entry["timestamp"]
                        }
                        self.api_client.add_insight(insight)
                        break

    def decide(self, data):
        weather_analysis = self.weather_agent.analyze(data)
        soil_analysis = self.soil_agent.analyze(data)

        # Consider historical insights
        insights = data.get("insights", [])
        avg_improvement = 0
        if insights:
            improvements = [i["improvement"] for i in insights if i["type"] == "watering_effectiveness"]
            if improvements:
                avg_improvement = sum(improvements) / len(improvements)

        decision = "OFF"
        reasons = []
        confidence = "high"

        soil_rec = soil_analysis["recommendation"]
        weather_rec = weather_analysis["recommendation"]

        # Coordination Logic
        if soil_analysis["status"] == "CRITICAL":
            decision = "ON"
            reasons.append(soil_analysis["reason"])
            if weather_rec == "OFF":
                reasons.append("Watering is necessary despite expected rain due to critical dryness.")
        elif soil_rec == "ON":
            if avg_improvement < 5 and insights:
                reasons.append(f"Historical data suggests watering is not very effective (avg improvement: {avg_improvement:.1f}%).")

            if weather_rec == "OFF":
                decision = "OFF"
                reasons.append(soil_analysis["reason"])
                reasons.append(weather_analysis["reason"])
                reasons.append("Avoiding unnecessary watering because rain is expected.")
            else:
                decision = "ON"
                reasons.append(soil_analysis["reason"])
                if weather_analysis["reason"]:
                    reasons.append(weather_analysis["reason"])
        else:
            decision = "OFF"
            reasons.append(soil_analysis["reason"])
            if weather_analysis["reason"] and weather_rec == "OFF":
                reasons.append(weather_analysis["reason"])

        return {
            "decision": decision,
            "reason": " ".join(reasons),
            "confidence": confidence
        }

    def run(self):
        if not self.api_client:
            return None

        try:
            soil_data = self.api_client.get_soil_data()
            weather_data = self.api_client.get_weather()
            insights = self.api_client.get_insights()

            input_data = {
                "soil_moisture": soil_data["soil_moisture"],
                "temperature": soil_data["temperature"],
                "rain_expected": weather_data["rain_expected"],
                "last_watered": soil_data["last_watered"],
                "insights": insights
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

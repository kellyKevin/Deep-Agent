# 🧠 🌱 Smart Irrigation Deep Agent

An autonomous Smart Irrigation AI Agent responsible for managing water usage efficiently based on environmental data.

## 🎯 Goal
Optimize plant health while minimizing unnecessary water usage.

## 🚀 How it Works
The agent follows a 5-step decision-making process:

1.  **Analyze soil condition**:
    -   `soil_moisture < 40` → Dry
    -   `soil_moisture between 40–70` → Optimal
    -   `soil_moisture > 70` → Wet
2.  **Analyze weather conditions**:
    -   If `rain_expected` is true, avoid watering unless the soil is extremely dry (< 20%).
    -   If `temperature > 30°C`, consider faster evaporation.
3.  **Consider recent watering**:
    -   Avoid overwatering if the system was recently activated.
4.  **Make a decision**:
    -   Turn pump `ON` only if necessary.
    -   Otherwise, keep pump `OFF`.
5.  **Provide reasoning**:
    -   Explain the reasoning behind the decision in a structured format.

## 🛠 Tools (APIs)
-   `GET /soil-data` → returns soil moisture, temperature, and last watered time.
-   `GET /weather` → returns rain forecast and temperature.
-   `POST /pump` → turns irrigation system ON or OFF.

## 📦 Output Format (Strict JSON)
```json
{
  "decision": "ON" or "OFF",
  "reason": "clear explanation of your reasoning",
  "confidence": "high/medium/low"
}
```

## 💻 Usage

### Prerequisites
- Python 3.x

### Running the Agent
To see the agent in action using the mock API:
```bash
python3 agent.py
```

### Running Tests
To run the unit tests and verify the logic:
```bash
python3 test_agent.py
```

## 📜 Rules
- Never waste water.
- Prioritize plant health.
- Be cautious with watering if rain is expected.
- Avoid rapid switching ON/OFF.
- Base decisions ONLY on provided data.

# 🧠 🌱 Smart Irrigation Deep Agent

An autonomous Smart Irrigation AI Agent responsible for managing water usage efficiently based on environmental data.

## 🎯 Goal
Optimize plant health while minimizing unnecessary water usage by making data-driven decisions.

## 🏗 Architecture
The system consists of three main components:
-   **Agent (`agent.py`)**: Contains the core decision-making logic.
-   **Mock API (`mock_api.py`)**: Simulates the environment (soil data, weather, pump control).
-   **Runner (`main.py`)**: The entry point that executes the agent in a continuous loop.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+

### Installation
1. Clone the repository.
2. Install dependencies (optional, as the mock version has no external requirements):
```bash
pip install -r requirements.txt
```

### Running the Agent
Execute the continuous monitoring loop:
```bash
python3 main.py
```
By default, the agent checks conditions every 10 seconds (configurable via `CHECK_INTERVAL` environment variable).

### Running Tests
Verify the agent's logic across different scenarios:
```bash
python3 test_agent.py
```

## 🧠 Decision Logic
The agent follows a 5-step process:
1.  **Analyze soil moisture**: Dry (<40%), Optimal (40–70%), Wet (>70%).
2.  **Analyze weather**: Postpone watering if rain is expected, unless soil is extremely dry (<20%).
3.  **Check history**: Avoid overwatering if recently watered (within 4 hours).
4.  **Execute**: Turn pump ON/OFF via POST request.
5.  **Reason**: Log the decision-making process in strict JSON format.

## 📦 Output Format
```json
{
  "decision": "ON",
  "reason": "Soil is dry and no rain is expected. High temperature (35°C) increases evaporation risk.",
  "confidence": "high"
}
```

## 📜 Rules
-   **Water Conservation**: Never waste water if rain is imminent.
-   **Plant Health**: Prioritize hydration when moisture levels are critically low.
-   **Stability**: Avoid rapid ON/OFF cycles.

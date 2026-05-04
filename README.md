# 🧠 🌱 Smart Irrigation Deep Agent Ecosystem

An autonomous Smart Irrigation AI Agent designed as a Deep Agent ecosystem, where specialized subagents work together under a Mission Controller to manage water usage efficiently.

## 🌌 The Big Shift: Multi-Agent Intelligence
This system is built on the principle that intelligence emerges from many small, specialized agents working together. Inspired by the coordination of forces in *Interstellar*, our system separates concerns into modular subagents and reusable skills.

## 🏗 Architecture

### 🤖 1. Mission Control Agent (`agents/mission_control.py`)
The central AI that receives telemetry from the device (ESP32/Mock), coordinates subagents, and delegates tasks.

### 🧩 2. Subagents (`agents/`)
-   **🌧 Weather Subagent**: Analyzes external conditions and predicts rain.
-   **🌱 Soil Intelligence Subagent**: Tracks moisture trends and detects drying patterns.
-   **💧 Irrigation Decision Subagent**: Determines the watering strategy based on context.
-   **📊 Learning Subagent**: Evaluates actions vs. outcomes to improve the system over time.
-   **⚙️ Device Control Subagent**: Interfaces with the hardware/API.

### ⚙️ 3. Skills (`skills/`)
Reusable procedures loaded only when needed:
-   **Watering Procedure**: Multi-step process for activating/deactivating the pump.
-   **Rain Prediction Check**: Extracts probability from weather data.
-   **Learning Update**: Evaluates efficiency and updates the knowledge base.

## 🛰 "Message Across Time" (Intelligence Inheritance)
The system stores decisions and outcomes in `knowledge_base.json`. Future agent iterations "inherit" this intelligence, allowing them to adjust strategies (e.g., increasing thresholds) based on historical effectiveness.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- `python-dotenv`

### Installation
1. Clone the repository.
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Agent
Execute the continuous monitoring loop:
```bash
python3 main.py
```

### Running Tests
Verify the ecosystem's logic:
```bash
python3 test_agent.py
```

## 📦 Output Format
The agent outputs its decision-making process in a transparent JSON format:
```json
{
  "decision": "ON",
  "reason": "Soil is dry and no immediate relief from weather. High evaporation risk detected due to heat.",
  "confidence": "high",
  "metadata": {
    "soil": { "moisture": 30, "status": "dry", "trend": "drying_fast" },
    "weather": { "rain_expected": false, "temperature": 35 }
  }
}
```

## 📜 Repository Structure
- `agents/`: Core subagent logic.
- `skills/`: Reusable operational procedures.
- `api/`: API client and mocks.
- `knowledge_base.json`: Persistent intelligence stored over time.

# 🌌 🧠 🌱 Smart Irrigation Deep Agent: The Big Shift

An autonomous Multi-Agent Smart Farming System inspired by the concept of "Deep Agents" and distributed intelligence. This system manages water usage efficiently by coordinating specialized AI agents.

## 🚀 The Big Shift: Multi-Agent Intelligence
Intelligence is not one big brain — it’s many small specialized agents working together. This project transforms a monolithic irrigation script into a modular "Mission Control" ecosystem.

## 🏗 Multi-Agent Architecture

### 🤖 1. Mission Control Agent (The "Mission Controller")
The central AI that receives telemetry from the hardware (ESP32/Mock), coordinates analysis across subagents, and executes the final decision.

### 🌧 Weather Subagent
**Purpose:** Understand external conditions.
- Uses weather forecasts.
- Predicts rain and high evaporation risks.
- Answers: "Will it rain soon?"

### 🌱 Soil Intelligence Subagent
**Purpose:** Analyze soil behavior over time.
- Tracks moisture trends (drying fast, stable, hydrating).
- Detects patterns in how the soil retains water.

### 💧 Irrigation Decision Subagent
**Purpose:** Decide watering strategy.
- Combines insights from Soil and Weather subagents.
- Implements conservative watering logic to save water.

### 📊 Learning Subagent
**Purpose:** Improve system over time (The "Future Intelligence" layer).
- Compares actions vs. outcomes.
- Stores insights in `knowledge_base.json` for "inheritance" across sessions.

### ⚙️ Device Control Subagent
**Purpose:** Interface with the physical world.
- Sends commands to the pump.
- Aggregates sensor telemetry.

## 🔁 How They Work Together
1. **ESP32** → Sends soil & weather telemetry.
2. **Mission Control** → Asks Subagents for context.
3. **Weather Subagent** → "Rain expected in 2 hours."
4. **Soil Subagent** → "Soil retains water well; trend is stable."
5. **Decision Subagent** → "Decision: Wait — don't water."
6. **Device Control** → Sends `OFF` command.
7. **Learning Subagent** → Logs the decision for future optimization.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- `pip install -r requirements.txt`

### Running the Agent
Execute the continuous monitoring loop:
```bash
python3 main.py
```

### Running Tests
Verify the multi-agent logic and trend analysis:
```bash
python3 test_agent.py
```

## 📦 Output Format
The system communicates in strict JSON for interoperability:
```json
{
  "decision": "OFF",
  "reason": "Soil is dry but rain is expected soon. Conserving water.",
  "confidence": "high",
  "metadata": {
    "soil": { "moisture": 35, "status": "dry", "trend": "stable" },
    "weather": { "rain_expected": true, "summary": "Rain expected" }
  }
}
```

## 📜 Principles
- **Separation of Concerns**: Weather ≠ Soil ≠ Control. Each task is isolated for clean reasoning.
- **Future Intelligence**: Decisions are recorded to build a long-term knowledge base.
- **Water Conservation**: Prioritize plant health while minimizing waste through predictive analysis.

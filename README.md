# Smart Irrigation Deep Agent

This project implements an autonomous Smart Irrigation AI Agent responsible for managing water usage efficiently based on environmental data.

## Features
- Analyzes soil moisture, temperature, and rain forecast.
- Makes watering decisions (ON/OFF) based on a structured decision-making process.
- Minimizes water waste while prioritizing plant health.
- Provides reasoning for each decision in a strict JSON format.

## Decision Logic
1. **Analyze soil condition**:
   - < 40: Dry
   - 40–70: Optimal
   - > 70: Wet
2. **Analyze weather conditions**:
   - Rain expected: Avoid watering unless extremely dry.
   - High temperature (>30°C): Consider faster evaporation.
3. **Consider recent watering**: Avoid overwatering if recently watered.
4. **Output**: Strict JSON with `decision`, `reason`, and `confidence`.

## APIs Used
- `GET /soil-data`
- `GET /weather`
- `POST /pump`

import time
import logging
import json
import os
from dotenv import load_dotenv
from agent import SmartIrrigationAgent
from mock_api import MockIrrigationAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SmartIrrigationApp")

def main():
    load_dotenv()
    # In a real scenario, we might use a RealAPI client here
    # For now, we use the mock
    api_client = MockIrrigationAPI()
    agent = SmartIrrigationAgent(api_client)

    logger.info("Smart Irrigation Agent started. Press Ctrl+C to stop.")

    try:
        while True:
            logger.info("Analyzing conditions...")
            result = agent.run_once()

            # Print decision in strict JSON format as requested by the master prompt
            print(json.dumps(result, indent=2))

            logger.info(f"Decision: {result['decision']} | Confidence: {result['confidence']}")

            # Wait before next cycle (e.g., 1 hour in reality, 10s for demo)
            interval = int(os.getenv("CHECK_INTERVAL", 10))
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")

if __name__ == "__main__":
    main()

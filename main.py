import time
import logging
import json
import os
import sys
from dotenv import load_dotenv

# Ensure the root directory is in the path so we can import from agents and api
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agents import SmartIrrigationAgent
    from api.mock_api import MockIrrigationAPI
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SmartIrrigationApp")

def main():
    # Load environment variables
    load_dotenv()

    # Configuration
    kb_path = os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base.json")
    interval = int(os.getenv("CHECK_INTERVAL", 10))

    # In a real scenario, we might use a RealAPI client here
    # For now, we use the mock
    api_client = MockIrrigationAPI()
    agent = SmartIrrigationAgent(api_client)

    logger.info("Smart Irrigation Deep Agent Ecosystem started. Press Ctrl+C to stop.")
    logger.info(f"Checking every {interval}s. Knowledge base: {kb_path}")

    try:
        while True:
            logger.info("Mission Control: Analyzing conditions...")
            result = agent.run_once()

            # Print decision in strict JSON format
            print(json.dumps(result, indent=2), flush=True)

            logger.info(f"Decision: {result['decision']} | Confidence: {result['confidence']}")

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Agent stopped by user.")
    except Exception as e:
        logger.error(f"Critical error in main loop: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

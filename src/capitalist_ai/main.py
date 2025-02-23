#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from dotenv import load_dotenv
from capitalist_ai.crew import CapitalistAI

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """Run the crew with user input."""
    inputs = {
        'inquiry': input("Enter inquiry: ")
    }
    try:
        CapitalistAI().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        CapitalistAI().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """Replay the crew execution from a specific task."""
    try:
        CapitalistAI().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """Test the crew execution and returns the results."""
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        CapitalistAI().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    # Get the command from sys.argv
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "serve":
            from capitalist_ai.api.main import serve
            serve()
        elif command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            run()
    else:
        run()

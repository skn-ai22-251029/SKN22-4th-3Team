import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v2.preprocessor import V2Preprocessor

if __name__ == "__main__":
    processor = V2Preprocessor()
    # V2 preprocessor uses LLM and is async
    processor.run()

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v1.preprocessor import V1Preprocessor

if __name__ == "__main__":
    processor = V1Preprocessor()
    processor.run()

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v3.embedder import V3Embedder
from src.core.config import ZipsaConfig

async def main():
    policy = ZipsaConfig.get_policy("v3")
    embedder = V3Embedder()
    # Input is the output of preprocessor
    # Preprocessor output is hardcoded/configured in class as "data/v3/processed.json"
    input_path = "data/v3/processed.json" 
    await embedder.run(input_path)

if __name__ == "__main__":
    asyncio.run(main())

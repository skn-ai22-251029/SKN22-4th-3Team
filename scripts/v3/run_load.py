import sys
import os
import asyncio

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v3.loader import V3Loader

async def main():
    loader = V3Loader()
    # Input is the output of embedder
    input_path = "data/v3/embedded.pkl"
    await loader.run(input_path)

if __name__ == "__main__":
    asyncio.run(main())

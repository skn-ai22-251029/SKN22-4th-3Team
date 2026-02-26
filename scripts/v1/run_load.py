import sys
import os
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v1.loader import V1Loader

async def main():
    loader = V1Loader()
    input_path = "data/v1/embedded.pkl"
    await loader.run(input_path)

if __name__ == "__main__":
    asyncio.run(main())

import sys
import os
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v2.loader import V2Loader

async def main():
    loader = V2Loader()
    input_path = "data/v2/embedded.pkl"
    await loader.run(input_path)

if __name__ == "__main__":
    asyncio.run(main())

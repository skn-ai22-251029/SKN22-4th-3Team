import sys
import os
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
sys.path.append(PROJECT_ROOT)

from src.pipelines.v1.embedder import V1Embedder

async def main():
    embedder = V1Embedder()
    input_path = "data/v1/processed.json"
    await embedder.run(input_path)

if __name__ == "__main__":
    asyncio.run(main())

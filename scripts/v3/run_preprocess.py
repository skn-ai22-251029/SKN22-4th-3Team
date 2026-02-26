import sys
import os
import asyncio

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/v3/
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR)) # project root
sys.path.append(PROJECT_ROOT)

from src.pipelines.v3.preprocessor import V3Preprocessor
from dotenv import load_dotenv

load_dotenv()

async def main():
    limit = None
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
        
    processor = V3Preprocessor()
    await processor.run(limit=limit)

if __name__ == "__main__":
    asyncio.run(main())

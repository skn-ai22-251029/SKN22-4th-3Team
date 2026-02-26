import os
import pickle
import asyncio
from tqdm import tqdm
from src.utils.mongodb import MongoDBManager
from src.core.config import ZipsaConfig
from src.pipelines.base import BaseLoader

class V2Loader(BaseLoader):
    def __init__(self):
        self.policy = ZipsaConfig.get_policy("v2")
        self.db = MongoDBManager.get_v2_db() 
        self.collection = self.db[self.policy.collection_name]

    async def run(self, input_path: str):
        print(f"🚀 Starting V2 Loading from {input_path}...")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        with open(input_path, "rb") as f:
            items = pickle.load(f)
            
        print(f"📊 Loading {len(items)} documents into {self.policy.db_name}.{self.policy.collection_name}...")
        
        for item in tqdm(items, desc="Loading V2"):
            # Upsert based on UID (or title if UID is ephemeral/missing)
            key = {"uid": item.get("uid")} if item.get("uid") else {"title": item["title"]}
            
            await self.collection.update_one(
                key,
                {"$set": item},
                upsert=True
            )
            
        print("✨ V2 Loading Complete!")

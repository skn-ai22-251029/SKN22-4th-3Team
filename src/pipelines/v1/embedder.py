import os
import json
import pickle
import asyncio
from tqdm import tqdm
from src.embeddings.factory import EmbeddingFactory
from src.pipelines.base import BaseEmbedder

class V1Embedder(BaseEmbedder):
    def __init__(self):
        self.embedder = EmbeddingFactory.get_embedder()
        self.output_path = "data/v1/embedded.pkl"

    async def run(self, input_path: str) -> str:
        print(f"🚀 Starting V1 Embedding Generation reading from {input_path}...")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        with open(input_path, "r", encoding="utf-8") as f:
            items = json.load(f)
            
        print(f"📊 Generating embeddings for {len(items)} documents...")
        embedded_items = []
        
        for item in tqdm(items, desc="V1 Embedding"):
            # V1 Logic: [Category] Title Text
            cat = item.get("category", "General")
            content = f"[{cat}] {item['title']} {item.get('text', '')}"
            
            # OpenAI Call
            vector = await self.embedder.embed_query(content[:4000])
            
            item["embedding"] = vector
            embedded_items.append(item)
            
        with open(self.output_path, "wb") as f:
            pickle.dump(embedded_items, f)
            
        print(f"✨ Saved {len(embedded_items)} embedded items to {self.output_path} (Pickle format)")
        return self.output_path

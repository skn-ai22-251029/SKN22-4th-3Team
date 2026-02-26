import os
import json
import pickle
import asyncio
from tqdm import tqdm
from src.embeddings.factory import EmbeddingFactory
from src.pipelines.base import BaseEmbedder

class V2Embedder(BaseEmbedder):
    def __init__(self):
        self.embedder = EmbeddingFactory.get_embedder()
        self.output_path = "data/v2/embedded.pkl"

    async def run(self, input_path: str) -> str:
        print(f"🚀 Starting V2 Embedding Generation reading from {input_path}...")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        with open(input_path, "r", encoding="utf-8") as f:
            items = json.load(f)
            
        print(f"📊 Generating embeddings for {len(items)} documents...")
        embedded_items = []
        
        for item in tqdm(items, desc="V2 Embedding"):
            # V2 Logic: [Cats] [Specs] Title Text
            cats = ", ".join(item.get("categories", []))
            specs = ", ".join(item.get("specialists", []))
            content = f"[{cats}] [{specs}] {item['title']} {item.get('text', '')}"
            
            # OpenAI Call
            vector = await self.embedder.embed_query(content[:8000])
            
            item["embedding"] = vector
            embedded_items.append(item)
            
        # Save as Pickle
        with open(self.output_path, "wb") as f:
            pickle.dump(embedded_items, f)
            
        print(f"✨ Saved {len(embedded_items)} embedded items to {self.output_path} (Pickle format)")
        return self.output_path

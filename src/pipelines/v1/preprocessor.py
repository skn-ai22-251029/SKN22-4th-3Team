import os
import re
import json
import asyncio
from typing import List, Dict, Any
from tqdm import tqdm
from src.utils.text import tokenize_korean
from src.core.config import ZipsaConfig
from src.pipelines.base import BasePreprocessor
from src.pipelines.v1.classifier import V1Classifier

class V1Preprocessor(BasePreprocessor):
    def __init__(self):
        self.policy = ZipsaConfig.get_policy("v1")
        self.output_path = "data/v1/processed.json"
        self.classifier = V1Classifier()
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def clean_text(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def run_async(self) -> str:
        print("🚀 Starting V1 Preprocessing (Legacy)...")
        raw_path = "data/raw/bemypet_catlab.json" 
        
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Source data not found at {raw_path}")

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        print(f"📊 Processing {len(raw_items)} source documents...")
        processed_items = []
        batch_size = 5
        
        for i in range(0, len(raw_items), batch_size):
            batch = raw_items[i:i+batch_size]
            batch_data = []
            
            for j, item in enumerate(batch):
                global_idx = i + j
                title = self.clean_text(item.get("title", ""))
                text = self.clean_text(item.get("content", "") or item.get("text", ""))
                uid = f"doc_{global_idx}"
                
                batch_data.append({
                    "uid": uid,
                    "title": title,
                    "text": text,
                    "original_item": item 
                })
            
            print(f"🤖 Classifying batch {i}/{len(raw_items)}...")
            results = await self.classifier.classify_batch(batch_data)
            
            for doc_prep, meta in zip(batch_data, results):
                final_doc = doc_prep["original_item"].copy()
                final_doc.update(meta)
                
                final_doc["title"] = doc_prep["title"]
                final_doc["text"] = doc_prep["text"]
                final_doc["uid"] = meta.get("uid") or doc_prep["uid"]
                
                full_text = f"{final_doc['title']} {final_doc.get('summary', '')} {final_doc['text']}"
                final_doc["tokenized_text"] = tokenize_korean(full_text)
                
                processed_items.append(final_doc)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(processed_items, f, ensure_ascii=False, indent=2)
            
        print(f"✨ Saved {len(processed_items)} items to {self.output_path}")
        return self.output_path

    def run(self) -> str:
        return asyncio.run(self.run_async())

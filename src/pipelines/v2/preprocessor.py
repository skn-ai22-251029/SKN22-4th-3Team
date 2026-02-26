import os
import re
import json
import asyncio
from typing import List, Dict, Any
from tqdm import tqdm
from src.utils.text import tokenize_korean
from src.core.config import ZipsaConfig
from src.pipelines.base import BasePreprocessor
from src.pipelines.v2.classifier import V2Classifier

class V2Preprocessor(BasePreprocessor):
    def __init__(self):
        self.policy = ZipsaConfig.get_policy("v2")
        self.output_path = "data/v2/processed.json"
        self.classifier = V2Classifier()
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def run_async(self) -> str:
        print("🚀 Starting V2 Preprocessing (with LLM Classifier)...")
        
        # Raw Input
        raw_path = self.policy.raw_data_path 
        if not os.path.exists(raw_path):
             # Fallback if config path is relative/not found
             raw_path = "data/raw/bemypet_catlab.json"
        
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Source data not found at {raw_path}")

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        print(f"📊 Processing {len(raw_items)} source documents...")
        processed_items = []
        batch_size = 5 # LLM Batch Size
        
        # Process in batches
        for i in range(0, len(raw_items), batch_size):
            batch = raw_items[i:i+batch_size]
            batch_data = []
            
            # 1. Clean & Prepare for Classification
            for j, item in enumerate(batch):
                global_idx = i + j
                title = self.clean_text(item.get("title", ""))
                text = self.clean_text(item.get("content", "") or item.get("text", "")) # Handle potential field name diffs
                uid = f"doc_{global_idx}" # Temporary ID for classification matching
                
                batch_data.append({
                    "uid": uid,
                    "title": title,
                    "text": text,
                    "original_item": item 
                })
            
            # 2. Run Classification
            print(f"🤖 Classifying batch {i}/{len(raw_items)}...")
            results = await self.classifier.classify_batch(batch_data)
            
            # 3. Merge & Tokenize
            for doc_prep, meta in zip(batch_data, results):
                # Meta is a dict from Pydantic model
                # Merge logic
                final_doc = doc_prep["original_item"].copy()
                final_doc.update(meta) # Overwrite with LLM extracted metadata
                
                # Cleanup fields
                final_doc["title"] = doc_prep["title"]
                final_doc["text"] = doc_prep["text"]
                final_doc["uid"] = meta.get("uid") or doc_prep["uid"]
                
                # Tokenization
                full_text = f"{final_doc['title']} {final_doc.get('summary', '')} {final_doc['text']}"
                final_doc["tokenized_text"] = tokenize_korean(full_text)
                
                processed_items.append(final_doc)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(processed_items, f, ensure_ascii=False, indent=2)
            
        print(f"✨ Saved {len(processed_items)} items to {self.output_path}")
        return self.output_path

    # Synchronous wrapper for base interface if needed, but we encourage async
    def run(self) -> str:
        return asyncio.run(self.run_async())

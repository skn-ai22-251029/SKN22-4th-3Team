import os
import sys
import asyncio
import logging
import json

# Ensure src is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from src.preprocessing.markdown_loader import MarkdownLoader
from src.preprocessing.article_classifier import ArticleClassifier

# Processes pre-summarized markdown reports (like youtube_extract.md)
async def process_markdown_summaries():
    # We keep the file name youtube_extract.md as per previous instruction, 
    # but the loader/script is now generically named.
    INPUT_FILE = os.path.join(PROJECT_ROOT, 'data/raw/youtube_extract_info.md')
    OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'data/raw/youtube_extract_preprocessed.json')
    
    if not os.path.exists(INPUT_FILE):
        print(f"⚠️ Input file not found: {INPUT_FILE}")
        return

    print(f"🔍 Loading markdown data from {os.path.basename(INPUT_FILE)}...")
    loader = MarkdownLoader(INPUT_FILE)
    items = loader.load_and_parse()
    
    if not items:
        print("⚠️ No valid items found in the markdown file.")
        return
        
    print(f"✅ Found {len(items)} summaries to process.")
    
    classifier = ArticleClassifier()
    
    print(f"🚀 Processing metadata through LLM classifier...")
    # Single batch processing for small document sets
    results = await classifier.classify_batch(items)
    
    if not results:
        print("❌ LLM classification failed.")
        return

    # Merge extracted metadata with original text content
    final_data = []
    for res in results:
        uid = res.get('uid')
        original = next((item for item in items if item['uid'] == uid), None)
        if original:
            merged = original.copy()
            merged.update(res)
            final_data.append(merged)

    # Ensure data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Save finalized JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"✨ Successfully saved standardized data to {OUTPUT_FILE}")
    
    # Summary Statistics
    stats = {}
    for item in final_data:
        cat = item.get('category', 'Uncategorized')
        stats[cat] = stats.get(cat, 0) + 1
    
    print("\n📊 Classification Stats:")
    for cat, count in stats.items():
        print(f"  - {cat}: {count}")

if __name__ == "__main__":
    asyncio.run(process_markdown_summaries())

import os
import sys
import asyncio
import json
from typing import List, Set
from collections import Counter
from kiwipiepy import Kiwi
from tqdm import tqdm

# Ensure src is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from src.utils.mongodb import MongoDBManager
from src.core.config import ZipsaConfig

async def build_domain_dictionary():
    print("🚀 Starting Domain Dictionary Generation (From Raw Files)...")
    
    # Initialize Kiwi
    kiwi = Kiwi()
    
    # Input Paths
    raw_guides_path = os.path.join(PROJECT_ROOT, "data/raw/bemypet_catlab.json")
    
    # Use V3 Policy for breeds path
    v3_policy = ZipsaConfig.get_policy("v3")
    breeds_path = os.path.join(PROJECT_ROOT, v3_policy.breed_data_path)
    
    noun_counts = Counter()
    
    # 1. Process Guides
    if os.path.exists(raw_guides_path):
        with open(raw_guides_path, "r", encoding="utf-8") as f:
            guides = json.load(f)
            
        print(f"📊 Scanning Guides ({len(guides)} documents)...")
        for doc in tqdm(guides, desc="Scanning Guides"):
            text_content = f"{doc.get('title', '')} {doc.get('content', '')}" # Note: Raw data usually has 'content' or 'text'
            
            # Helper to handle list of strings if content is list
            if isinstance(doc.get('content'), list):
                 text_content += " ".join(doc.get('content'))
            
            if not text_content.strip():
                continue
                
            tokens = kiwi.tokenize(text_content)
            for t in tokens:
                if t.tag.startswith(('NNP', 'NNG')) and len(t.form) >= 2:
                    noun_counts[t.form] += 1
    else:
        print(f"⚠️ Warning: Guides file not found at {raw_guides_path}")

    # 2. Process Breeds
    if os.path.exists(breeds_path):
        with open(breeds_path, "r", encoding="utf-8") as f:
            breeds = json.load(f)
            
        print(f"📊 Scanning Breeds ({len(breeds)} documents)...")
        for doc in tqdm(breeds, desc="Scanning Breeds"):
            text_content = f"{doc.get('name_ko', '')} {doc.get('summary_ko', '')} "
            text_content += " ".join(doc.get('personality_traits', []))
            
            tokens = kiwi.tokenize(text_content)
            for t in tokens:
                if t.tag.startswith(('NNP', 'NNG')) and len(t.form) >= 2:
                    noun_counts[t.form] += 1
    else:
        print(f"⚠️ Warning: Breeds file not found at {breeds_path}")

    print(f"✅ Total unique nouns found: {len(noun_counts)}")
    
    # Filter Top 1000 to ensure coverage of common terms
    top_nouns = set([word for word, count in noun_counts.most_common(1000)])
    
    # Explicitly add ALL Breed Names
    breed_names = set()
    if os.path.exists(breeds_path):
        with open(breeds_path, "r", encoding="utf-8") as f:
            breeds_data = json.load(f)
            for b in breeds_data:
                name = b.get("name_ko", "")
                if name:
                    breed_names.add(name)
                    if name.endswith(" 고양이"):
                        breed_names.add(name.replace(" 고양이", ""))
                        
    print(f"🐈 Added {len(breed_names)} breed terms explicitly.")

    # 3. Process Synonyms (Explicitly add nicknames as NNP)
    synonyms_path = os.path.join(PROJECT_ROOT, "src/core/tokenizer/synonyms.json")
    synonym_terms = set()
    if os.path.exists(synonyms_path):
        with open(synonyms_path, "r", encoding="utf-8") as f:
            syn_data = json.load(f)
            
        for standard, aliases in syn_data.items():
            for alias in aliases:
                # Add alias to dictionary so it's tokenized as a single noun
                synonym_terms.add(alias)
                
        print(f"🔄 Added {len(synonym_terms)} synonym terms from synonyms.json.")
    else:
        print(f"⚠️ Warning: Synonyms file not found at {synonyms_path}")
    
    # 4. Process Extra Nouns
    extra_nouns_path = os.path.join(PROJECT_ROOT, "src/core/tokenizer/extra_nouns.txt")
    extra_nouns = set()
    if os.path.exists(extra_nouns_path):
        with open(extra_nouns_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split('\t')
                word = parts[0].strip()
                if word:
                    extra_nouns.add(word)
        print(f"➕ Added {len(extra_nouns)} extra noun terms.")

    # Merge: Top 1000 + Breeds + Synonyms + Extra Nouns
    final_dict = top_nouns | breed_names | synonym_terms | extra_nouns
    sorted_dict = sorted(list(final_dict))
    
    # Save to file
    output_path = os.path.join(PROJECT_ROOT, "src/core/tokenizer/domain_dictionary.txt")
    
    with open(output_path, "w", encoding="utf-8") as f:
        for word in sorted_dict:
            # Clean text (remove spaces if Kiwi doesn't like them, but NNG usually no spaces)
            if not word.strip(): continue
            f.write(f"{word}\tNNG\n")
            
    print(f"✨ Saved {len(sorted_dict)} terms to {output_path}")

if __name__ == "__main__":
    asyncio.run(build_domain_dictionary())

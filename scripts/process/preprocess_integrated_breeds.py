import os
import sys
import json
import csv
import asyncio
import math
from tqdm.asyncio import tqdm

# Ensure src is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from src.preprocessing.breed_classifier import BreedClassifier
from src.core.config import ZipsaConfig

async def preprocess_integrated_breeds():
    CSV_PATH = os.path.join(PROJECT_ROOT, 'data/raw/cat_breeds.csv')
    THECATAPI_PATH = os.path.join(PROJECT_ROOT, 'data/raw/cat_breeds_thecatapi.json')
    WIKI_PATH = os.path.join(PROJECT_ROOT, 'data/raw/cat_breeds_wiki_info.json')
    
    # Use V3 Policy for output path
    v3_policy = ZipsaConfig.get_policy("v3")
    OUTPUT_PATH = os.path.join(PROJECT_ROOT, v3_policy.breed_data_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    print("🔍 Loading raw breed data sources...")
    
    # 1. Load CSV
    breeds_master = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            breeds_master.append(row)
    
    # 2. Load TheCatAPI (Index by ID)
    with open(THECATAPI_PATH, 'r', encoding='utf-8') as f:
        thecatapi_list = json.load(f)
    thecatapi_map = {item['id']: item for item in thecatapi_list}

    # 3. Load Wiki (Index by Name - might need fuzzy matching or normalization)
    with open(WIKI_PATH, 'r', encoding='utf-8') as f:
        wiki_list = json.load(f)
    # Use lowercase normalization for matching
    wiki_map = {item['original_name'].lower(): item for item in wiki_list}

    print(f"📊 Ready to process {len(breeds_master)} breeds.")

    # Prepare integration items
    integration_items = []
    for breed in breeds_master:
        b_id = breed['id']
        b_name = breed['name']
        
        item = {
            "id": b_id,
            "name": b_name,
            "thecatapi_data": thecatapi_map.get(b_id, {}),
            "wiki_data": wiki_map.get(b_name.lower(), {})
        }
        integration_items.append(item)

    classifier = BreedClassifier()
    BATCH_SIZE = 5 # Small batch since we send a lot of context
    total_batches = math.ceil(len(integration_items) / BATCH_SIZE)
    
    final_results = []
    
    print(f"🚀 Integrating breed data in {total_batches} batches...")
    
    async for i in tqdm(range(0, len(integration_items), BATCH_SIZE), desc="Integrating Breeds"):
        batch = integration_items[i : i + BATCH_SIZE]
        results = await classifier.integrate_breed_data(batch)
        
        # Merge with initial stats for preservation (weight, life_span etc.)
        for res, original in zip(results, batch):
            res['stats'] = {
                "weight_metric": original['thecatapi_data'].get('weight', {}).get('metric'),
                "life_span": original['thecatapi_data'].get('life_span'),
                "indoor": original['thecatapi_data'].get('indoor'),
                "lap": original['thecatapi_data'].get('lap'),
                "hypoallergenic": original['thecatapi_data'].get('hypoallergenic'),
                "adaptability": original['thecatapi_data'].get('adaptability'),
                "affection_level": original['thecatapi_data'].get('affection_level'),
                "child_friendly": original['thecatapi_data'].get('child_friendly'),
                "dog_friendly": original['thecatapi_data'].get('dog_friendly'),
                "energy_level": original['thecatapi_data'].get('energy_level'),
                "grooming": original['thecatapi_data'].get('grooming'),
                "health_issues": original['thecatapi_data'].get('health_issues'),
                "intelligence": original['thecatapi_data'].get('intelligence'),
                "shedding_level": original['thecatapi_data'].get('shedding_level'),
                "social_needs": original['thecatapi_data'].get('social_needs'),
                "stranger_friendly": original['thecatapi_data'].get('stranger_friendly'),
                "vocalisation": original['thecatapi_data'].get('vocalisation')
            }
            res['source_urls'] = {
                "wiki": original['wiki_data'].get('url'),
                "cfa": original['thecatapi_data'].get('cfa_url'),
                "vetstreet": original['thecatapi_data'].get('vetstreet_url'),
                "vcahospitals": original['thecatapi_data'].get('vcahospitals_url')
            }
            final_results.append(res)

    # Save final JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)

    print(f"\n✨ Successfully integrated {len(final_results)} breeds into {OUTPUT_PATH}")

if __name__ == "__main__":
    asyncio.run(preprocess_integrated_breeds())

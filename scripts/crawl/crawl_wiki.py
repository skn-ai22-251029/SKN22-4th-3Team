import sys
import os
import csv
import pandas as pd
from time import sleep

# Add project root to sys.path to import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.wiki_api import WikipediaAPI

def main():
    input_file = 'data/raw/cat_breeds_thecatapi.json'
    output_file = 'data/raw/cat_breeds_wiki_info.json' # Let's keep consistency in variable naming, though file logic handles it below

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Load cat breeds from JSON
    try:
        import json
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        breeds = [item['name'] for item in data]
        # Remove duplicates just in case
        breeds = sorted(list(set(breeds)))
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    print(f"Found {len(breeds)} breeds to process.")
    
    wiki_api = WikipediaAPI()
    results = []
    
    for i, breed in enumerate(breeds):
        print(f"[{i+1}/{len(breeds)}] Searching for: {breed}")
        
        # Search candidates in order of preference
        # 1. Exact match + " cat" (e.g. "Siberian cat")
        # 2. Exact match (e.g. "Abyssinian")
        # 3. Cleaned match names (e.g. "Bengal Cats" -> "Bengal cat")
        
        # Special cases mapping
        SPECIAL_CASES = {
            "Cheetoh": "Cheetoh Cat"
        }

        if breed in SPECIAL_CASES:
            candidates = [SPECIAL_CASES[breed]]
        else:
            candidates = [f"{breed} cat", breed]
        
        # specific handling for "Cats" suffix in input
        if "Cats" in breed or "Cat" in breed:
            cleaned = breed.replace("Cats", "").replace("Cat", "").strip()
            if cleaned:
                candidates.append(f"{cleaned} cat")
                candidates.append(cleaned)
        
        found_info = None
        
        for candidate in candidates:
            info = wiki_api.get_page_info(candidate)
            if info:
                # Validation: Check if it's a disambiguation page or unrelated
                context_lower = info['context'].lower()
                title_lower = info['title'].lower()
                
                # Check for disambiguation indicators
                if "may refer to:" in info['context'] or "may refer to" in info['context']:
                    print(f"  - Skipped '{candidate}': Disambiguation page.")
                    continue
                
                # Check for relevance (must contain 'cat' or 'feline' or 'breed')
                # But be careful, 'cat' might be in 'location' etc.
                # simpler check: if we searched for "X cat", and got a result, it's likely relevant.
                # If we searched for "X", we need to be careful.
                keywords = ['cat', 'feline', 'breed', 'kitten']
                if not any(k in context_lower for k in keywords):
                    print(f"  - Skipped '{candidate}': Context doesn't look like a cat article.")
                    continue

                # If we searched for "Bombay" and got "Mumbai", reject it unless it mentions cat clearly.
                # verification: "Mumbai" context usually doesn't have "cat breed".
                
                found_info = info
                break
        
        if found_info:
            print(f"  -> Found: {found_info['title']}")
            results.append({
                'original_name': breed,
                'title': found_info['title'],
                'context': found_info['context'],
                'url': found_info['url'],
                'updated_at': found_info['updated_at']
            })
        else:
            print(f"  -> Failed to find info for {breed}")
            results.append({
                'original_name': breed,
                'title': None,
                'context': None,
                'url': None,
                'updated_at': None
            })
        
        # Be nice to the API
        sleep(0.5)

    # Save results to JSON
    output_json_file = 'data/raw/cat_breeds_wiki_info.json'
    import json
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"\nSaved results to {output_json_file}")

if __name__ == "__main__":
    main()

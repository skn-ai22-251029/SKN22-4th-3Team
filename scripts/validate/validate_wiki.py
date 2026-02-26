import json
import pandas as pd
from collections import Counter
import sys
import os

def validate():
    # Paths
    csv_path = 'data/raw/cat_breeds.csv'
    json_path = 'data/raw/cat_breeds_wiki_info.json'
    
    # Check files
    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print("Error: Missing data files.")
        return

    # Load Data
    try:
        df = pd.read_csv(csv_path)
        master_breeds = set(df['name'].dropna().tolist())
        
        with open(json_path, 'r', encoding='utf-8') as f:
            wiki_data = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"=== Validation Report ===\n")

    # 1. Coverage Check
    print(f"1. Coverage Check")
    wiki_breeds_set = set(item['original_name'] for item in wiki_data)
    
    missing_in_wiki = master_breeds - wiki_breeds_set
    extra_in_wiki = wiki_breeds_set - master_breeds
    
    print(f"   - Master list count: {len(master_breeds)}")
    print(f"   - Wiki data count: {len(wiki_data)}")
    
    if missing_in_wiki:
        print(f"   - [FAIL] Missing {len(missing_in_wiki)} breeds in Wiki data: {missing_in_wiki}")
    else:
        print(f"   - [PASS] All master breeds exist in Wiki data.")
        
    if extra_in_wiki:
         print(f"   - [WARN] Extra {len(extra_in_wiki)} breeds in Wiki data (not in master): {extra_in_wiki}")

    print()

    # 2. Success Rate Check
    print(f"2. Search Success Rate")
    found_items = [i for i in wiki_data if i.get('title')]
    failed_items = [i for i in wiki_data if not i.get('title')]
    
    print(f"   - Successfully found: {len(found_items)}")
    print(f"   - Failed to find: {len(failed_items)}")
    
    if failed_items:
        print(f"   - Failed breeds: {[i['original_name'] for i in failed_items]}")
    
    print()

    # 3. Duplicate Content (Redirects)
    print(f"3. Duplicate Content Check (Redirects)")
    urls = [i['url'] for i in found_items if i.get('url')]
    url_counts = Counter(urls)
    duplicates = {url: count for url, count in url_counts.items() if count > 1}
    
    if duplicates:
        print(f"   - [WARN] Found {len(duplicates)} URLs shared by multiple breeds:")
        for url, count in duplicates.items():
            breeds_sharing = [i['original_name'] for i in found_items if i.get('url') == url]
            print(f"     * {url} ({count} times): {breeds_sharing}")
    else:
        print(f"   - [PASS] No duplicate URLs found.")

    print()

    # 4. Content Quality
    print(f"4. Content Quality Check")
    short_content = [i for i in found_items if len(i.get('context', '')) < 100]
    
    if short_content:
        print(f"   - [WARN] {len(short_content)} items have very short content (<100 chars):")
        for i in short_content:
            print(f"     * {i['original_name']} ({len(i['context'])} chars)")
    else:
        print(f"   - [PASS] All found items have substantial content.")

if __name__ == "__main__":
    validate()

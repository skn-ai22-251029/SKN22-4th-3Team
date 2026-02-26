import json
from collections import Counter

def validate():
    file_path = "data/raw/bemypet_catlab.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"Total items: {len(data)}")
    
    # 1. Duplicates
    seen = set()
    duplicates = []
    for item in data:
        key = (item['title'], item['text'][:50]) # Use title and first 50 chars of text
        if key in seen:
            duplicates.append(item)
        seen.add(key)
    
    print(f"Duplicate items found: {len(duplicates)}")
    if duplicates:
        print(f"Sample duplicate: {duplicates[0]['title']}")

    # 2. Missing Fields
    missing_title = [i for i in data if not i.get('title')]
    missing_text = [i for i in data if not i.get('text')]
    print(f"Items missing title: {len(missing_title)}")
    print(f"Items missing text: {len(missing_text)}")

    # 3. Short Content
    short_text = [i for i in data if len(i.get('text', '')) < 50]
    print(f"Items with text < 50 chars: {len(short_text)}")
    if short_text:
        print("Sample short text items:")
        for i in short_text[:3]:
            print(f"  - Page {i['page']} Idx {i['index']}: {i['title']} (Len: {len(i['text'])})")

    # 4. Page Continuity
    pages = [i['page'] for i in data]
    page_counts = Counter(pages)
    sorted_pages = sorted(page_counts.keys())
    
    print(f"Page range: {min(sorted_pages)} to {max(sorted_pages)}")
    print(f"Unique pages collected: {len(sorted_pages)}")
    
    # Check for gaps
    missing_pages = []
    for p in range(min(sorted_pages), max(sorted_pages) + 1):
        if p not in page_counts:
            missing_pages.append(p)
            
    if missing_pages:
        print(f"Missing pages: {missing_pages}")
    else:
        print("No missing pages in the range.")

    # Check items per page
    abnormal_pages = {p: c for p, c in page_counts.items() if c != 10}
    print(f"Pages with != 10 items: {abnormal_pages}")

if __name__ == "__main__":
    validate()

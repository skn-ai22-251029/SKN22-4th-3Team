import json
import os
import random

def generate_testset():
    print("🚀 Generating Golden Dataset from V2 Potential Questions...")
    
    # Paths
    v2_path = "data/v2/bemypet_catlab_v2_preprocessed.json"
    output_path = "data/v3/golden_dataset.json"
    
    # Load V2 Data
    with open(v2_path, "r", encoding="utf-8") as f:
        v2_docs = json.load(f)

    # Load V3 Data (Source of Truth for IDs and Titles)
    v3_path = "data/v3/processed.json"
    if not os.path.exists(v3_path):
        print(f"❌ V3 Data not found at {v3_path}")
        return

    with open(v3_path, "r", encoding="utf-8") as f:
        v3_docs = json.load(f)

    # Create V3 Lookup Map (Key: First 50 chars of text -> Value: V3 Doc)
    # This handles the case where V3 dropped some V2 documents or reordered them.
    v3_map = {}
    for doc in v3_docs:
        # Normalize text: strip and take first 50 chars
        key = doc.get("text", "").strip()[:50]
        if key:
            v3_map[key] = doc
            
    print(f"🗺️ Created V3 Lookup Map with {len(v3_map)} entries.")

    evaluation_set = []
    count = 0
    matched_count = 0
    
    for v2_doc in v2_docs:
        questions = v2_doc.get("potential_questions", [])
        if not questions:
            continue
            
        # Try to find corresponding V3 doc
        v2_key = v2_doc.get("text", "").strip()[:50]
        v3_target = v3_map.get(v2_key)
        
        if not v3_target:
            # If no match found (likely filtered out in V3 pipeline), skip
            # specific logic could be added here to log missing
            continue
            
        matched_count += 1
            
        # Metadata from V3 (Target)
        target_uid = v3_target.get("uid")
        target_title = v3_target.get("title_refined")
        
        # Specialist mapping: Use V3's if available, else V2's
        specialist_list = v3_target.get("specialists", [])
        specialist = specialist_list[0] if specialist_list else "General"
        
        # Iterate through ALL potential questions
        for q in questions:
            evaluation_set.append({
                "query": q,
                "expected_keyword": target_title, # Ground Truth is the Refined Title
                "specialist": specialist,
                "source_doc_id": target_uid
            })
            count += 1
            
    print(f"🔗 Successfully matched {matched_count}/{len(v2_docs)} documents.")
        
    # Shuffle (Optional, but good for randomness if we inspect manually)
    random.shuffle(evaluation_set)
    final_set = evaluation_set # No limit
    
    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_set, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated {len(final_set)} test cases (Source: {count} docs).")
    print(f"📂 Saved to: {output_path}")

if __name__ == "__main__":
    generate_testset()

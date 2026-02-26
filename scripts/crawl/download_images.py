
import os
import json
import requests
from tqdm import tqdm

def download_images():
    RAW_PATH = "data/raw/cat_breeds_thecatapi.json"
    IMAGE_DIR = "static/images/breeds"
    
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        print(f"📁 Created directory: {IMAGE_DIR}")

    if not os.path.exists(RAW_PATH):
        print(f"❌ Raw data not found: {RAW_PATH}")
        return

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        breeds = json.load(f)

    print(f"🚀 Starting download for {len(breeds)} breed images...")
    
    success_count = 0
    fail_count = 0
    
    for breed in tqdm(breeds, desc="Downloading"):
        b_id = breed.get("id")
        image_info = breed.get("image")
        
        if not b_id or not image_info or not image_info.get("url"):
            continue
            
        img_url = image_info["url"]
        # Standardize extension to .jpg for simplicity in UI, or keep original. 
        # TheCatAPI usually returns jpg.
        ext = os.path.splitext(img_url)[1] or ".jpg"
        save_path = os.path.join(IMAGE_DIR, f"{b_id}{ext}")
        
        if os.path.exists(save_path):
            success_count += 1
            continue

        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"⚠️ Failed to download {b_id}: {e}")
            fail_count += 1

    print(f"\n✅ Download Finished!")
    print(f" - Success: {success_count}")
    print(f" - Failed: {fail_count}")
    print(f" - Path: {IMAGE_DIR}")

if __name__ == "__main__":
    download_images()

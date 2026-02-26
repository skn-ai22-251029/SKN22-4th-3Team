import os
import sys
import json
import time
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright

class BeMyPetCrawler:
    def __init__(self, max_pages: int = 2, start_page: int = 1):
        self.base_url = "https://bemypet.kr/content/catlab"
        self.max_pages = max_pages
        self.start_page = start_page

    def crawl(self) -> List[Dict[str, Any]]:
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Start at base URL (Page 1)
            page.goto(self.base_url, wait_until="networkidle")

            for page_num in range(1, self.max_pages + 1):
                print(f"Processing page {page_num}...")
                
                # Skipping logic if resuming
                if page_num < self.start_page:
                     print(f"  Skipping extraction for page {page_num} (already collected)")
                else: 
                    # Retry logic for empty pages (Rate limit handling)
                    max_retries = 3
                    for attempt in range(max_retries):
                        found_on_page = 0
                        for i in range(1, 11):
                            title_xpath = f"/html/body/div/div[2]/div[{i}]/div[1]/div[1]"
                            text_xpath = f"/html/body/div/div[2]/div[{i}]/div[1]/div[2]"
                            
                            if page.locator(f"xpath={title_xpath}").count() > 0:
                                title = page.locator(f"xpath={title_xpath}").inner_text()
                                text = ""
                                if page.locator(f"xpath={text_xpath}").count() > 0:
                                    text = page.locator(f"xpath={text_xpath}").inner_text()
                                
                                results.append({
                                    "page": page_num,
                                    "index": i,
                                    "title": title,
                                    "text": text,
                                    "source": "bemypet_catlab"
                                })
                                found_on_page += 1
                        
                        if found_on_page > 0:
                            print(f"  Found {found_on_page} items.")
                            break # Success
                        else:
                            print(f"  [Warning] Found 0 items on page {page_num}. Attempt {attempt+1}/{max_retries}")
                            if attempt < max_retries - 1:
                                wait_time = 30 * (attempt + 1)
                                print(f"  Waiting {wait_time}s before reloading...")
                                time.sleep(wait_time)
                                page.reload(wait_until="networkidle")
                            else:
                                print("  Failed to retrieve items. Saving debug screenshot.")
                                page.screenshot(path=f"fail_page_{page_num}.png")

                # Pagination Logic (Click 'Next')
                if page_num < self.max_pages:
                    next_li_xpath = "/html/body/div/div[2]/ul/li[contains(@class, 'active')]/following-sibling::li[1]"
                    next_li = page.locator(f"xpath={next_li_xpath}")
                    
                    if next_li.count() > 0:
                        class_attr = next_li.get_attribute("class") or ""
                        if "disabled" in class_attr:
                            print("Next page button is disabled. Stopping.")
                            break
                            
                        next_li.click()
                        
                        try:
                            time.sleep(3) 
                            page.wait_for_load_state("networkidle", timeout=10000)
                        except Exception as e:
                            print(f"Warning during pagination wait: {e}")
                    else:
                        print("No next page element found. Stopping.")
                        break
            
            browser.close()
            
        return results

    def save(self, data: List[Dict[str, Any]], filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} items to {filepath}")


def main():
    print("Starting crawler...")
    
    # Check Project Root relative to script
    # This script is at scripts/crawl/crawl_bemypet.py
    # Data should go to data/bemypet_catlab.json (at project root)
    
    # We are usually running from project root, but let's be safe.
    # If running "python scripts/crawl/crawl_bemypet.py", CWD is project root.
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "bemypet_catlab.json")
    
    existing_data = []
    start_page = 1
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            if existing_data:
                last_item = existing_data[-1]
                # Assuming page info is reliable, resume from next page
                start_page = last_item.get("page", 0) + 1
                print(f"Resuming from page {start_page} (Found {len(existing_data)} items)")
        except Exception as e:
            print(f"Error loading existing data: {e}")

    crawler = BeMyPetCrawler(max_pages=116, start_page=start_page) 
    new_data = crawler.crawl()
    
    if new_data:
        final_data = existing_data + new_data
        crawler.save(final_data, output_file)
    else:
        print("No new data collected.")

if __name__ == "__main__":
    main()

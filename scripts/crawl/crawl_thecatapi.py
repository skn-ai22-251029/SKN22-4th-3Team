import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler.thecatapi import TheCatAPICrawler

def main():
    try:
        crawler = TheCatAPICrawler()
        print("Starting crawl of TheCatAPI...")
        data = crawler.crawl()
        print(f"Successfully crawled {len(data)} breeds.")
        
        output_path = "data/raw/cat_breeds_thecatapi.json"
        crawler.save(data, output_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

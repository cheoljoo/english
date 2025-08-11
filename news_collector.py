import sys
sys.path.insert(0, '/usr/src/app/local_libs')

import csv
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

# Configuration
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "VentureBeat": "https://venturebeat.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "TechRadar": "https://www.techradar.com/rss",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Engadget": "https://www.engadget.com/rss.xml",
}
TODAY_DATE = datetime.now().strftime("%Y-%m-%d")
CSV_OUTPUT_FILE = "database-today.csv"
JSON_OUTPUT_FILE = "contents-today.temp.json"

def get_main_content(soup):
    """Extract main article text from a BeautifulSoup object."""
    # Try common article tags
    main_content = soup.find("article")
    if not main_content:
        main_content = soup.find("main")
    
    # Fallback to common content div classes
    if not main_content:
        content_divs = soup.find_all("div", class_=[ "post-content", "article-content", "entry-content", "post-body", "article-body" ])
        if content_divs:
            main_content = content_divs[0]

    # Generic fallback: get all text from body, but try to remove nav/footer
    if not main_content:
        main_content = soup.body
        if main_content:
            for tag in main_content.find_all(['nav', 'footer', 'header', 'script', 'style']):
                tag.decompose()

    if main_content:
        return main_content.get_text(separator='\n', strip=True)
    return ""

def process_feeds():
    """Fetch, parse, and process articles from RSS feeds."""
    csv_rows = []
    json_articles = []

    print("Starting to process feeds...")
    for name, url in RSS_FEEDS.items():
        try:
            print(f"Fetching {name}...")
            feed = feedparser.parse(url)
            if not feed.entries:
                print(f"Warning: No entries found for {name}")
                continue

            latest_entry = feed.entries[0]
            article_url = latest_entry.link
            article_title = latest_entry.title

            print(f"  - Latest article: '{article_title}'")
            print(f"  - URL: {article_url}")

            # Add to CSV data
            csv_rows.append([TODAY_DATE, article_url, article_title])

            # Fetch and parse full article for JSON
            print(f"  - Fetching full content...")
            response = requests.get(article_url, headers={'User-Agent': 'Mozilla/5.0 '}, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            source_text = get_main_content(soup)
            if not source_text:
                print(f"Warning: Could not extract main content from {article_url}")

            json_articles.append({
                "date": TODAY_DATE,
                "topic": article_title,
                "URL": article_url,
                "source": source_text,
            })
            print(f"  - Done with {name}.")

        except Exception as e:
            print(f"Error processing {name}: {e}")

    # Write CSV file
    print(f"\nWriting data to {CSV_OUTPUT_FILE}...")
    try:
        with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'URL', 'topic'])
            writer.writerows(csv_rows)
        print("CSV file written successfully.")
    except IOError as e:
        print(f"Error writing CSV file: {e}")


    # Write JSON file
    print(f"Writing data to {JSON_OUTPUT_FILE}...")
    try:
        with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(json_articles, f, indent=4, ensure_ascii=False)
        print("JSON file written successfully.")
    except IOError as e:
        print(f"Error writing JSON file: {e}")


if __name__ == "__main__":
    process_feeds()
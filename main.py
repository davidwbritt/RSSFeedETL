import time
import feedparser
import openai
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


# MongoDB setup
mongo_client = MongoClient("mongodb://172.17.0.4:27017/")
db = mongo_client["supply_chain"]
collection = db["leads"]


# Function to get a summary using ChatGPT
def get_summary(url):
    prompt = f"Please summarize the content of this webpage: {url}"
    response = openai.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=400
    )
    summary = response.choices[0].message.content.strip()
    return summary


# Function to process RSS feed
def process_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    print(f"Entries found in the RSS feed: {len(feed.entries)}")

    for entry in feed.entries:
        try:
            title = entry.title
            link = entry.link

            summary = get_summary(link)
            lead_data = {"title": title, "link": link, "summary": summary}
            collection.insert_one(lead_data)
            print(f"Inserted: {title}")
        except Exception as e:
            print(f"Error processing entry: {e}")


# Main loop
def main():
    rss_url = "https://rss.app/feeds/_oK0MhvUF4Gc3VH3t.xml"
    while True:
        process_rss_feed(rss_url)
        print("RSS feed processed. Waiting for 24 hours before next poll.")
        time.sleep(86400)


if __name__ == "__main__":
    main()

import time
import feedparser
import openai
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from pymongo import MongoClient
import json

client = openai.OpenAI()

# MongoDB setup
mongo_client = MongoClient("mongodb://172.17.0.4:27017/")
db = mongo_client["supply_chain"]
collection = db["articles"]


# Pydantic model
class ArticleData(BaseModel):
    title: str
    link: str
    entities: list[dict]


# Function to extract data using ChatGPT with token limit handling
def extract_data_from_text(text, max_tokens=4096):
    format = '{{"entities": [{{"entity": "Entity1","jurisdiction": "Jurisdiction1","flags": ["Flag1", "Flag2"]}}]}} Please to not add any tags or labels outside of the JSON structure.'
    prompt = f"This data is related to news about international trade and ethical sourcing. You will be provided with text to analyze. You are to please extract any entities (companies or persons), their jurisdiction (region), and one or more flags from the provided text. Your response should be data in the format: {format} \n\n The text to analyze: \n\n{text}."
    response = None
    entities = []
    while response is None:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert supply chain analyst, an expert with global economics, and a specialist in ethical trade. You pride yourself in your ability to extract entities (with jurisdiction), and flags from text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
            )
            response_text = response.choices[0].message.content.strip()
            print(response_text)
            data = json.loads(response_text)
            entities = data.get("entities", [])
        except openai.RateLimitError:
            print("Rate limit exceeded, waiting before retrying...")
            time.sleep(60)
        except requests.exceptions.ReadTimeout:
            print("Request timed out. Skipping...")
            return []
        except Exception as e:
            print(f"Invalid request error: {e}")
            return []

    return entities


# Function to extract text from <p> tags
def get_paragraph_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    paragraphs = soup.find_all("p")
    return " ".join(p.get_text() for p in paragraphs)


# Function to process RSS feed
def process_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    print(f"Entries found in the RSS feed: {len(feed.entries)}\n")
    for i, entry in enumerate(feed.entries, 1):
        print(i)
        try:
            title = entry.title
            link = entry.link
            article_content = requests.get(link, timeout=10).text
            paragraph_text = get_paragraph_text(article_content)

            print(title)
            print(link)
            print(paragraph_text)

            entities = extract_data_from_text(paragraph_text)

            if entities:
                article_data = ArticleData(title=title, link=link, entities=entities)
                collection.insert_one(article_data.model_dump())
        except Exception as e:
            print(f"Error processing entry {i}: {e}")


# Main loop
def main():
    rss_url = "https://rss.app/feeds/_oK0MhvUF4Gc3VH3t.xml"
    while True:
        process_rss_feed(rss_url)
        print("RSS feed processed. Waiting for 24 hours before next poll.")
        time.sleep(86400)


if __name__ == "__main__":
    main()

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from source import Source


def fetch_rss_feed(url: str) -> List[Source]:
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    # Namespace dictionary to handle the various XML namespaces in the RSS feed
    namespaces = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "media": "http://search.yahoo.com/mrss/",
    }

    channel = root.find("channel")
    channel_title = channel.find("title").text

    items = []
    for item in channel.findall("item"):
        title = item.find("title").text
        raw_description = item.find("description").text
        link = item.find("link").text
        guid = item.find("guid").text
        creator = item.find("dc:creator", namespaces).text
        pubDate = item.find("pubDate").text
        media_content = item.find("media:content", namespaces)
        media_content_url = (
            media_content.attrib["url"] if media_content is not None else None
        )

        # Clean HTML tags from the description
        soup = BeautifulSoup(raw_description, "html.parser")
        description = soup.get_text(separator=" ").strip()

        source_item = Source(
            title=title,
            description=description,
            link=link,
            guid=guid,
            creator=creator,
            pubDate=datetime.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %Z"),
            media_content_url=media_content_url,
            credibility=0.8,  # Example value, you can update this as needed
            processing_log=["Fetched from RSS feed"],
            channel_title=channel_title,
        )
        items.append(source_item)

    return items


if __name__ == "__main__":
    url = "https://rss.app/feeds/_oK0MhvUF4Gc3VH3t.xml"
    sources = fetch_rss_feed(url)
    for source in sources:
        print(source.model_dump_json(indent=2))

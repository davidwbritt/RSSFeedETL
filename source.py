from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class Source(BaseModel):
    title: str
    description: str
    link: HttpUrl
    guid: str
    creator: str
    pubDate: datetime
    media_content_url: Optional[HttpUrl]
    credibility: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    processing_log: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    channel_title: str

    class Config:
        schema_extra = {
            "example": {
                "title": "Example Title",
                "description": "Example Description",
                "link": "https://example.com",
                "guid": "example-guid",
                "creator": "Author Name",
                "pubDate": "2024-07-01T10:00:00Z",
                "media_content_url": "https://example.com/image.jpg",
                "credibility": 0.9,
                "date_created": "2024-07-01T10:00:00Z",
                "processing_log": ["Initial fetch", "Checked for updates"],
                "notes": "Some notes",
                "channel_title": "Flagged Entities Sources",
            }
        }

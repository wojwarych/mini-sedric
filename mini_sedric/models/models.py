"""Module keeping all pydantic models for FastAPI endpoints"""

from pydantic import BaseModel, Field


class InteractionInput(BaseModel):
    """Model for request body of /insights endpoint"""

    interaction_url: str = Field(pattern=r"^s3:\S+(.mp3)$")
    trackers: list[str]

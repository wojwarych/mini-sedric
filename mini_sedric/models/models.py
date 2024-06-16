"""Module keeping all pydantic models for FastAPI endpoints"""

from pydantic import BaseModel, Field


class InteractionInput(BaseModel):
    """Model for request body of /insights endpoint

    Attributes:
        interaction_url (str): URI in S3 format to the desired audio MP3 file
        trackers (list[str]): list of searched words in the transcription
    """

    interaction_url: str = Field(pattern=r"^s3:\S+(.mp3)$")
    trackers: list[str]

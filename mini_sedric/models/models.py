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


class TrackerData(BaseModel):
    """Model mapping tracker values for /insights response

    Attributes:
        sentence_index: (int): index of the sentence in the text
        start_word_index: (int): start index of the first word in the match
        end_word_index (int): end index of the last word in the match
        tracker_value (str): sentence that is matching
        transcribe_value (str): transcribed value from transcript
    """

    sentence_index: int
    start_word_index: int
    end_word_index: int
    tracker_value: str
    transcribe_value: str


class InsightsGetResponse(BaseModel):
    """Model returned by GET /insights/{job_name} call

    Attributes:
        insights (list[TrackerData]): list of found trakcers in the transcription
    """

    insights: list[TrackerData]


class InsightsPostResponse(BaseModel):
    """Model returned by POST /insights call

    Attributes:
        name (str): name of json with insights from transcription
    """

    name: str

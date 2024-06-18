"""
Extractor class holds routine for getting ready transcript and extracting matching
trackers to the text
"""

import json
import re
from collections.abc import Iterator
from urllib.parse import urlparse

from mini_sedric.s3_integration import S3BucketNotFoundException, S3Interface
from mini_sedric.transcribe_service import (
    TranscribeWorkerError,
    TranscribeWorkerInterface,
)

from .exceptions import JobServiceError


class InsightsExtractor:
    """Class for composing insights from transcription text"""

    def __init__(
        self, transcribe_service: TranscribeWorkerInterface, s3_interface: S3Interface
    ) -> None:
        self.transcribe_service = transcribe_service
        self.s3_interface = s3_interface

    def get_transcript_from_bucket(self, job_name: str) -> str:
        """ "
        Pulls transcribed text from S3 bucket and extracts the transcription from it

        Args:
            job_name (str): name of transcription job for which bucket should be checked

        Returns:
            str: transcribed string in the string format
        """
        try:
            transcription_uri = self.transcribe_service.get_transcript_uri(job_name)

            path_to_bucket = urlparse(transcription_uri).path.lstrip("/").split("/")
            bucket_name = path_to_bucket[0]
            object_key = path_to_bucket[1]

            object_data = self.s3_interface.get_object(bucket_name, object_key)

            return json.loads(object_data["Body"].read().decode("utf-8"))["results"][
                "transcripts"
            ][0]["transcript"]
        except (S3BucketNotFoundException, TranscribeWorkerError, KeyError) as e:
            raise JobServiceError("Extractor error!") from e

    def find_trackers(
        self, insights: list[str], transcript: str
    ) -> Iterator[dict[str, str | int]]:
        """
        Finds occurences of insight sentence from list of insights in transcription

        Args:
            insights (list[str]): list of tracker i.e. insights to look in text
        """
        for insight in insights:
            ret: dict[str, str | int] = {}
            pattern = rf"({insight})"
            search = re.search(pattern, transcript)
            if search:
                print(search)
                ret["start_word_index"] = search.start()
                ret["end_word_index"] = search.end()
                ret["tracker_value"] = insight
                ret["transcribe_value"] = search.group(1)
                # provide better way for sentence index
                ret["sentence_index"] = search.start()
                print(ret)
                yield ret

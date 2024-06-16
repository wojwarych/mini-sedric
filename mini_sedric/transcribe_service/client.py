"""Module that implements interface for TranscribeWorkerInterface"""

from typing import Any

from mini_sedric.s3_integration import S3Interface
from mini_sedric.s3_integration.exceptions import S3BucketNotFoundException

from .exceptions import JobNotFoundException
from .interface import TranscribeWorkerInterface


class LocalTranscribeWorker(TranscribeWorkerInterface):
    """Local implementation of AWS Transcribe Worker"""

    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, str]] = {}

    def start_job(
        self, job_name: str, s3_file_uri: str, s3_client: S3Interface
    ) -> dict[str, Any]:
        if not s3_client.check(s3_file_uri):
            raise S3BucketNotFoundException("Bucket not found!")
        return {"Job Status": "COMPLETED"}

    def get_transcription_job_status(self, job_name: str) -> str:
        if job_name in self.jobs:
            return self.jobs[job_name]["Job Status"]
        raise JobNotFoundException("Job not found!")

    def close(self) -> None:
        return


class AWSTranscribeWorker(TranscribeWorkerInterface):
    """AWS-connected transcription worker implementation"""

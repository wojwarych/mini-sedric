"""Module that implements interface for TranscribeWorkerInterface"""

from typing import Any

import boto3
import botocore

from mini_sedric.config import settings
from mini_sedric.s3_integration import S3Interface
from mini_sedric.s3_integration.exceptions import S3BucketNotFoundException

from .exceptions import JobNotFoundException, TranscribeWorkerError
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
        self.jobs[job_name] = {"Job Status": "COMPLETED"}
        return self.jobs[job_name]

    def get_transcription_job_status(self, job_name: str) -> str:
        if job_name in self.jobs:
            return self.jobs[job_name]["Job Status"]
        raise JobNotFoundException("Job not found!")

    def get_transcript_uri(self, job_name: str) -> str:
        if job_name in self.jobs:
            return (
                f"http://s3.localhost.localstack.cloud:4566/test-bucket/{job_name}.json"
            )
        raise TranscribeWorkerError(
            f"Couldn't get transcription URI for job: {job_name}"
        )

    def delete_job(self, job_name: str) -> None:
        self.jobs.pop(job_name, None)

    def close(self) -> None:
        return


class AWSTranscribeWorker(TranscribeWorkerInterface):
    """AWS-connected transcription worker implementation"""

    def __init__(self) -> None:
        self.transcribe_client = boto3.client(
            "transcribe",
            endpoint_url=settings.aws_endpoint,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.region_name,
        )

    def start_job(
        self, job_name: str, s3_file_uri: str, s3_client: S3Interface
    ) -> dict[str, Any]:
        if not s3_client.check(s3_file_uri):
            raise S3BucketNotFoundException("Bucket not found!")
        return self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_file_uri},
            MediaFormat="mp3",
            LanguageCode="en-US",
        )

    def get_transcription_job_status(self, job_name: str) -> str:
        try:
            return self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )["TranscriptionJob"]["TranscriptionJobStatus"]
        except Exception as exc:
            print(exc)
            raise JobNotFoundException("Job not found!") from exc

    def get_transcript_uri(self, job_name: str) -> str:
        try:
            return self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        except botocore.exceptions.ClientError as exc:
            print(exc)
            raise TranscribeWorkerError(
                f"Couldn't get transcription URI for job: {job_name}"
            ) from exc

    def delete_job(self, job_name: str) -> None:
        try:
            return self.transcribe_client.delete_transcription_job(
                TranscriptionJobName=job_name
            )
        except botocore.exceptions.ClientError as exc:
            print(exc)
            raise TranscribeWorkerError(
                f"Couldn't delete job with name: {job_name}"
            ) from exc

    def close(self) -> None:
        self.transcribe_client.close()

"""Module for the abstract interface of connection with Transcription service"""

from abc import ABC, abstractmethod
from typing import Any

from mini_sedric.s3_integration import S3Interface


class TranscribeWorkerInterface(ABC):
    """Interface class for defining job running transcription of audio file to text"""

    @abstractmethod
    def start_job(
        self, job_name: str, s3_file_uri: str, s3_client: S3Interface
    ) -> dict[str, Any]:
        """
        Method starting transcription job

        Args:
            job_name (str): name of the job
            s3_file_uri (str): name of the object from S3 to run transcription
            s3_client (S3Interface): S3 client to check existence of the object

        Returns:
            dict[str, Any]: dictionary containing data about the job
        """

    @abstractmethod
    def get_transcription_job_status(self, job_name: str) -> str:
        """Check current status of the transcription job

        Args:
            job_name (str): name of the job to check

        Returns:
            str: string marking current status of the job
        """

    @abstractmethod
    def close(self) -> None:
        """
        Closes properly connection with TranscribeService client

        Returns:
            None
        """

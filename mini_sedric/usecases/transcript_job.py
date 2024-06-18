# pylint: disable=W0511
"""
Module running extraction of insights from transcribed mp3 file, taken from S3 bucket
file with TranscriberWorkerInterface
"""

import json
import time

from mini_sedric.s3_integration import S3Interface
from mini_sedric.transcribe_service import (
    TranscribeWorkerError,
    TranscribeWorkerInterface,
)

from .exceptions import JobServiceError
from .extractor import InsightsExtractor


def create_insights(  # pylint: disable=too-many-arguments
    job_name: str,
    s3_file_uri: str,
    trackers: list[str],
    s3_interface: S3Interface,
    transcribe_service: TranscribeWorkerInterface,
    extractor: InsightsExtractor,
) -> None:
    """
    Creates insights data about each tracker from the request.

    Args:
        job_name (str): name of transcription job for which bucket should be checked
        s3_file_uri (str): bucket where .mp3 audio file resides
        trackers (list[str]): list of phrases for which insights should be done
        transcribe_service (TranscribeWorkerInterface): transcriber interface
        s3_interface (S3Interface): S3 bucket interface

    Returns:
        str
    """
    transcribe_service.start_job(job_name, s3_file_uri, s3_interface)

    _wait_for_the_job_to_complete(job_name, transcribe_service)

    transcript = extractor.get_transcript_from_bucket(job_name)

    ret = {"insights": list(extractor.find_trackers(trackers, transcript))}

    byte_data = json.dumps(ret).encode("utf-8")

    s3_interface.add_to_bucket(s3_file_uri, f"{job_name}.insights", byte_data)

    try:
        # jobs should be rather kept as long possible for log reasons
        # the TranscriberWorkerInterface.start_job() should have better naming
        # mechanism for transcription jobs
        transcribe_service.delete_job(job_name)
    except TranscribeWorkerError as e:
        raise JobServiceError("Couldn't delete finished job!") from e


def _wait_for_the_job_to_complete(
    job_name: str, transcribe_service: TranscribeWorkerInterface
) -> None:
    """
    Checks status of the transcription job

    Args:
        job_name (str): name of transcription job for which bucket should be checked
        transcribe_service (TranscribeWorkerInterface): transcriber interface

    Returns:
        None
    """
    # TODO: should be queue service not blocking request
    max_attempts = 30
    while max_attempts > 0:
        max_attempts -= 1
        job_status = transcribe_service.get_transcription_job_status(job_name)
        if job_status == "COMPLETED":
            print("Job done.")
            break
        print(f"Waiting for job {job_name}. Current status is {job_status}")
        time.sleep(5)

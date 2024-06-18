import pytest

from mini_sedric.s3_integration import (
    LocalS3Interface,
    S3BucketNotFoundException,
    S3Interface,
)
from mini_sedric.transcribe_service import (
    JobNotFoundException,
    LocalTranscribeWorker,
    TranscribeWorkerError,
)


@pytest.fixture
def s3_uri() -> str:
    return "s3://some-bucket/value.mp3"


@pytest.fixture
def local_s3_interface(s3_uri: str) -> LocalS3Interface:
    return LocalS3Interface([s3_uri])


@pytest.fixture
def job_name() -> str:
    return "random-job"


@pytest.fixture
def transcribe_worker_with_job(
    s3_uri: str, local_s3_interface: LocalS3Interface, job_name: str
) -> LocalTranscribeWorker:
    local_transcribe_worker = LocalTranscribeWorker()
    local_transcribe_worker.start_job(job_name, s3_uri, local_s3_interface)

    return local_transcribe_worker


def test_start_job_returns_dict_with_status_on_successful_start(
    local_s3_interface: S3Interface, s3_uri: str
) -> None:
    local_transcribe_worker = LocalTranscribeWorker()

    ret = local_transcribe_worker.start_job("some-job", s3_uri, local_s3_interface)
    assert ret["Job Status"] == "COMPLETED"


def test_start_job_raises_s3_bucket_not_found_on_non_existing_resource(
    local_s3_interface: S3Interface, s3_uri: str
) -> None:
    local_transcribe_worker = LocalTranscribeWorker()

    with pytest.raises(S3BucketNotFoundException):
        local_transcribe_worker.start_job(
            "some-job", "s3://non-existent/bucket.mp3", local_s3_interface
        )


def test_get_transcription_job_status_returns_status_on_existing_job(
    transcribe_worker_with_job: LocalTranscribeWorker, job_name: str
) -> None:
    assert (
        transcribe_worker_with_job.get_transcription_job_status(job_name) == "COMPLETED"
    )


def test_get_transcription_job_status_raises_job_not_found_exception_on_no_job(
    local_s3_interface: S3Interface, s3_uri: str
) -> None:
    local_transcribe_worker = LocalTranscribeWorker()

    with pytest.raises(JobNotFoundException):
        local_transcribe_worker.get_transcription_job_status("some-job")


def test_get_transcript_uri_returns_json_bucket_on_existing_job(
    transcribe_worker_with_job: LocalTranscribeWorker, job_name: str
) -> None:
    assert (
        transcribe_worker_with_job.get_transcript_uri(job_name)
        == f"http://s3.localhost.localstack.cloud:4566/test-bucket/{job_name}.json"
    )


def test_get_transcript_uri_raises_transcribe_worker_error_on_no_job(
    job_name: str,
) -> None:
    local_transcribe_worker = LocalTranscribeWorker()

    with pytest.raises(TranscribeWorkerError):
        local_transcribe_worker.get_transcript_uri(job_name)


def test_delete_job_removes_job(
    transcribe_worker_with_job: LocalTranscribeWorker, job_name: str
) -> None:
    transcribe_worker_with_job.delete_job(job_name)
    assert job_name not in transcribe_worker_with_job.jobs

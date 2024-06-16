import pytest

from mini_sedric.s3_integration import (
    LocalS3Interface,
    S3BucketNotFoundException,
    S3Interface,
)
from mini_sedric.transcribe_service import LocalTranscribeWorker


@pytest.fixture
def s3_uri() -> str:
    return "s3://some-bucket/value.mp3"


@pytest.fixture
def local_s3_interface(s3_uri: str) -> LocalS3Interface:
    return LocalS3Interface([s3_uri])


def test_start_job_returns_dict_with_status_on_successfulStart(
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

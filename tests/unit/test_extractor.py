import pytest

from mini_sedric.s3_integration import LocalS3Interface
from mini_sedric.transcribe_service import LocalTranscribeWorker
from mini_sedric.usecases.extractor import InsightsExtractor


@pytest.fixture
def job_name() -> str:
    return "some-job"


@pytest.fixture
def s3_file_uri(job_name: str) -> str:
    return f"s3://test-bucket/{job_name}"


@pytest.fixture
def s3_client(s3_file_uri: str) -> LocalS3Interface:
    return LocalS3Interface([s3_file_uri])


@pytest.fixture
def transcribe_worker_with_job(
    job_name: str, s3_file_uri: str, s3_client: LocalS3Interface
) -> LocalTranscribeWorker:
    transcriber = LocalTranscribeWorker()
    transcriber.start_job(job_name, s3_file_uri, s3_client)
    return transcriber


def test_insights_extractor_get_transcript_from_bucket(
    job_name: str,
    transcribe_worker_with_job: LocalTranscribeWorker,
    s3_client: LocalS3Interface,
) -> None:
    extractor = InsightsExtractor(transcribe_worker_with_job, s3_client)

    transcript = extractor.get_transcript_from_bucket("some-job")

    assert transcript
    assert isinstance(transcript, str)


def test_insights_extractor_finds_trackers(
    job_name: str,
    transcribe_worker_with_job: LocalTranscribeWorker,
    s3_client: LocalS3Interface,
) -> None:
    extractor = InsightsExtractor(transcribe_worker_with_job, s3_client)

    transcript = extractor.get_transcript_from_bucket("some-job")

    ret = list(extractor.find_trackers(["Great!"], transcript))
    assert ret
    assert isinstance(ret[0], dict)

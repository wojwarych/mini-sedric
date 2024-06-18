from collections.abc import AsyncIterator

import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture

from mini_sedric.main import app
from mini_sedric.models import InteractionInput
from mini_sedric.s3_integration import (
    LocalS3Interface,
    S3BucketNotFoundException,
    S3Interface,
    connect_to_s3,
)
from mini_sedric.transcribe_service import (
    LocalTranscribeWorker,
    TranscribeWorkerInterface,
    connect_to_transcribe_service,
)

pytestmark = pytest.mark.anyio


def s3_uri_string() -> str:
    return "s3://some/basic/volume.mp3"


def job_name() -> str:
    return "volume.mp3"


async def connect_to_s3_override() -> AsyncIterator[S3Interface]:
    s3_conn = LocalS3Interface([s3_uri_string()])
    try:
        yield s3_conn
    finally:
        s3_conn.close()


async def connect_to_transcribe_service_override() -> (
    AsyncIterator[TranscribeWorkerInterface]
):
    service = LocalTranscribeWorker()
    # for testing resons just to inject some job name
    # should be improved with proper injection of data
    service.jobs[job_name()] = {"Job Status": "IN_PROGRESS"}
    try:
        yield service
    finally:
        service.close()


app.dependency_overrides[connect_to_s3] = connect_to_s3_override
app.dependency_overrides[connect_to_transcribe_service] = (
    connect_to_transcribe_service_override
)


@pytest.fixture
def interaction_input() -> dict[str, str | list[str]]:
    return InteractionInput(
        interaction_url="s3://some/basic/volume.mp3",
        trackers=["val1", "val2", "val3"],
    ).model_dump()


async def test_root() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Hello, MiniSedric!"


async def test_insights_returns_200_on_successful_transcribe_job(
    interaction_input: dict[str, str | list[str]], mocker: MockerFixture
) -> None:
    mocked_insights = mocker.patch("mini_sedric.main.create_insights")
    mocked_insights.return_value = {
        "insights": [
            {
                "sentence_index": 4,
                "start_word_index": 2,
                "end_word_index": 5,
                "tracker_value": interaction_input["trackers"][0],
                "transcribe_value": "some transcription",
            }
        ]
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/insights", json=interaction_input)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()
    assert (
        response.json()["insights"][0]["tracker_value"]
        == interaction_input["trackers"][0]
    )


async def test_insights_returns_404_on_no_bucket_data(
    interaction_input: dict[str, str | list[str]], mocker: MockerFixture
) -> None:
    mocked_insights = mocker.patch("mini_sedric.main.create_insights")
    mocked_insights.side_effect = S3BucketNotFoundException("Not found!")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/insights", json=interaction_input)
    assert response.status_code == status.HTTP_404_NOT_FOUND

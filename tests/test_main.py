from collections.abc import AsyncIterator

import pytest
from pytest_mock import MockerFixture
from fastapi import status
from httpx import AsyncClient

from mini_sedric.main import app
from mini_sedric.models import InteractionInput
from mini_sedric.usecases import S3BucketNotFoundException
from mini_sedric.s3_integration import LocalS3Interface, S3Interface, connect_to_s3


pytestmark = pytest.mark.anyio


def s3_uri_string() -> str:
    return "s3://some/basic/volume.mp3"


async def connect_to_s3_override() -> AsyncIterator[S3Interface]:
    s3_conn = LocalS3Interface([s3_uri_string()])
    try:
        yield s3_conn
    finally:
        s3_conn.close()


app.dependency_overrides[connect_to_s3] = connect_to_s3_override


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


async def test_insights_returns_200_on_existing_bucket(
    interaction_input: dict[str, str | list[str]]
) -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/insights", json=interaction_input)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "insights": [
            {
                "sentence_index": 4,
                "start_word_index": 5,
                "end_word_index": 7,
                "tracker_value": "How aree you doing today, Sir?",
                "transcribe_value": "How are you feeling?",
            }
        ]
    }


async def test_insights_returns_404_on_no_bucket_data(
    interaction_input: dict[str, str | list[str]], mocker: MockerFixture
) -> None:
    mocked_get_s3_bucket = mocker.patch("mini_sedric.main.get_s3_bucket")
    mocked_get_s3_bucket.side_effect = S3BucketNotFoundException
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/insights", json=interaction_input)
    assert response.status_code == status.HTTP_404_NOT_FOUND

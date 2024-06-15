import pytest

from mini_sedric.s3_integration import LocalS3Interface, S3Interface
from mini_sedric.usecases import S3BucketNotFoundException, get_s3_bucket

pytestmark = pytest.mark.anyio


@pytest.fixture
def s3_interface_no_data() -> S3Interface:
    return LocalS3Interface()


@pytest.fixture
def s3_bucket_uri() -> str:
    return "s3://some/valid/sample.mp3"


@pytest.fixture
def s3_interface_with_data(s3_bucket_uri: str) -> S3Interface:
    return LocalS3Interface([s3_bucket_uri])


async def test_get_s3_bucket_returns_false_on_no_bucket(
    s3_interface_no_data: S3Interface,
) -> None:
    with pytest.raises(S3BucketNotFoundException):
        await get_s3_bucket(s3_interface_no_data, "random string")


async def test_get_s3_bucket_returns_bucket_content(
    s3_interface_with_data: S3Interface, s3_bucket_uri: str
) -> None:
    assert await get_s3_bucket(s3_interface_with_data, s3_bucket_uri)

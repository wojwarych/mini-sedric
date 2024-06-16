"""Module for dependency injection of S3Interface"""

from collections.abc import AsyncIterator

from mini_sedric.config import settings

from .clients import LocalS3Interface, S3AWSInterface
from .interface import S3Interface


async def connect_to_s3() -> AsyncIterator[S3Interface]:
    """Creates connection dependency injection of S3Interface

    Yields:
        AsyncIterator[S3Interface]: Instance of the interface
    """
    s3_conn = (
        LocalS3Interface()
        if settings.env_for_dynaconf == "testing"
        else S3AWSInterface()
    )
    try:
        yield s3_conn
    finally:
        s3_conn.close()

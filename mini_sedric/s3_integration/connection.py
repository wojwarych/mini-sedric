"""Module for dependency injection of S3Interface"""

from collections.abc import AsyncIterator

from .clients import LocalS3Interface
from .interface import S3Interface


async def connect_to_s3() -> AsyncIterator[S3Interface]:
    """Creates connection dependency injection of S3Interface"""
    s3_conn = LocalS3Interface()
    try:
        yield s3_conn
    finally:
        s3_conn.close()

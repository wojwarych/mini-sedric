"""Module for implementations of S3Interface ABC class"""

from .interface import S3Interface


class LocalS3Interface(S3Interface):
    """Local implementation of S3Interface class. For test/local usage only."""

    def __init__(self, data: list[str] | None = None) -> None:
        self.data = [] if not data else data

    def check(self, uri: str) -> bool:
        return uri in self.data

    def close(self) -> None:
        return

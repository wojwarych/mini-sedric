"""Interface for creating connection with AWS S3 Bucket"""

from abc import ABC, abstractmethod
from typing import Any


class S3Interface(ABC):
    """
    S3Interface is an abstract class which interface should be implemented by
    inherited class in order to create proper connection with S3 service
    """

    @abstractmethod
    def check(self, uri: str) -> bool:
        """
        Method which checks if bucket with such URI exists

        Args:
            uri (str): URI of S3 bucket to check

        Returns:
            bool: True if object with such URI exists in the S3
        """

    @abstractmethod
    def get_object(self, bucket_name: str, object_key: str) -> dict[str, Any]:
        """
        Gets the object from the S3 bucket

        Args:
            bucket_name (str): name of the bucket
            object_key (str): object's key which has to be fetched

        Returns:
            dict[str, Any]: response containing data and metadata about the object
        """

    @abstractmethod
    def close(self) -> None:
        """
        Closes properly connection with S3 service

        Returns:
            None
        """

    @abstractmethod
    def add_to_bucket(
        self, s3_uri: str, object_key: str, data: bytes
    ) -> dict[str, Any]:
        """
        Adds insights data as a JSON bucket

        Args:
            s3_uri (str): URI of bucket to which data should be added
            object_key (str): object name to be added
            data (bytes): data which should be send to bucket

        Returns:
            None
        """

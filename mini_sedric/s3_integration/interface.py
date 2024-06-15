"""Interface for creating connection with AWS S3 Bucket"""

from abc import ABC, abstractmethod


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
    def close(self) -> None:
        """
        Closes properly connection with S3 service

        Returns:
            None
        """

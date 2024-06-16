"""Module for implementations of S3Interface ABC class"""

import boto3
import botocore

from mini_sedric.config import settings

from .interface import S3Interface


class LocalS3Interface(S3Interface):
    """Local implementation of S3Interface class. For test/local usage only."""

    def __init__(self, data: list[str] | None = None) -> None:
        self.data = [] if not data else data

    def check(self, uri: str) -> bool:
        return uri in self.data

    def close(self) -> None:
        return


class S3AWSInterface(S3Interface):
    """Class for communicating with S3 interface of AWS"""

    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.region_name,
        )

    def check(self, uri: str) -> bool:
        try:
            sanitized_uri = uri.lstrip("s3://").rsplit("/")
            self.s3_client.head_object(Bucket=sanitized_uri[0], Key=sanitized_uri[1])
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("Object not found!")
            else:
                print("Unexpected error!")
                print(e.response)
            return False
        return True

    def close(self) -> None:
        self.s3_client.close()

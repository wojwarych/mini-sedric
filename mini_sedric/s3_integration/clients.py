# pylint: disable=C0301
"""Module for implementations of S3Interface ABC class"""

import json
from io import BytesIO
from typing import Any
from urllib.parse import urlparse

import boto3
import botocore
from botocore.response import StreamingBody

from mini_sedric.config import settings

from .interface import S3Interface


class LocalS3Interface(S3Interface):
    """Local implementation of S3Interface class. For test/local usage only."""

    def __init__(self, data: list[str] | None = None) -> None:
        self.data = [] if not data else data

    def check(self, uri: str) -> bool:
        return uri in self.data

    def get_object(self, bucket_name: str, object_key: str) -> dict[str, Any]:
        body_json = {
            "results": {
                "transcripts": [
                    {
                        "transcript": "Transcription text, and? That has multiple sentences. Great!"  # noqa: E501
                    }
                ]
            }
        }

        encoded = json.dumps(body_json).encode("utf-8")

        body = StreamingBody(BytesIO(encoded), len(encoded))
        return {"Body": body}

    def add_to_bucket(
        self, s3_uri: str, object_key: str, data: bytes
    ) -> dict[str, Any]:
        return {}

    def close(self) -> None:
        return


class S3AWSInterface(S3Interface):
    """Class for communicating with S3 interface of AWS"""

    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3_aws_endpoint,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.region_name,
        )

    def check(self, uri: str) -> bool:
        try:
            parsed_s3_uri = urlparse(uri)
            self.s3_client.head_object(
                Bucket=parsed_s3_uri.netloc,
                Key=parsed_s3_uri.path.lstrip("/"),
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("Object not found!")
            else:
                print("Unexpected error!")
                print(e.response)
            return False
        return True

    def get_object(self, bucket_name: str, object_key: str) -> dict[str, Any]:
        try:
            ret = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("Object not found!")
            else:
                print("Unexpected error!")
                print(e.response)
            return {}
        return ret

    def add_to_bucket(
        self, s3_uri: str, object_key: str, data: bytes
    ) -> dict[str, Any]:
        try:
            parsed_bucket_uri = urlparse(s3_uri)
            ret = self.s3_client.put_object(
                Body=data, Bucket=parsed_bucket_uri.netloc, Key=object_key
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("Object not found!")
            else:
                print("Unexpected error!")
                print(e.response)
        return ret

    def close(self) -> None:
        self.s3_client.close()

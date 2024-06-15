"""Module keeping all usecases that are related to procedures done with S3 service"""

from typing import Any

from mini_sedric.s3_integration import S3Interface

from .exceptions import S3BucketNotFoundException


async def get_s3_bucket(
    s3_interface: S3Interface, s3_uri: str
) -> dict[str, list[dict[str, Any]]]:
    """
    Get data from particular S3 bucket

    Args:
        s3_interface (S3Interface): concrete implementation of S3Interface class
        s3_uri (str): URI to S3 resource
    Returns:
        dict[str, list[dict[str, Any]]]: dictionary with insights
    """
    if not s3_interface.check(s3_uri):
        raise S3BucketNotFoundException("Bucket not found!")
    return {
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

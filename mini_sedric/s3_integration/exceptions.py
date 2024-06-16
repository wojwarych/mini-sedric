"""Module keeping all exceptions related to S3 service"""


class S3BucketNotFoundException(Exception):
    """Exception raised when particular S3 object is not found"""

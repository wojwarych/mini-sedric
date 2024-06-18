"""Module keeping all exceptions related to Transcribe service"""


class JobNotFoundException(Exception):
    """Exception raised when job in transcribe service is not found"""


class TranscribeWorkerError(Exception):
    """General purpose error for TranscribeWorker interface"""

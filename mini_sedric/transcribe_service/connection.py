"""Module for dependency injection of TranscribeWorkerInterface"""

from collections.abc import AsyncIterator

from .client import LocalTranscribeWorker
from .interface import TranscribeWorkerInterface


async def connect_to_transcribe_service() -> AsyncIterator[TranscribeWorkerInterface]:
    """Creates connection dependency injection of TranscribeWorkerInterface

    Yields:
        AsyncIterator[TranscribeWorkerInterface]: Instance of the interface
    """
    transcribe_worker = LocalTranscribeWorker()
    try:
        yield transcribe_worker
    finally:
        transcribe_worker.close()

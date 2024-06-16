# pylint: disable=W0707
"""Main entrypoint for MiniSedric app"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from .models import InteractionInput
from .s3_integration import S3BucketNotFoundException, S3Interface, connect_to_s3
from .transcribe_service import TranscribeWorkerInterface, connect_to_transcribe_service

app = FastAPI()


@app.get("/")
async def hello_world():
    """Basic hello world entrypoint for app"""
    return "Hello, MiniSedric!"


@app.post("/insights")
async def insights(
    interaction_input: InteractionInput,
    s3_connection: Annotated[S3Interface, Depends(connect_to_s3)],
    transcribe_service: Annotated[
        TranscribeWorkerInterface, Depends(connect_to_transcribe_service)
    ],
):
    """Endpoint for starting transcription job"""
    try:
        ret = transcribe_service.start_job(
            interaction_input.interaction_url,
            interaction_input.interaction_url,
            s3_connection,
        )
        return ret
    except S3BucketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

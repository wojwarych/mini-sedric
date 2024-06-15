# pylint: disable=W0707
"""Main entrypoint for MiniSedric app"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from .models import InteractionInput
from .s3_integration import S3Interface, connect_to_s3
from .usecases import S3BucketNotFoundException, get_s3_bucket

app = FastAPI()


@app.get("/")
async def hello_world():
    """Basic hello world entrypoint for app"""
    return "Hello, MiniSedric!"


@app.post("/insights")
async def insights(
    interaction_input: InteractionInput,
    s3_connection: Annotated[S3Interface, Depends(connect_to_s3)],
):
    """Endpoint for extracting data from transcription"""
    try:
        ret = await get_s3_bucket(s3_connection, interaction_input.interaction_url)
        return ret
    except S3BucketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

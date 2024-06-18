# pylint: disable=W0707
"""Main entrypoint for MiniSedric app"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from .models import InsightsResponse, InteractionInput
from .s3_integration import S3BucketNotFoundException, S3Interface, connect_to_s3
from .transcribe_service import TranscribeWorkerInterface, connect_to_transcribe_service
from .usecases.transcript_job import InsightsExtractor, JobServiceError, create_insights

app = FastAPI()


@app.get("/")
async def hello_world():
    """Basic hello world entrypoint for app"""
    return "Hello, MiniSedric!"


@app.post("/insights", response_model=InsightsResponse)
async def insights(
    interaction_input: InteractionInput,
    s3_connection: Annotated[S3Interface, Depends(connect_to_s3)],
    transcribe_service: Annotated[
        TranscribeWorkerInterface, Depends(connect_to_transcribe_service)
    ],
):
    """Endpoint for getting insights from transcribed mp3 file"""
    try:
        extractor = InsightsExtractor(transcribe_service, s3_connection)
        job_name = interaction_input.interaction_url.split("/")[-1]
        return create_insights(
            job_name,
            interaction_input.interaction_url,
            interaction_input.trackers,
            s3_connection,
            transcribe_service,
            extractor,
        )
    except S3BucketNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except JobServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

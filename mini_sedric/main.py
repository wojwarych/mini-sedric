# pylint: disable=W0707
"""Main entrypoint for MiniSedric app"""

import json
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI

from .config import settings
from .models import InsightsGetResponse, InsightsPostResponse, InteractionInput
from .s3_integration import S3Interface, connect_to_s3
from .transcribe_service import TranscribeWorkerInterface, connect_to_transcribe_service
from .usecases.transcript_job import InsightsExtractor, create_insights

app = FastAPI()


@app.get("/")
async def hello_world():
    """Basic hello world entrypoint for app"""
    return "Hello, MiniSedric!"


@app.post("/insights", status_code=201, response_model=InsightsPostResponse)
async def post_insights(
    interaction_input: InteractionInput,
    s3_connection: Annotated[S3Interface, Depends(connect_to_s3)],
    transcribe_service: Annotated[
        TranscribeWorkerInterface, Depends(connect_to_transcribe_service)
    ],
    background_tasks: BackgroundTasks,
):
    """Endpoint for getting insights from transcribed mp3 file"""
    extractor = InsightsExtractor(transcribe_service, s3_connection)
    job_name = interaction_input.interaction_url.split("/")[-1] + ".json"
    background_tasks.add_task(
        create_insights,
        job_name=job_name,
        s3_file_uri=interaction_input.interaction_url,
        trackers=interaction_input.trackers,
        s3_interface=s3_connection,
        transcribe_service=transcribe_service,
        extractor=extractor,
    )
    return {"name": f"{job_name}.insights"}


@app.get("/insights/{job_name}", response_model=InsightsGetResponse)
async def get_insights(
    job_name: str,
    s3_connection: Annotated[S3Interface, Depends(connect_to_s3)],
):
    """
    GET request for fetching tracker insights from previously called transcription job
    """
    # should be more flexible when it comes to name of a bucket
    obj = s3_connection.get_object(settings.s3_bucket_name, job_name)
    if obj:
        return json.loads(obj["Body"].read().decode("utf-8"))
    return {"insights": []}

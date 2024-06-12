"""Main entrypoint for MiniSedric app"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world():
    """Basic hello world entrypoint for app"""
    return "Hello, MiniSedric!"

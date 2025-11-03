import os
from fastapi import FastAPI
from src.batch_classify_from_bigquery import main as run_batch_job
import asyncio

app = FastAPI()

@app.post("/")
async def run_job():
    """
    Endpoint to trigger the batch classification job.
    """
    try:
        print("Job triggered by Cloud Scheduler.")
        await run_batch_job()
        print("Job finished successfully.")
        return {"status": "OK"}
    except Exception as e:
        print(f"An error occurred during job execution: {e}")
        return {"status": "Error"}, 500

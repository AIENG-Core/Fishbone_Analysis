from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from ml.inference import analyze

app = FastAPI(title="Fishbone RCA AI")

class Request(BaseModel):
    incident: str

@app.post("/fishbone")
async def generate(req: Request):
    return await analyze(req.incident)

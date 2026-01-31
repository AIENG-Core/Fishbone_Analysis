import ollama
import asyncio
from config import LLM_MODEL, MAX_LLM_CONCURRENCY

_semaphore = asyncio.Semaphore(MAX_LLM_CONCURRENCY)

async def generate_description(incident, category, cause):
    prompt = f"""
You are assisting in an industrial safety Root Cause Analysis.

Incident:
{incident}

Category: {category}
Cause: {cause}

Write a short, neutral, factual explanation of how this cause contributed
to the incident.

Rules:
- No blame
- No assumptions
- No new causes
- 2 to 3 sentences max
"""

    async with _semaphore:
        response = ollama.generate(
            model=LLM_MODEL,
            prompt=prompt
        )
        return response["response"].strip()

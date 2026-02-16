# 
# description_generator.py
import ollama
import asyncio
from config import LLM_MODEL

async def generate_descriptions_batch(incident, category, causes):

    causes_text = "\n".join(f"- {c}" for c in causes)

    prompt = f"""
You are assisting in an industrial safety Root Cause Analysis.

Incident:
{incident}

Category: {category}

Causes:
{causes_text}

Write a short neutral description (1 to 2 sentences)
for EACH cause in order.

Rules:
- No blame
- No assumptions
- No new causes
- Output as numbered list
"""

    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt
    )

    text = response["response"].strip()

    # Split numbered output
    descriptions = [
        line.split(".", 1)[-1].strip()
        for line in text.split("\n")
        if line.strip()
    ]

    return descriptions

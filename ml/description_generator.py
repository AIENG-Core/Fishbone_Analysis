import ollama
from config import LLM_MODEL


async def generate_descriptions_batch(incident, causes):

    if not causes:
        return {}

    causes_text = "\n".join(
        f"{i+1}. {c['category']} — {c['cause']}"
        for i, c in enumerate(causes)
    )

    prompt = f"""
You are assisting in an industrial Root Cause Analysis.

Incident description:
{incident}

Possible root causes:

{causes_text}

Task:
Explain briefly how each cause might contribute to the incident.

Rules:
- Use incident information if available
- If the cause is not supported say:
"Cause not supported by the incident description."
- Keep explanation to ONE sentence
- Return numbered list
"""

    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"num_predict": 200}
    )

    text = response["response"]

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    descriptions = {}

    for i, line in enumerate(lines):

        if i >= len(causes):
            break

        if "." in line:
            desc = line.split(".", 1)[1].strip()
        else:
            desc = line

        key = f"{causes[i]['category']}::{causes[i]['cause']}"

        descriptions[key] = desc

    return descriptions
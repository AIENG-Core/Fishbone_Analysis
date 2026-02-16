import ollama
from config import LLM_MODEL


async def generate_descriptions_batch(incident, category, causes):

    # 🔴 Safety check
    if isinstance(causes, str):
        causes = [causes]

    if not causes:
        return []

    causes_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(causes))

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
- Return numbered list only
"""

    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"num_predict": 150}
    )

    text = response["response"].strip()

    # Parse numbered output safely
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    descriptions = []
    for line in lines:
        if "." in line:
            descriptions.append(line.split(".", 1)[1].strip())
        else:
            descriptions.append(line)

    # Ensure same length as causes
    while len(descriptions) < len(causes):
        descriptions.append("")

    return descriptions[:len(causes)]

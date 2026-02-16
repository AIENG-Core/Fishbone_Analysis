import asyncio
from sklearn.metrics.pairwise import cosine_similarity
from models.embeddings import EmbeddingModel
from models.relevance_model import RelevanceModel
from ml.constants import FISHBONE, THRESHOLDS
from ml.description_generator import generate_descriptions_batch

embedder = EmbeddingModel()
relevance = RelevanceModel()

async def analyze(incident_text):
    emb = embedder.encode(incident_text)
    result = {}

    for category, causes in FISHBONE.items():
        selected = []

        for cause in causes:
            sim = cosine_similarity(
                [emb], [embedder.encode(cause)]
            )[0][0]

            score = relevance.score(sim, cause)
            if score >= THRESHOLDS[category]:
                desc = await generate_descriptions_batch(
                    incident_text, category, cause
                )
                selected.append({
                    "cause": cause,
                    "description": desc
                })

        if not selected:
            cause = causes[0]
            desc = await generate_descriptions_batch(
                incident_text, category, cause
            )
            for cause, desc in zip(cause, desc):
                selected.append({
                    "cause": cause,
                    "description": desc
    })
            selected.append({"cause": cause, "description": desc})

        result[category] = selected

    return result
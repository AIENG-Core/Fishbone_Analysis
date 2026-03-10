from sklearn.metrics.pairwise import cosine_similarity

from models.embeddings import EmbeddingModel
from models.relevance_model import RelevanceModel

from ml.constants import FISHBONE
from ml.description_generator import generate_descriptions_batch

from config import MAX_CAUSES_PER_CATEGORY, MIN_SIMILARITY_SCORE


embedder = EmbeddingModel()
relevance = RelevanceModel()


# Precompute embeddings
CAUSE_EMBEDDINGS = {}

for category, causes in FISHBONE.items():

    CAUSE_EMBEDDINGS[category] = {}

    for cause in causes:

        text = (
            f"{category} root cause: {cause}. "
            f"This cause can contribute to industrial incidents."
        )

        CAUSE_EMBEDDINGS[category][cause] = embedder.encode(text)


async def analyze(incident_text: str):

    incident_emb = embedder.encode(incident_text)

    selected_causes = []

    for category, causes in FISHBONE.items():

        scores = []

        for cause in causes:

            cause_emb = CAUSE_EMBEDDINGS[category][cause]

            sim = cosine_similarity(
                [incident_emb],
                [cause_emb]
            )[0][0]

            score = relevance.score(sim, cause)

            scores.append((cause, score))

        # sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        # select top causes
        top_causes = scores[:MAX_CAUSES_PER_CATEGORY]

        for cause, score in top_causes:

            if score < MIN_SIMILARITY_SCORE:
                continue

            selected_causes.append({
                "category": category,
                "cause": cause
            })

    # fallback
    if not selected_causes:

        selected_causes.append({
            "category": "Process",
            "cause": "Inadequate Operating Procedure"
        })

    # generate explanations
    descriptions = await generate_descriptions_batch(
        incident_text,
        selected_causes
    )

    result = {cat: [] for cat in FISHBONE}

    for item in selected_causes:

        category = item["category"]
        cause = item["cause"]

        key = f"{category}::{cause}"

        result[category].append({
            "cause": cause,
            "description": descriptions.get(
                key,
                "Cause not supported by the incident description."
            )
        })

    return result
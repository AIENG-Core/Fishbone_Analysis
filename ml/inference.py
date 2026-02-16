import asyncio
from sklearn.metrics.pairwise import cosine_similarity

from models.embeddings import EmbeddingModel
from models.relevance_model import RelevanceModel
from ml.constants import FISHBONE, THRESHOLDS
from ml.description_generator import generate_descriptions_batch


embedder = EmbeddingModel()
relevance = RelevanceModel()


# --------------------------------------------------
# Pre-encode all causes WITH category context
# --------------------------------------------------
CAUSE_EMBEDDINGS = {
    cat: {
        cause: embedder.encode(f"{cat}. Root cause: {cause}")
        for cause in causes
    }
    for cat, causes in FISHBONE.items()
}


# --------------------------------------------------
# Main analysis function
# --------------------------------------------------
async def analyze(incident_text: str):

    incident_emb = embedder.encode(incident_text)
    result = {}

    for category, causes in FISHBONE.items():

        selected_causes = []

        # -------- Similarity filtering --------
        for cause in causes:

            cause_emb = CAUSE_EMBEDDINGS[category][cause]

            sim = cosine_similarity(
                [incident_emb],
                [cause_emb]
            )[0][0]

            score = relevance.score(sim, cause)

            if score >= THRESHOLDS[category]:
                selected_causes.append(cause)

        # -------- Fallback (ensure at least one cause) --------
        if not selected_causes:
            selected_causes = [causes[0]]

        # -------- Batch description generation --------
        descriptions = await generate_descriptions_batch(
            incident_text,
            category,
            selected_causes   # 🔥 LIST (fixes character bug)
        )

        # -------- Combine causes + descriptions --------
        selected = []

        for cause, desc in zip(selected_causes, descriptions):
            selected.append({
                "cause": cause,
                "description": desc
            })

        result[category] = selected

    return result

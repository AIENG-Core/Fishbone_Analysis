# training.py
from models.relevance_model import RelevanceModel

def train(ai_output, final_output):
    model = RelevanceModel()

    accepted = []
    rejected = []

    for cat, ai_items in ai_output.items():
        ai_causes = {i["cause"] for i in ai_items}
        final_causes = set(final_output.get(cat, []))

        # AI suggested
        for cause in ai_causes:
            if cause in final_causes:
                accepted.append(cause)
            else:
                rejected.append(cause)

        # User manually added new causes
        for cause in final_causes:
            if cause not in ai_causes:
                accepted.append(cause)

    model.update(accepted, rejected)

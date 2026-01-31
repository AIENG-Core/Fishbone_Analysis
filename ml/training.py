from models.relevance_model import RelevanceModel

def train(ai_output, final_output):
    model = RelevanceModel()
    accepted, rejected = [], []

    for cat, items in ai_output.items():
        ai_causes = {i["cause"] for i in items}
        final_causes = set(final_output.get(cat, []))

        for c in ai_causes:
            if c in final_causes:
                accepted.append(c)
            else:
                rejected.append(c)

    model.update(accepted, rejected)

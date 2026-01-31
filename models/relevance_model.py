import json
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path("data/relevance.json")

class RelevanceModel:
    def __init__(self):
        self.weights = defaultdict(lambda: 1.0)
        self.load()

    def score(self, similarity, cause):
        return similarity * self.weights[cause]

    def update(self, accepted, rejected):
        for c in accepted:
            self.weights[c] += 0.1

        for c in rejected:
            self.weights[c] = max(0.5, self.weights[c] - 0.1)

        self.save()

    def save(self):
        DATA_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(self.weights, f, indent=2)

    def load(self):
        if DATA_FILE.exists():
            with open(DATA_FILE) as f:
                self.weights.update(json.load(f))

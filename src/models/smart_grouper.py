import json
from typing import List, Dict, Set
from utils.text_processor import TextProcessor
from utils.similarity_analyzer import SimilarityAnalyzer

class SmartGrouper:
    def __init__(self, seed_path: str = "resources/seed_groups.json", threshold: float = 0.85):
        self.text_processor = TextProcessor()
        self.similarity_analyzer = SimilarityAnalyzer(threshold)
        self.seed_groups = self._load_seed(seed_path)

    def _load_seed(self, path: str) -> Dict[str, Set[str]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                return {k: set(v) for k, v in raw.items()}
        except Exception:
            return {}

    def group(self, texts: List[str]) -> Dict[str, Set[str]]:
        matched = set()
        result = {}

        for true_name, variants in self.seed_groups.items():
            group = set()
            for text in texts:
                norm = self.text_processor.normalize(text)
                if norm in map(self.text_processor.normalize, variants):
                    group.add(text)
                    matched.add(text)
            if group:
                result[true_name] = group

        remaining = [t for t in texts if t not in matched]
        sim_groups = self.similarity_analyzer.find_similar_groups(remaining)

        for rep, group in sim_groups.items():
            result[rep] = group

        return result    
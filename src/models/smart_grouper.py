from typing import List, Dict, Set
from utils.text_processor import TextProcessor
from utils.similarity_analyzer import SimilarityAnalyzer

class SmartGrouper:
    def __init__(self, threshold: float = 0.75):
        self.text_processor = TextProcessor()
        self.similarity_analyzer = SimilarityAnalyzer(threshold)

    def group(self, texts: List[str]) -> Dict[str, Set[str]]:
        # Используем только улучшенный анализатор схожести
        return self.similarity_analyzer.find_similar_groups(texts)
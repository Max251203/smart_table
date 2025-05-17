from typing import List, Dict, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from utils.text_processor import TextProcessor

class SimilarityAnalyzer:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), min_df=1)
        self.text_processor = TextProcessor()

    def find_similar_groups(self, texts: List[str]) -> Dict[str, Set[str]]:
        if not texts:
            return {}

        original_texts = list(set(texts))
        processed_texts = [self.text_processor.normalize(t) for t in original_texts]

        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
        clusters = self._cluster_similar_items(1 - similarity_matrix)

        return self._format_results(original_texts, processed_texts, clusters)

    def _cluster_similar_items(self, similarity_matrix: np.ndarray) -> np.ndarray:
        clustering = DBSCAN(eps=1 - self.similarity_threshold, min_samples=1, metric='precomputed')
        return clustering.fit_predict(similarity_matrix)

    def _format_results(self, original_texts: List[str], processed_texts: List[str], clusters: np.ndarray) -> Dict[str, Set[str]]:
        results = {}
        for cluster_id in set(clusters):
            indices = np.where(clusters == cluster_id)[0]
            group = [original_texts[i] for i in indices]
            representative = min(group, key=len)
            results[representative] = set(group)
        return results
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

        # Если только один текст, просто вернем его как группу
        if len(texts) == 1:
            return {texts[0]: {texts[0]}}

        # Убираем дубликаты и пустые значения
        original_texts = [t for t in list(set(texts)) if t and str(t).strip()]
        if not original_texts:
            return {}
            
        # Если после фильтрации остался только один текст
        if len(original_texts) == 1:
            return {original_texts[0]: {original_texts[0]}}
            
        processed_texts = [self.text_processor.normalize(t) for t in original_texts]

        try:
            # Безопасное вычисление TF-IDF матрицы
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
            
            # Убедимся, что значения расстояний корректны (неотрицательны)
            distance_matrix = 1 - similarity_matrix
            
            # Проверим и исправим любые отрицательные значения (из-за погрешностей вычислений)
            distance_matrix = np.clip(distance_matrix, 0, None)
            
            # Теперь используем исправленную матрицу расстояний
            clusters = self._cluster_similar_items(distance_matrix)
        except Exception as e:
            print(f"Ошибка при кластеризации: {e}")
            # В случае ошибки просто группируем каждый текст отдельно
            result = {}
            for text in original_texts:
                result[text] = {text}
            return result

        return self._format_results(original_texts, processed_texts, clusters)

    def _cluster_similar_items(self, distance_matrix: np.ndarray) -> np.ndarray:
        try:
            clustering = DBSCAN(eps=1 - self.similarity_threshold, min_samples=1, metric='precomputed')
            return clustering.fit_predict(distance_matrix)
        except Exception as e:
            print(f"Ошибка DBSCAN: {e}")
            # В случае ошибки просто каждый элемент в свой кластер
            return np.arange(distance_matrix.shape[0], dtype=int)

    def _format_results(self, original_texts: List[str], processed_texts: List[str], clusters: np.ndarray) -> Dict[str, Set[str]]:
        results = {}
        for cluster_id in set(clusters):
            indices = np.where(clusters == cluster_id)[0]
            group = [original_texts[i] for i in indices]
            if not group:
                continue
            representative = min(group, key=len)
            results[representative] = set(group)
        return results     
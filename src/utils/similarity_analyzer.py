from typing import List, Dict, Set, Tuple
import numpy as np
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from utils.text_processor import TextProcessor

class SimilarityAnalyzer:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 3),
            min_df=1
        )
        self.text_processor = TextProcessor()

    def find_similar_groups(self, texts: List[str]) -> Dict[str, Set[str]]:
        """
        Находит группы похожих текстов
        """
        if not texts:
            return {}

        # Предобработка текстов
        processed_texts = [self.text_processor.normalize(text) for text in texts]
        
        # Создание матрицы схожести
        similarity_matrix = self._calculate_similarity_matrix(processed_texts)
        
        # Кластеризация
        clusters = self._cluster_similar_items(similarity_matrix)
        
        return self._format_results(texts, processed_texts, clusters)

    def _calculate_similarity_matrix(self, texts: List[str]) -> np.ndarray:
        """
        Рассчитывает матрицу схожести между текстами
        """
        n = len(texts)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = fuzz.ratio(texts[i], texts[j]) / 100.0
                matrix[i][j] = matrix[j][i] = similarity
        
        return matrix

    def _cluster_similar_items(self, similarity_matrix: np.ndarray) -> np.ndarray:
        """
        Кластеризует элементы на основе матрицы схожести
        """
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=2,
            metric='precomputed'
        )
        return clustering.fit_predict(1 - similarity_matrix)

    def _format_results(self, 
                       original_texts: List[str], 
                       processed_texts: List[str], 
                       clusters: np.ndarray) -> Dict[str, Set[str]]:
        """
        Форматирует результаты кластеризации
        """
        results = {}
        
        # Обработка кластеров
        for cluster_id in set(clusters):
            if cluster_id == -1:  # Пропускаем выбросы
                continue
                
            cluster_indices = np.where(clusters == cluster_id)[0]
            cluster_texts = [original_texts[i] for i in cluster_indices]
            
            # Выбираем самый короткий текст как представителя группы
            representative = min(cluster_texts, key=len)
            results[representative] = set(cluster_texts)

        # Добавляем одиночные элементы
        for i, cluster_id in enumerate(clusters):
            if cluster_id == -1:
                results[original_texts[i]] = {original_texts[i]}

        return results
from typing import Tuple, List, Dict, Optional
import pandas as pd
from utils.text_processor import TextProcessor
from utils.similarity_analyzer import SimilarityAnalyzer

class DataProcessor:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.current_df: Optional[pd.DataFrame] = None
        self.similar_groups: Dict[str, set] = {}

    def load_excel(self, file_path: str) -> Tuple[pd.DataFrame, int]:
        """
        Загружает Excel файл и подготавливает данные
        Returns: (DataFrame, номер колонки с номерами)
        """
        df = pd.read_excel(file_path)
        
        # Находим колонку с номерами
        num_col_index = self.text_processor.find_num_column(df.columns)
        
        if num_col_index is None:
            # Если колонка с номерами не найдена, создаем новую
            df.insert(0, "Excel #", df.index + 2)
            num_col_index = 0

        # Заполняем пустые значения и конвертируем в строки
        df = df.fillna("")
        for col in df.columns:
            df[col] = df[col].astype(str)

        self.current_df = df
        return df, num_col_index

    def analyze_column(self, column_name: str) -> Dict[str, set]:
        """
        Анализирует указанную колонку на наличие похожих значений
        """
        if self.current_df is None:
            return {}

        values = self.current_df[column_name].unique().tolist()
        self.similar_groups = self.similarity_analyzer.find_similar_groups(values)
        return self.similar_groups

    def filter_data(self, column: str, filter_text: str) -> pd.DataFrame:
        """
        Фильтрует данные по указанной колонке и тексту
        """
        if not self.current_df is None:
            return pd.DataFrame()

        if not filter_text:
            return self.current_df.copy()

        normalized_filter = self.text_processor.normalize(filter_text)
        
        # Проверяем, есть ли текст среди групп похожих значений
        if self.similar_groups:
            for group_key, group_values in self.similar_groups.items():
                if self.text_processor.normalize(group_key) == normalized_filter:
                    mask = self.current_df[column].isin(group_values)
                    return self.current_df[mask].copy()

        # Если группа не найдена, ищем по ключевым словам
        keywords = self.text_processor.extract_keywords(filter_text)
        if keywords:
            mask = self.current_df[column].apply(
                lambda x: all(kw in self.text_processor.normalize(x) for kw in keywords)
            )
            return self.current_df[mask].copy()

        return pd.DataFrame()
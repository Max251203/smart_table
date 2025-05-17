from typing import Tuple, List, Dict, Optional
import pandas as pd
from utils.text_processor import TextProcessor
from utils.similarity_analyzer import SimilarityAnalyzer
from models.smart_grouper import SmartGrouper

class DataProcessor:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.similarity_analyzer = SimilarityAnalyzer()
        self.grouper = SmartGrouper("resources/seed_groups.json")
        self.current_df: Optional[pd.DataFrame] = None
        self.similar_groups: Dict[str, set] = {}

    def load_excel(self, file_path: str) -> Tuple[pd.DataFrame, int]:
        df = pd.read_excel(file_path)
        num_col_index = self.text_processor.find_num_column(df.columns)
        if num_col_index is None:
            df.insert(0, "Excel #", df.index + 2)
            num_col_index = 0
        df = df.fillna("")
        for col in df.columns:
            df[col] = df[col].astype(str)
        self.current_df = df
        return df, num_col_index

    def analyze_column(self, column_name: str) -> Dict[str, set]:
        if self.current_df is None:
            return {}
        values = self.current_df[column_name].unique().tolist()
        self.similar_groups = self.grouper.group(values)
        return self.similar_groups

    def filter_data(self, column: str, filter_text: str) -> pd.DataFrame:
        if self.current_df is None or column not in self.current_df.columns:
            return pd.DataFrame()
        # Поиск по номеру только точное совпадение
        if column.lower().strip() in ["excel #", "№"]:
            return self.current_df[self.current_df[column] == filter_text].copy()
        if not filter_text:
            return self.current_df.copy()
        normalized_filter = self.text_processor.normalize(filter_text)
        if self.similar_groups:
            for group_key, group_values in self.similar_groups.items():
                if self.text_processor.normalize(group_key) == normalized_filter:
                    mask = self.current_df[column].isin(group_values)
                    return self.current_df[mask].copy()
        keywords = self.text_processor.extract_keywords(filter_text)
        if keywords:
            mask = self.current_df[column].apply(
                lambda x: all(kw in self.text_processor.normalize(x) for kw in keywords)
            )
            return self.current_df[mask].copy()
        return pd.DataFrame()
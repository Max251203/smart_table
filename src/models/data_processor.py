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
        self.excel_num_column_added = False  # Флаг, указывающий, добавили ли мы сами колонку Excel #

    def load_excel(self, file_path: str) -> Tuple[pd.DataFrame, int]:
        df = pd.read_excel(file_path)
        num_col_index = self.text_processor.find_num_column(df.columns)
        if num_col_index is None:
            # Добавляем колонку Excel # и устанавливаем флаг
            df.insert(0, "Excel #", df.index + 2)
            num_col_index = 0
            self.excel_num_column_added = True
        else:
            # Колонка с номерами уже есть в файле
            self.excel_num_column_added = False
            
        df = df.fillna("")
        for col in df.columns:
            df[col] = df[col].astype(str)
        self.current_df = df
        return df, num_col_index

    def save_excel(self, file_path: str) -> bool:
        """Сохраняет текущий DataFrame в Excel-файл."""
        if self.current_df is None:
            return False
            
        try:
            df_to_save = self.current_df.copy()
            
            # Удаляем временную колонку Excel #, если она была добавлена нами
            if self.excel_num_column_added and "Excel #" in df_to_save.columns:
                df_to_save = df_to_save.drop(columns=["Excel #"])
            
            # Сохраняем без индекса
            df_to_save.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False

    def add_record(self, record_data: Dict[str, str]) -> None:
        """Добавляет новую запись в текущий DataFrame."""
        if self.current_df is None:
            return
            
        # Создаем новую строку
        new_row = pd.Series(record_data, index=self.current_df.columns)
        
        # Если мы добавляли колонку Excel #, назначаем следующий номер
        if self.excel_num_column_added and "Excel #" in self.current_df.columns:
            try:
                # Находим максимальный текущий номер
                max_num = 0
                for val in self.current_df["Excel #"]:
                    try:
                        num = int(float(val))
                        max_num = max(max_num, num)
                    except:
                        pass
                
                # Следующий номер
                new_row["Excel #"] = str(max_num + 1)
            except:
                # В случае ошибки используем номер len + 2 (как в Excel)
                new_row["Excel #"] = str(len(self.current_df) + 2)
        
        # Добавляем строку в DataFrame
        self.current_df = pd.concat([self.current_df, pd.DataFrame([new_row])], ignore_index=True)

    def analyze_column(self, column_name: str) -> Dict[str, set]:
        """Анализирует колонку и находит группы схожих значений"""
        if self.current_df is None:
            return {}
            
        try:
            # Получаем все уникальные значения колонки
            values = [str(v) for v in self.current_df[column_name].unique() if v and str(v).strip()]
            
            # Группируем схожие значения
            self.similar_groups = self.grouper.group(values)
            
            # Для отладки выведем найденные группы
            print(f"Найдено {len(self.similar_groups)} групп схожих значений в колонке '{column_name}'")
            for key, group in self.similar_groups.items():
                if len(group) > 1:  # Показываем только группы с более чем одним элементом
                    print(f"  Группа '{key}': {group}")
            
            return self.similar_groups
        except Exception as e:
            print(f"Ошибка при анализе колонки '{column_name}': {e}")
            return {}

    def filter_data(self, column: str, filter_text: str) -> pd.DataFrame:
        if self.current_df is None or column not in self.current_df.columns:
            return pd.DataFrame()
        
        if not filter_text:
            return self.current_df.copy()
        
        # Проверяем, является ли колонка числовой
        is_numeric = True
        try:
            # Проверяем, можно ли преобразовать непустые значения в числа
            values = [v for v in self.current_df[column].unique() if str(v).strip()]
            for v in values:
                float(v)
        except ValueError:
            is_numeric = False
        
        # Если колонка числовая, делаем точное числовое сравнение
        if is_numeric:
            try:
                filter_value = float(filter_text)
                # Преобразуем строковые значения в числа для сравнения
                mask = self.current_df[column].apply(
                    lambda x: str(x).strip() and float(str(x).strip()) == filter_value if str(x).strip() else False
                )
                return self.current_df[mask].copy()
            except ValueError:
                # Если не удалось преобразовать filter_text в число, продолжаем обычный поиск
                pass
        
        # Если это не числовая колонка или числовой поиск не дал результатов, используем существующую логику
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
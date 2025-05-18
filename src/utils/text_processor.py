import re
from typing import List, Optional

class TextProcessor:
    @staticmethod
    def normalize(text: str) -> str:
        """
        Нормализует текст: приводит к нижнему регистру, удаляет спецсимволы и лишние пробелы
        """
        text = str(text).lower()
        # Удаляем скобки с их содержимым
        text = re.sub(r'\([^)]*\)', '', text)
        # Оставляем только буквы, цифры и пробелы
        text = re.sub(r'[^а-яёa-z0-9\s]', '', text)
        # Нормализуем пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        # Заменяем 'имени' на 'им'
        text = text.replace('имени', 'им')
        # Удаляем префиксы организаций
        text = re.sub(r'^(уо|го|гуо)\s+', '', text)
        return text

    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Извлекает ключевые слова из текста
        """
        normalized = TextProcessor.normalize(text)
        words = re.findall(r'\w+', normalized)
        return [w for w in words if len(w) >= min_length]

    @staticmethod
    def find_num_column(columns: List[str]) -> Optional[int]:
        """
        Находит индекс колонки с номерами
        """
        num_col_names = ["excel #", "№", "номер строки", "номер", "номер_строки", ""]
        for i, col in enumerate(columns):
            if TextProcessor.normalize(str(col)) in [TextProcessor.normalize(n) for n in num_col_names]:
                return i
        return None     
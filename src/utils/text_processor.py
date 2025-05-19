import re
from typing import List, Optional

class TextProcessor:
    @staticmethod
    def normalize(text: str) -> str:
        """
        Улучшенная нормализация текста для более точного сравнения
        """
        # Приводим к строке и нижнему регистру
        text = str(text).lower()
        
        # Заменяем различные типы кавычек на стандартные
        text = re.sub(r'[«»""\']', '"', text)
        
        # Заменяем различные типы тире на стандартное
        text = re.sub(r'[–—−]', '-', text)
        
        # Заменяем различные типы пробелов на стандартные
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем скобки с их содержимым
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Заменяем числа с # или № на стандартную форму
        text = re.sub(r'[#№](\s*)(\d+)', r'номер \2', text)
        
        # Стандартизируем сокращения
        text = re.sub(r'\bим\.\s+', 'имени ', text)
        text = re.sub(r'\bг\.\s+', 'город ', text)
        text = re.sub(r'\bул\.\s+', 'улица ', text)
        text = re.sub(r'\bпр\.\s+', 'проспект ', text)
        
        # Удаляем пунктуацию и лишние пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Удаляем префиксы организаций
        text = re.sub(r'^(уо|го|гуо|оо)\s+', '', text)
        
        return text

    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Извлекает ключевые слова из текста
        """
        normalized = TextProcessor.normalize(text)
        words = re.findall(r'\b\w+\b', normalized)
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
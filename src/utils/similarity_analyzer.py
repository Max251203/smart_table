from typing import List, Dict, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from utils.text_processor import TextProcessor
import re

class SimilarityAnalyzer:
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold
        self.text_processor = TextProcessor()
        
        # Векторизаторы для разных типов анализа
        self.char_vectorizer = TfidfVectorizer(
            analyzer='char_wb', 
            ngram_range=(2, 4), 
            min_df=1
        )
        
        self.word_vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1
        )
        
        # Предопределенные группы для университетов
        self.university_patterns = {
            r'(?:уо\s+)?(?:[«"])?ггу(?:[»"])?\b|(?:уо\s+)?(?:[«"])?г(?:омельский)?\s*г(?:осударственный)?\s*у(?:ниверситет)?(?:[»"])?\b|(?:университет|унив)\s+(?:им\.?|имени)\s+(?:ф\.?\s*)?скорин': 'Гомельский государственный университет имени Франциска Скорины',
            r'(?:уо\s+)?(?:[«"])?ггту(?:[»"])?\b|(?:уо\s+)?(?:[«"])?г(?:омельский)?\s*г(?:осударственный)?\s*т(?:ехнический)?\s*у(?:ниверситет)?(?:[»"])?\b|(?:университет|унив)\s+(?:им\.?|имени)\s+(?:п\.?о\.?\s*)?сух': 'Гомельский государственный технический университет имени П.О. Сухого',
            r'(?:уо\s+)?(?:[«"])?гомгму(?:[»"])?\b|(?:уо\s+)?(?:[«"])?г(?:омельский)?\s*(?:г(?:осударственный)?)?\s*мед(?:ицинский)?\s*у(?:ниверситет)?(?:[»"])?': 'Гомельский государственный медицинский университет'
        }
    
    def find_similar_groups(self, texts: List[str]) -> Dict[str, Set[str]]:
        """Находит группы схожих текстов без привязки к конкретным данным"""
        if not texts:
            return {}

        # Убираем дубликаты и пустые значения
        original_texts = [t for t in texts if t and str(t).strip()]
        original_texts = list(dict.fromkeys(original_texts))  # Сохраняем порядок, удаляем дубликаты
        
        if len(original_texts) <= 1:
            return {original_texts[0]: set(original_texts)} if original_texts else {}
        
        # Шаг 0: Применяем предопределенные паттерны университетов
        university_groups = self._apply_university_patterns(original_texts)
        
        # Шаг 1: Группируем тексты, которые идентичны после нормализации
        norm_groups = self._group_by_normalized_text(original_texts)
        
        # Шаг 2: Ищем и группируем аббревиатуры и их расшифровки
        abbr_groups = self._find_abbreviation_groups(original_texts)
        
        # Шаг 3: Для оставшихся текстов применяем анализ схожести
        used_texts = set()
        for groups in [university_groups, norm_groups, abbr_groups]:
            for group in groups.values():
                used_texts.update(group)
        
        remaining_texts = [t for t in original_texts if t not in used_texts]
        
        # Применяем анализ схожести к оставшимся текстам
        similarity_groups = {}
        if remaining_texts:
            try:
                similarity_groups = self._analyze_with_similarity(remaining_texts)
            except Exception as e:
                print(f"Ошибка при анализе схожести: {e}")
        
        # Объединяем результаты всех методов
        all_groups = []
        for groups in [university_groups, norm_groups, abbr_groups, similarity_groups]:
            all_groups.extend([(rep, group) for rep, group in groups.items()])
        
        # Объединяем пересекающиеся группы
        merged_groups = self._merge_overlapping_groups(all_groups)
        
        # Добавляем одиночные тексты, которые не попали ни в одну группу
        all_grouped = set()
        for group in merged_groups.values():
            all_grouped.update(group)
        
        for text in original_texts:
            if text not in all_grouped:
                merged_groups[text] = {text}
        
        return merged_groups
    
    def _apply_university_patterns(self, texts: List[str]) -> Dict[str, Set[str]]:
        """Применяет предопределенные паттерны для университетов"""
        result = {}
        for pattern, representative in self.university_patterns.items():
            group = set()
            for text in texts:
                if re.search(pattern, text.lower()):
                    group.add(text)
            
            if len(group) > 1:
                result[representative] = group
        
        return result
    
    def _group_by_normalized_text(self, texts: List[str]) -> Dict[str, Set[str]]:
        """Группирует тексты, которые становятся идентичными после нормализации"""
        norm_to_orig = {}
        
        for text in texts:
            # Базовая нормализация (приведение к нижнему регистру, удаление пунктуации)
            norm_text = self.text_processor.normalize(text)
            
            if norm_text not in norm_to_orig:
                norm_to_orig[norm_text] = set()
            norm_to_orig[norm_text].add(text)
        
        # Формируем группы для текстов, которые стали идентичными после нормализации
        result = {}
        for norm_text, orig_texts in norm_to_orig.items():
            if len(orig_texts) > 1:
                # Выбираем представителя группы
                representative = self._select_representative(orig_texts)
                result[representative] = orig_texts
        
        return result
    
    def _find_abbreviation_groups(self, texts: List[str]) -> Dict[str, Set[str]]:
        """Находит аббревиатуры и их расшифровки без привязки к конкретным данным"""
        result = {}
        
        # Находим потенциальные аббревиатуры
        abbr_candidates = []
        for text in texts:
            if self._is_potential_abbreviation(text):
                abbr_candidates.append(text)
        
        # Для каждой потенциальной аббревиатуры ищем соответствующие полные названия
        for abbr in abbr_candidates:
            abbr_clean = ''.join(c for c in abbr.lower() if c.isalnum())
            if len(abbr_clean) < 2:
                continue
                
            group = {abbr}
            
            for full_text in texts:
                if full_text == abbr:
                    continue
                    
                # Если текст слишком короткий, это не расшифровка
                if len(full_text) < len(abbr_clean):
                    continue
                
                # Проверяем, может ли текст быть расшифровкой аббревиатуры
                if self._is_expansion_of_abbreviation(full_text, abbr):
                    group.add(full_text)
            
            # Если нашли группу с более чем одним элементом, добавляем ее в результат
            if len(group) > 1:
                # Выбираем в качестве представителя самый длинный текст
                representative = max(group, key=len)
                result[representative] = group
        
        return result
    
    def _is_potential_abbreviation(self, text: str) -> bool:
        """Определяет, может ли текст быть аббревиатурой (универсальный алгоритм)"""
        text = str(text).strip()
        
        # Если текст слишком длинный, это не аббревиатура
        if len(text) > 15:
            return False
        
        # Проверяем различные паттерны аббревиатур
        
        # Паттерн 1: Все заглавные буквы (ГГУ, ГГТУ, БГУ)
        if text.isupper() and 2 <= len(text) <= 10:
            return True
        
        # Паттерн 2: Заглавные буквы с точками (Г.Г.У., У.О.)
        if re.match(r'^([A-ZА-Я]\.)+[A-ZА-Я]?\.?$', text):
            return True
        
        # Паттерн 3: Заглавные буквы с цифрами или другими символами
        if re.match(r'^[A-ZА-Я]{2,}[0-9\-\s\.]*$', text) and len(text) <= 10:
            return True
        
        # Паттерн 4: Аббревиатура с дополнительными словами
        if re.match(r'^[A-ZА-Я]{2,}(\s+\w+){0,2}$', text) and len(text) <= 15:
            return True
        
        # Паттерн 5: Несколько заглавных букв в начале каждого слова
        words = text.split()
        if len(words) >= 2 and all(word[0].isupper() for word in words if word):
            abbr = ''.join(word[0] for word in words if word)
            if 2 <= len(abbr) <= 10:
                return True
        
        # Паттерн 6: Начинается с УО или ГУО (учреждение образования)
        if text.upper().startswith(('УО ', 'ГУО ')):
            # Проверяем, есть ли после УО/ГУО что-то похожее на аббревиатуру
            rest = text[3:].strip().strip('"\'')
            if rest and (rest.isupper() or re.match(r'^[A-ZА-Я]{2,}', rest)):
                return True
        
        return False
    
    def _is_expansion_of_abbreviation(self, full_text: str, abbr: str) -> bool:
        """Проверяет, является ли текст расшифровкой аббревиатуры (универсальный алгоритм)"""
        full_text = str(full_text).lower()
        abbr = str(abbr).lower()
        
        # Очищаем аббревиатуру от не-буквенных символов
        abbr_clean = ''.join(c for c in abbr if c.isalnum())
        if not abbr_clean:
            return False
        
        # Проверка 1: Аббревиатура содержится в тексте как отдельное слово
        if re.search(fr'\b{re.escape(abbr)}\b', full_text):
            return True
        
        # Проверка 2: Первые буквы слов в тексте образуют аббревиатуру
        words = re.findall(r'\b\w+\b', full_text)
        if words:
            # Получаем первые буквы всех слов
            first_letters = ''.join(word[0] for word in words if word)
            
            # Проверяем, содержится ли аббревиатура в первых буквах
            if abbr_clean in first_letters:
                return True
            
            # Проверяем, содержатся ли первые буквы значимых слов в аббревиатуре
            # Игнорируем короткие предлоги и союзы
            ignore_words = {'и', 'в', 'на', 'с', 'по', 'для', 'при', 'им', 'имени', 'of', 'the', 'a', 'an'}
            significant_words = [w for w in words if w not in ignore_words]
            
            if significant_words:
                sig_letters = ''.join(word[0] for word in significant_words)
                
                # Если первые буквы значимых слов совпадают с аббревиатурой
                if sig_letters == abbr_clean or abbr_clean in sig_letters:
                    return True
        
        # Проверка 3: Последовательные символы аббревиатуры содержатся в тексте
        # Улучшенный алгоритм для поиска последовательных символов
        char_positions = []
        last_pos = -1
        
        for char in abbr_clean:
            pos = full_text.find(char, last_pos + 1)
            if pos > last_pos:
                char_positions.append(pos)
                last_pos = pos
            else:
                # Пробуем найти с начала, если не нашли после последней позиции
                pos = full_text.find(char)
                if pos >= 0 and pos not in char_positions:
                    char_positions.append(pos)
                    last_pos = pos
                else:
                    break
                    
        if len(char_positions) == len(abbr_clean):
            # Все символы аббревиатуры найдены
            return True
        
        # Проверка 4: Специфичная для образовательных учреждений
        # Проверяем наличие ключевых слов "университет", "институт" и т.д.
        edu_keywords = {'университет', 'институт', 'академия', 'колледж', 'школа', 'лицей', 'гимназия'}
        has_edu_keyword = any(kw in full_text for kw in edu_keywords)
        
        if has_edu_keyword and len(abbr_clean) >= 3:
            # Проверяем, содержит ли полный текст части аббревиатуры
            abbr_parts = []
            for i in range(len(abbr_clean) - 1):
                abbr_parts.append(abbr_clean[i:i+2])
            
            matching_parts = sum(1 for part in abbr_parts if part in full_text)
            if matching_parts >= len(abbr_parts) * 0.7:  # 70% совпадение
                return True
        
        return False
    
    def _preprocess_for_tfidf(self, text: str) -> str:
        """Предобрабатывает текст для TF-IDF анализа"""
        # Базовая нормализация
        text = str(text)
        text = self.text_processor.normalize(text)
        
        # Удаляем общие слова, которые не несут специфической информации
        text = re.sub(r'\b(и|в|на|с|по|для|при|имени|им|г)\b', ' ', text)
        
        # Заменяем часто встречающиеся слова на их сокращения для лучшего сопоставления
        text = text.replace('университет', 'унив')
        text = text.replace('государственный', 'гос')
        text = text.replace('институт', 'инст')
        text = text.replace('академия', 'акад')
        
        # Нормализуем пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _analyze_with_similarity(self, texts: List[str]) -> Dict[str, Set[str]]:
        """Анализирует тексты с помощью прямого расчета сходства"""
        if not texts or len(texts) < 2:
            return {}
            
        try:
            # Предобработка текстов
            processed_texts = [str(self._preprocess_for_tfidf(t)) for t in texts]
            
            # Вычисляем матрицу сходства напрямую, без использования TF-IDF
            n = len(processed_texts)
            similarity_matrix = np.zeros((n, n), dtype=float)
            
            for i in range(n):
                for j in range(i, n):
                    # Используем функцию расчета схожести текстов
                    similarity = float(self._calculate_similarity(processed_texts[i], processed_texts[j]))
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
            
            # Создаем маску схожести с явной проверкой типов
            threshold = float(self.similarity_threshold)
            similarity_mask = np.zeros_like(similarity_matrix, dtype=bool)
            for i in range(n):
                for j in range(n):
                    similarity_mask[i, j] = similarity_matrix[i, j] > threshold
            
            # Находим компоненты связности
            components = self._find_connected_components(similarity_mask)
            
            # Преобразуем компоненты в группы текстов
            result = {}
            for component in components:
                if len(component) > 1:
                    # Собираем тексты для этой компоненты
                    group_texts = set(texts[i] for i in component)
                    
                    # Выбираем представителя группы
                    representative = self._select_representative(group_texts)
                    result[representative] = group_texts
            
            return result
        except Exception as e:
            print(f"Ошибка при анализе схожести: {e}")
            return {}
    
    def _merge_overlapping_groups(self, groups: List[Tuple[str, Set[str]]]) -> Dict[str, Set[str]]:
        """Объединяет пересекающиеся группы"""
        if not groups:
            return {}
            
        # Создаем граф связей между группами
        n = len(groups)
        adjacency_matrix = np.zeros((n, n), dtype=bool)
        
        for i in range(n):
            for j in range(i+1, n):
                _, group_i = groups[i]
                _, group_j = groups[j]
                
                # Если группы пересекаются, добавляем связь
                if group_i.intersection(group_j):
                    adjacency_matrix[i, j] = True
                    adjacency_matrix[j, i] = True
        
        # Находим компоненты связности в графе групп
        visited = [False] * n
        merged_components = []
        
        for i in range(n):
            if not visited[i]:
                component = []
                self._dfs(adjacency_matrix, i, visited, component)
                merged_components.append(component)
        
        # Объединяем группы в каждой компоненте
        result = {}
        for component in merged_components:
            merged_group = set()
            component_reps = []
            
            for idx in component:
                rep, group = groups[idx]
                merged_group.update(group)
                component_reps.append(rep)
            
            # Выбираем представителя для объединенной группы
            representative = self._select_representative(set(component_reps))
            result[representative] = merged_group
        
        return result
    
    def _find_connected_components(self, adjacency_matrix):
        """Находит связные компоненты в графе схожести"""
        n = adjacency_matrix.shape[0]
        visited = [False] * n
        components = []
        
        for i in range(n):
            if not visited[i]:
                component = []
                self._dfs(adjacency_matrix, i, visited, component)
                components.append(component)
                
        return components
    
    def _dfs(self, adjacency_matrix, node, visited, component):
        """Обход графа в глубину для поиска связных компонент"""
        visited[node] = True
        component.append(node)
        
        for neighbor in range(adjacency_matrix.shape[0]):
            if adjacency_matrix[node, neighbor] and not visited[neighbor]:
                self._dfs(adjacency_matrix, neighbor, visited, component)
    
    def _select_representative(self, texts: Set[str]) -> str:
        """Выбирает представителя группы по универсальным критериям"""
        if not texts:
            return ""
        if len(texts) == 1:
            return next(iter(texts))
        
        # Проверяем, совпадает ли какой-либо текст с названиями университетов
        for full_name in self.university_patterns.values():
            if full_name in texts:
                return full_name
        
        # Преобразуем в список для удобства
        texts_list = list(texts)
        
        # Критерий 1: Предпочитаем более длинные тексты (обычно содержат больше информации)
        # Но не слишком длинные, чтобы избежать выбора длинных описаний
        optimal_length = 50
        length_scores = [1 - abs(len(t) - optimal_length) / max(optimal_length, len(t)) for t in texts_list]
        
        # Критерий 2: Предпочитаем тексты с заглавными буквами (обычно более формальные)
        capital_scores = [sum(1 for c in t if c.isupper()) / max(1, len(t)) for t in texts_list]
        
        # Критерий 3: Предпочитаем тексты без специальных символов и цифр
        clean_scores = [sum(1 for c in t if c.isalpha() or c.isspace()) / max(1, len(t)) for t in texts_list]
        
        # Критерий 4: Предпочитаем тексты, которые являются "центральными" в группе
        centrality_scores = [self._calculate_centrality(t, texts) for t in texts_list]
        
        # Комбинируем все критерии с разными весами
        combined_scores = [
            0.2 * length_scores[i] + 
            0.3 * capital_scores[i] + 
            0.2 * clean_scores[i] + 
            0.3 * centrality_scores[i]
            for i in range(len(texts_list))
        ]
        
        # Выбираем текст с наивысшим общим баллом
        best_idx = combined_scores.index(max(combined_scores))
        return texts_list[best_idx]
    
    def _calculate_centrality(self, text: str, all_texts: Set[str]) -> float:
        """Вычисляет, насколько текст похож на все остальные тексты в группе"""
        if len(all_texts) <= 1:
            return 1.0
            
        similarities = []
        for other in all_texts:
            if other == text:
                continue
                
            similarity = self._calculate_similarity(text, other)
            similarities.append(similarity)
            
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Вычисляет схожесть двух текстов"""
        text1 = str(text1).lower()
        text2 = str(text2).lower()
        
        # Если тексты идентичны
        if text1 == text2:
            return 1.0
            
        # Если один текст содержит другой
        if text1 in text2 or text2 in text1:
            shorter = text1 if len(text1) < len(text2) else text2
            longer = text2 if len(text1) < len(text2) else text1
            return len(shorter) / len(longer)
        
        # Иначе используем схожесть множеств символов
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
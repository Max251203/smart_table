from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QMessageBox, QPushButton
from models.table_model import SmartTableModel
from models.data_processor import DataProcessor
from ui.components.table_view import SmartTableView
import pandas as pd
import os

class TableController(QObject):
    def __init__(self, view: SmartTableView):
        super().__init__()
        self.view = view
        self.data_processor = DataProcessor()
        self.model: Optional[SmartTableModel] = None
        self.num_mode = "excel"
        self.num_col_index = 0
        self.current_file_path = None

    def load_file(self, file_path: str) -> bool:
        try:
            df, num_col_index = self.data_processor.load_excel(file_path)
            self.num_col_index = num_col_index
            self.num_mode = "excel"
            self.model = SmartTableModel(df, self.num_mode, self.num_col_index)
            self.view.setModel(self.model)
            self.view.adjust_columns()
            self.current_file_path = file_path
            return True
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False

    def get_columns(self) -> List[str]:
        if self.model is None:
            return []
        return [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]

    def toggle_number_mode(self):
        if self.model is None:
            return
        self.num_mode = "order" if self.num_mode == "excel" else "excel"
        self.model.num_mode = self.num_mode
        self.model.layoutChanged.emit()
        self.view.adjust_columns()

    def sort_column(self, column: int, order: Qt.SortOrder):
        if self.model is None:
            return
        if column == self.num_col_index and self.num_mode == "order":
            return
        self.model.sort(column, order)
        self.view.header.setSortIndicator(column, order)
        self.view.adjust_columns()

    def set_number_mode(self, mode):
        if self.model is not None:
            self.num_mode = mode
            self.model.num_mode = mode
            self.model.layoutChanged.emit()
            self.view.adjust_columns()

    def set_filtered_dataframe(self, df: pd.DataFrame):
        if self.model is not None:
            self.model.set_dataframe(df)
            self.view.adjust_columns()

    def reset_all(self):
        if self.model is None or self.data_processor.current_df is None:
            return
        self.model.set_dataframe(self.data_processor.current_df)
        index = self.num_col_index
        self.model.sort(index, Qt.AscendingOrder)
        self.num_mode = "excel"
        self.model.num_mode = "excel"
        self.view.header.setSortIndicator(-1)  # <--- Сброс!
        self.view.adjust_columns()

    def get_cell_value(self, row: int, column: int) -> str:
        if self.model is None:
            return ""
        return self.model.data(self.model.index(row, column), Qt.DisplayRole)

    def get_column_values(self, column_name: str) -> List[str]:
        if self.model is None or self.data_processor.current_df is None:
            return []
        return self.data_processor.current_df[column_name].unique().tolist()
        
    def analyze_column_data(self, column_name: str) -> Dict:
        """Анализирует данные колонки и возвращает статистику."""
        if self.model is None or self.data_processor.current_df is None:
            return {}
            
        try:
            column_data = self.data_processor.current_df[column_name]
            result = {
                "max_length": max([len(str(v)) for v in column_data if v and str(v).strip()], default=0),
                "unique_count": len(column_data.unique()),
                "is_numeric": False,
                "is_date": False,
                "sample_values": list(column_data.unique())[:10]
            }
            
            # Проверяем, числовая ли колонка
            try:
                numeric_values = pd.to_numeric(column_data, errors='coerce')
                if not numeric_values.isna().all():
                    result["is_numeric"] = True
            except:
                pass
                
            return result
        except:
            return {}

    def add_record(self, record_data: Dict[str, str]) -> bool:
        """Добавляет новую запись в таблицу и сохраняет в Excel-файл."""
        if self.model is None or self.data_processor.current_df is None:
            return False
            
        try:
            # Создаем новую запись
            new_record = {}
            
            # Заполняем все колонки из dataframe
            for col in self.data_processor.current_df.columns:
                if col in record_data:
                    new_record[col] = record_data[col]
                else:
                    # Пропускаем Excel # - она будет автоматически назначена
                    if col.lower() in ["excel #", "№", "№ (порядок)"]:
                        new_record[col] = ""
                    else:
                        new_record[col] = ""
            
            # Проверяем, можно ли сохранить в Excel
            if self.current_file_path and not self._can_save_to_excel():
                return False
            
            # Если проверка прошла успешно или не требуется сохранение, добавляем запись
            self.data_processor.add_record(new_record)
            
            # Сохраняем изменения в Excel-файл
            if self.current_file_path:
                save_result = self.save_to_excel()
                if not save_result:
                    return False
            
            # Обновляем модель
            self.model.set_dataframe(self.data_processor.current_df)
            self.view.adjust_columns()
            return True
                
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False
            
    def _can_save_to_excel(self) -> bool:
        """Проверяет, можно ли сохранить данные в Excel-файл."""
        if not self.current_file_path:
            return False
            
        try:
            # Проверяем, не открыт ли файл в другой программе
            # Пытаемся открыть файл для записи
            with open(self.current_file_path, 'a+b'):
                pass
            return True
        except Exception:
            return False
            
    def save_to_excel(self) -> bool:
        """Сохраняет текущие данные в Excel-файл."""
        if self.model is None or self.data_processor.current_df is None or not self.current_file_path:
            return False
            
        try:
            # Создаем временное имя файла
            file_dir = os.path.dirname(self.current_file_path)
            file_name = os.path.basename(self.current_file_path)
            temp_file = os.path.join(file_dir, f"~temp_{file_name}")
            
            # Сохраняем во временный файл
            self.data_processor.save_excel(temp_file)
            
            # Проверяем, что файл создан
            if not os.path.exists(temp_file):
                return False
                
            # Пробуем заменить оригинальный файл
            try:
                if os.path.exists(self.current_file_path):
                    os.replace(temp_file, self.current_file_path)
                else:
                    os.rename(temp_file, self.current_file_path)
                return True
            except Exception:
                # Если файл заблокирован или другая ошибка
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                return False
                
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return False
    
    def get_row_id(self, row_index: int) -> str:
        """Получает уникальный идентификатор строки по её индексу в текущей модели."""
        if self.model is None:
            return ""
        
        # Используем метод модели для получения реального ID независимо от режима
        return self.model.get_real_row_id(row_index)
    
    def find_row_by_id(self, row_id: str) -> int:
        """Находит индекс строки в DataFrame по её ID."""
        if self.model is None or self.data_processor.current_df is None:
            return -1
        
        # Определяем колонку с ID
        id_col_name = None
        for col in self.data_processor.current_df.columns:
            if col.lower() in ["excel #", "№"]:
                id_col_name = col
                break
        
        if id_col_name is None:
            return -1
        
        # Ищем строку по ID
        for i, row in self.data_processor.current_df.iterrows():
            if str(row[id_col_name]) == row_id:
                return i
        
        return -1
        
    def update_record(self, row_id: str, record_data: Dict[str, Any]) -> bool:
        """Обновляет запись по её ID."""
        if self.model is None or self.data_processor.current_df is None:
            return False
            
        try:
            # Находим строку по ID
            row_index = self.find_row_by_id(row_id)
            if row_index == -1:
                return False
            
            # Обновляем значения
            for col, value in record_data.items():
                if col in self.data_processor.current_df.columns:
                    # Не обновляем колонку ID
                    if col.lower() not in ["excel #", "№", "№ (порядок)"]:
                        self.data_processor.current_df.at[row_index, col] = value
            
            # Сохраняем изменения
            if self.current_file_path:
                save_result = self.save_to_excel()
                if not save_result:
                    return False
            
            # Обновляем модель
            self.model.set_dataframe(self.data_processor.current_df)
            self.view.adjust_columns()
            return True
                
        except Exception as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False
            
    def delete_record(self, row_id: str) -> bool:
        """Удаляет запись по её ID."""
        if self.model is None or self.data_processor.current_df is None:
            return False
            
        try:
            # Находим строку по ID
            row_index = self.find_row_by_id(row_id)
            if row_index == -1:
                return False
            
            # Удаляем строку
            self.data_processor.current_df = self.data_processor.current_df.drop(index=row_index).reset_index(drop=True)
            
            # Сохраняем изменения
            if self.current_file_path:
                save_result = self.save_to_excel()
                if not save_result:
                    return False
            
            # Обновляем модель
            self.model.set_dataframe(self.data_processor.current_df)
            self.view.adjust_columns()
            return True
                
        except Exception as e:
            print(f"Ошибка при удалении записи: {e}")
            return False
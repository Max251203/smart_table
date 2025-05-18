from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QTextEdit, QPushButton, 
                               QScrollArea, QWidget)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from typing import List, Dict, Set
from ui.components.custom_combobox import SmartComboBox  # Используем SmartComboBox

class RecordDialog(QDialog):
    def __init__(self, columns: List[str], parent=None, record_data: Dict[str, str] = None, 
                 column_max_lengths: Dict[str, int] = None, column_values: Dict[str, List[str]] = None,
                 work_place_groups: Dict[str, Dict[str, set]] = None):
        super().__init__(parent)
        
        self.setWindowTitle("Добавление записи" if record_data is None else "Редактирование записи")
        self.setMinimumSize(700, 500)
        self.setObjectName("recordDialog")
        
        self.columns = columns
        self.record_data = record_data
        self.column_max_lengths = column_max_lengths or {}
        self.column_values = column_values or {}
        self.work_place_groups = work_place_groups or {}
        self.field_widgets = {}
        
        self._init_ui()
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Создаем прокручиваемую область для полей формы
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("recordScrollArea")
        main_layout.addWidget(scroll_area)
        
        form_container = QWidget()
        form_container.setObjectName("recordFormContainer")
        scroll_area.setWidget(form_container)
        
        # Используем вертикальный макет для компактной формы
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)
        
        # Фильтруем колонки - исключаем системные
        filtered_columns = [c for c in self.columns if c.lower() not in ["excel #", "№", "№ (порядок)"]]
        
        # Создаем поля ввода для каждой колонки
        for column in filtered_columns:
            # Создаем контейнер для поля и метки
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(4)
            
            # Создаем метку
            label = QLabel(column)
            label.setObjectName("recordFieldLabel")
            label.setWordWrap(True)
            field_layout.addWidget(label)
            
            # Определяем тип поля и размеры на основе данных
            is_long_text = self._is_long_text(column)
            
            if is_long_text:
                # Многострочное поле для длинных текстов
                field = QTextEdit()
                field.setObjectName("recordTextEdit")
                
                # Настраиваем высоту поля в зависимости от длины текста
                max_length = self.column_max_lengths.get(column, 0)
                if max_length > 200:
                    field.setMinimumHeight(100)
                    field.setMaximumHeight(150)
                elif max_length > 100:
                    field.setMinimumHeight(80)
                    field.setMaximumHeight(120)
                else:
                    field.setMinimumHeight(60)
                    field.setMaximumHeight(80)
            else:
                # Вместо LineEdit используем SmartComboBox для всех полей
                field = SmartComboBox()
                field.setObjectName("recordComboBox")
                field.setEditable(True)  # Делаем редактируемым
                
                # Специальная обработка для поля места работы/учёбы
                is_workplace_field = "место работы" in column.lower() or "учёбы" in column.lower()
                
                if is_workplace_field and column in self.work_place_groups:
                    # Добавляем все группы в комбобокс
                    all_items = set()
                    groups = self.work_place_groups[column]
                    
                    # Сначала добавляем ключи групп
                    field.addItems(sorted(groups.keys()))
                    
                    # Собираем все значения для автодополнения
                    for key, values in groups.items():
                        all_items.add(key)
                        all_items.update(values)
                    
                    # Также добавляем все уникальные значения из колонки
                    if column in self.column_values:
                        all_items.update(self.column_values[column])
                        
                # Стандартное заполнение для других полей
                elif column in self.column_values and self.column_values[column]:
                    field.addItems(sorted(self.column_values[column]))
            
            # Если есть данные для редактирования, заполняем поле
            if self.record_data and column in self.record_data:
                if isinstance(field, SmartComboBox):
                    field.setCurrentText(self.record_data[column])
                else:
                    field.setPlainText(self.record_data[column])
            
            field_layout.addWidget(field)
            form_layout.addWidget(field_container)
            self.field_widgets[column] = field
        
        # Кнопки внизу диалога
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("recordCancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.setObjectName("recordSaveButton")
        self.save_button.setIcon(QIcon(":/icon/icons/save.png"))
        self.save_button.setIconSize(QSize(24, 24))
        self.save_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def _is_long_text(self, column: str) -> bool:
        """Определяет, нужно ли для колонки использовать многострочное поле."""
        long_text_indicators = ["комментарий", "описание", "адрес", "примечание"]
        
        # Проверяем название колонки
        if any(indicator in column.lower() for indicator in long_text_indicators):
            return True
        
        # Проверяем длину текста в колонке
        max_length = self.column_max_lengths.get(column, 0)
        return max_length > 50 or len(column) > 30
    
    def get_record_data(self) -> Dict[str, str]:
        """Возвращает данные, введенные пользователем."""
        result = {}
        for column, widget in self.field_widgets.items():
            if isinstance(widget, SmartComboBox):
                result[column] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                result[column] = widget.toPlainText()
        return result
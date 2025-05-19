from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTextEdit, QPushButton, 
                             QScrollArea, QWidget, QMessageBox)
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QIcon
from typing import List, Dict, Set
from ui.components.custom_combobox import SmartComboBox

class RecordDialog(QDialog):
    def __init__(self, columns: List[str], parent=None, record_data: Dict[str, str] = None, 
                 column_max_lengths: Dict[str, int] = None, column_values: Dict[str, List[str]] = None,
                 work_place_groups: Dict[str, Dict[str, set]] = None, table_controller=None):
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
        self.current_focus_widget = None
        self.table_controller = table_controller  # Добавляем ссылку на контроллер таблицы
        self.success = False  # Флаг успешного добавления
        
        self._init_ui()
        
    def keyPressEvent(self, event):
        """Предотвращаем закрытие диалога по Enter"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Не закрываем диалог по Enter - игнорируем событие
            return
        super().keyPressEvent(event)
        
    def eventFilter(self, obj, event):
        """Фильтр событий для отслеживания фокуса на полях"""
        if event.type() == QEvent.FocusIn:
            self.current_focus_widget = obj
        return False
        
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
            
            # Определяем тип поля на основе анализа фактического объема текста
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
                    
                # Заполняем данными при редактировании
                if self.record_data and column in self.record_data:
                    field.setPlainText(self.record_data[column])
            else:
                # Используем SmartComboBox для всех полей
                field = SmartComboBox(editable=True)  # Явно указываем редактируемость
                field.setObjectName("recordComboBox")
                field.installEventFilter(self)  # Устанавливаем фильтр событий для отслеживания фокуса
                
                # Настраиваем размер поля на основе анализа контента
                field_size = self._get_field_size(column)
                field.setMinimumWidth(field_size["width"])
                field.setMinimumHeight(field_size["height"])
                
                # Собираем все возможные значения для поля
                all_values = set()
                
                # Специальная обработка для поля места работы/учёбы
                is_workplace_field = "место работы" in column.lower() or "учёбы" in column.lower()
                
                if is_workplace_field and column in self.work_place_groups:
                    # Собираем все группы и их значения
                    groups = self.work_place_groups[column]
                    
                    # Добавляем ключи групп и их значения
                    for key, values in groups.items():
                        all_values.add(key)
                        all_values.update(values)
                
                # Добавляем значения из колонки для всех полей
                if column in self.column_values:
                    all_values.update(self.column_values[column])
                    
                # Настраиваем комбобокс с явным указанием редактируемости
                sorted_values = sorted(list(all_values)) if all_values else []
                if sorted_values:
                    field.setup(sorted_values, editable=True)
                else:
                    # Гарантируем, что у списка будет хотя бы один элемент
                    field.addItem("")
                
                # Заполняем данными при редактировании
                if self.record_data and column in self.record_data:
                    field.setCurrentText(self.record_data[column])
                else:
                    field.setCurrentText("")
            
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
        """Определяет, нужно ли для колонки использовать многострочное поле.
        
        Теперь мы анализируем фактический объем текста в данных колонки,
        а не только название или длину текста в ячейках.
        """
        # Проверим, не является ли колонка явно многострочной по названию
        long_text_indicators = ["комментарий", "описание", "примечание"]
        if any(indicator == column.lower() for indicator in long_text_indicators):
            return True
        
        # Теперь анализируем данные
        max_length = self.column_max_lengths.get(column, 0)
        
        # Если максимальная длина текста в колонке очень большая - делаем многострочным
        if max_length > 150:
            return True
            
        # Если в колонке есть слово "адрес" и большая длина - тоже многострочное
        if "адрес" in column.lower() and max_length > 50:
            return True
            
        # В других случаях предпочитаем использовать SmartComboBox
        # Делаем поле многострочным только если текст действительно значительный
        return False
    
    def _get_field_size(self, column: str) -> Dict[str, int]:
        """Определяет оптимальный размер поля на основе данных."""
        # По умолчанию стандартный размер
        result = {
            "width": 250,
            "height": 32
        }
        
        # Получаем максимальную длину текста в колонке
        max_length = self.column_max_lengths.get(column, 0)
        
        # Определяем размер на основе длины контента
        if max_length > 40:
            # Для очень длинных значений
            result["width"] = 400
            result["height"] = 35
        elif max_length > 25:
            # Для средних значений
            result["width"] = 350
            result["height"] = 35
        elif max_length > 15:
            # Для коротких значений
            result["width"] = 300
            result["height"] = 32
        else:
            # Для совсем коротких значений
            result["width"] = 250
            result["height"] = 32
        
        # Учитываем тип данных по названию колонки
        column_lower = column.lower()
        
        # Поля, которые обычно содержат длинные значения
        if "имя" in column_lower or "фамилия" in column_lower or "название" in column_lower:
            result["width"] = max(result["width"], 350)
        
        # Поля, которые обычно имеют сложную структуру
        if "должность" in column_lower or "статус" in column_lower:
            result["width"] = max(result["width"], 300)
            
        # Поля, которые обычно короткие
        if "дата" in column_lower or "возраст" in column_lower or "пол" in column_lower:
            result["width"] = min(result["width"], 250)
            
        return result
    
    def get_record_data(self) -> Dict[str, str]:
        """Возвращает данные, введенные пользователем."""
        result = {}
        for column, widget in self.field_widgets.items():
            if isinstance(widget, SmartComboBox):
                result[column] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                result[column] = widget.toPlainText()
        return result
    
    def accept(self):
        # Переопределяем стандартный метод accept
        # Не закрываем диалог сразу, а пытаемся сохранить данные
        if self.table_controller:
            record_data = self.get_record_data()
            
            # Проверяем, что есть хотя бы одно непустое поле
            has_data = False
            for value in record_data.values():
                if value and value.strip():
                    has_data = True
                    break
                    
            if not has_data:
                QMessageBox.warning(
                    self, 
                    "Пустая запись", 
                    "Невозможно сохранить полностью пустую запись. Введите хотя бы одно значение."
                )
                return  # Остаемся в диалоге
            
            # Определяем, это добавление или редактирование
            is_editing = hasattr(self, 'row_id') and self.row_id is not None
            
            try:
                # Проверяем, можно ли сохранить в Excel
                if self.table_controller.current_file_path and not self.table_controller._can_save_to_excel():
                    QMessageBox.critical(
                        self, 
                        "Ошибка сохранения", 
                        f"Не удалось {'обновить' if is_editing else 'добавить'} запись. Возможно, Excel-файл заблокирован для записи или открыт в другой программе.",
                        QMessageBox.Ok
                    )
                    return  # Остаемся в диалоге
                
                success = False
                
                # Если это редактирование, обновляем запись по ID
                if is_editing:
                    success = self.table_controller.update_record(self.row_id, record_data)
                else:
                    # Для добавления используем существующий метод
                    success = self.table_controller.add_record(record_data)
                
                if success:
                    # Сбрасываем режим колонки номеров в "excel"
                    self.table_controller.set_number_mode("excel")
                    
                    action_done = "обновлена" if is_editing else "добавлена"
                    QMessageBox.information(
                        self, 
                        f"Запись {action_done}", 
                        f"Запись успешно {action_done} в таблицу и сохранена в Excel-файл."
                    )
                    self.success = True  # Устанавливаем флаг успешного добавления/редактирования
                    super().accept()  # Закрываем диалог только при успехе
                else:
                    action_text = "обновить" if is_editing else "добавить"
                    QMessageBox.critical(
                        self, 
                        "Ошибка сохранения", 
                        f"Не удалось {action_text} запись. Возможно, произошла непредвиденная ошибка.",
                        QMessageBox.Ok
                    )
                    # Остаемся в диалоге
            except Exception as e:
                import traceback
                print(f"Ошибка при {'редактировании' if is_editing else 'добавлении'} записи: {e}")
                print(traceback.format_exc())
                QMessageBox.critical(
                    self, 
                    "Ошибка", 
                    f"Произошла ошибка при {'редактировании' if is_editing else 'добавлении'} записи: {str(e)}"
                )
                # Остаемся в диалоге
        else:
            super().accept()  # Если нет контроллера, просто закрываем диалог
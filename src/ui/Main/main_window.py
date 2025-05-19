from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QHBoxLayout, QLabel, QPushButton, QWidget, QCompleter
from PySide6.QtCore import Qt, QPropertyAnimation, QSize
from PySide6.QtGui import QIcon
from ui.Main.main_ui import Ui_MainWindow
from controllers.table_controller import TableController
from controllers.filter_controller import FilterController
from ui.components.custom_combobox import SmartComboBox
from ui.components.table_view import SmartTableView
from ui.components.record_dialog import RecordDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._init_search_panel()
        self._init_custom_widgets()
        self._init_controllers()
        self._connect_signals()
        self._search_panel_pinned = False
        self._update_search_button_state()

    def _init_search_panel(self):
        # Создаем макет для панели поиска
        layout = QHBoxLayout(self.ui.searchPanel)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)
        
        # Метка "Искать по:" вместо "Колонка:"
        label_column = QLabel("Искать по:")
        label_column.setObjectName("searchLabel")
        label_column.setMinimumWidth(80)
        label_column.setMaximumWidth(100)
        layout.addWidget(label_column, 0)
        
        # ComboBox для колонок (будет заменен на SmartComboBox)
        self.column_box_placeholder = QWidget()
        layout.addWidget(self.column_box_placeholder, 4)
        
        # Метка "Ключевые слова"
        label_keyword = QLabel("Ключевые слова:")
        label_keyword.setObjectName("searchLabel")
        label_keyword.setMinimumWidth(120)
        label_keyword.setMaximumWidth(150)
        layout.addWidget(label_keyword, 0)
        
        # ComboBox для ключевых слов (будет заменен на SmartComboBox)
        self.keyword_box_placeholder = QWidget()
        layout.addWidget(self.keyword_box_placeholder, 4)
        
        # Кнопка поиска - используем те же стили, что и для верхних кнопок
        self.btn_search = QPushButton("Найти")
        self.btn_search.setObjectName("btnSearch")
        self.btn_search.setIcon(QIcon(":/icon/icons/search.png"))
        self.btn_search.setIconSize(QSize(24, 24))
        layout.addWidget(self.btn_search, 0)
        
        # Кнопка закрепления панели - делаем её минималистичной
        self.btn_pin = QPushButton()
        self.btn_pin.setObjectName("pinButton")
        self.btn_pin.setIcon(QIcon(":/icon/icons/pin_off.png"))
        self.btn_pin.setIconSize(QSize(24, 24))
        self.btn_pin.setCheckable(True)
        self.btn_pin.setToolTip("Закрепить панель поиска")
        self.btn_pin.setFixedSize(QSize(32, 32))
        layout.addWidget(self.btn_pin, 0)
        
        # Настраиваем ID для панели поиска
        self.ui.searchPanel.setObjectName("searchPanel")

    def _init_custom_widgets(self):
        # Создаем и настраиваем SmartComboBox для колонок и ключевых слов
        self.column_box = SmartComboBox()
        self.keyword_box = SmartComboBox()
        self.keyword_box.setEditable(True)
        
        # Заменяем placeholder виджеты на реальные комбобоксы
        layout = self.ui.searchPanel.layout()
        layout.replaceWidget(self.column_box_placeholder, self.column_box)
        layout.replaceWidget(self.keyword_box_placeholder, self.keyword_box)
        self.column_box_placeholder.deleteLater()
        self.keyword_box_placeholder.deleteLater()
        
        # Создаем и настраиваем SmartTableView
        self.table_view = SmartTableView()
        self.ui.tableLayout.addWidget(self.table_view)
        
        # Исправление размера иконки на кнопке "Умный поиск" - одинаковый размер с другими кнопками
        self.ui.btnSmartSearch.setIconSize(QSize(24, 24))
        # Делаем кнопку умного поиска одинакового размера с другими кнопками
        self.ui.btnSmartSearch.setMinimumWidth(self.ui.btnReset.minimumWidth())
        self.ui.btnSmartSearch.setMinimumHeight(self.ui.btnReset.minimumHeight())

    def _init_controllers(self):
        self.table_controller = TableController(self.table_view)
        self.filter_controller = FilterController(
            column_box=self.column_box,
            keyword_edit=self.keyword_box,
            table_controller=self.table_controller,
        )

    def _connect_signals(self):
        # Подключаем сигналы для кнопок на основной панели инструментов
        self.ui.btnLoad.clicked.connect(self._load_excel)
        self.ui.btnReset.clicked.connect(self.filter_controller.reset_all)
        self.ui.btnSmartSearch.clicked.connect(self._toggle_search_panel)
        self.ui.btnAddRecord.clicked.connect(self._show_add_record_dialog)
        
        # Подключаем сигналы элементов панели поиска
        self.btn_search.clicked.connect(self.filter_controller.apply_filter)
        self.btn_pin.clicked.connect(self._toggle_pin_search_panel)
        self.column_box.currentIndexChanged.connect(self.filter_controller.on_column_change)
        self.keyword_box.lineEdit().returnPressed.connect(self.filter_controller.apply_filter)
        
        # Подключаем сигналы таблицы
        self.table_view.sortRequested.connect(self.table_controller.sort_column)
        self.table_view.numberModeChanged.connect(self.table_controller.toggle_number_mode)

    def _load_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть Excel файл", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            if self.table_controller.load_file(file_path):
                self.filter_controller.update_columns(self.table_controller.get_columns())
            else:
                QMessageBox.warning(
                    self, "Ошибка",
                    "Не удалось загрузить файл. Проверьте формат или структуру таблицы."
                )

    def _toggle_search_panel(self):
        if self._search_panel_pinned:
            return

        is_visible = self.ui.searchPanelContainer.isVisible()

        self.ui.searchPanelContainer.setVisible(True)
        self.animation = QPropertyAnimation(self.ui.searchPanelContainer, b"maximumHeight")
        self.animation.setDuration(200)

        if is_visible:
            self.animation.setStartValue(60)
            self.animation.setEndValue(0)
            self.animation.finished.connect(lambda: self._on_search_panel_hidden())
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(60)
            self.animation.finished.connect(self._update_search_button_state)

        self.animation.start()

    def _on_search_panel_hidden(self):
        self.ui.searchPanelContainer.setVisible(False)
        self._update_search_button_state()

    def _update_search_button_state(self):
        is_visible = self.ui.searchPanelContainer.isVisible()
        if is_visible:
            self.ui.btnSmartSearch.setIcon(QIcon(":/icon/icons/arrow_up.png"))
            self.ui.btnSmartSearch.setObjectName("btnSmartSearchActive")
        else:
            self.ui.btnSmartSearch.setIcon(QIcon(":/icon/icons/arrow_down.png"))
            self.ui.btnSmartSearch.setObjectName("btnSmartSearch")

        self.ui.btnSmartSearch.style().unpolish(self.ui.btnSmartSearch)
        self.ui.btnSmartSearch.style().polish(self.ui.btnSmartSearch)
        self.ui.btnSmartSearch.update()

    def _toggle_pin_search_panel(self, checked):
        self._search_panel_pinned = checked
        
        # Обновляем иконку кнопки закрепления
        if checked:
            self.btn_pin.setIcon(QIcon(":/icon/icons/pin_on.png"))
            self.btn_pin.setToolTip("Открепить панель поиска")
            
            # Если панель скрыта, но нажали кнопку закрепления, показываем панель
            if not self.ui.searchPanelContainer.isVisible():
                self._toggle_search_panel()
        else:
            self.btn_pin.setIcon(QIcon(":/icon/icons/pin_off.png"))
            self.btn_pin.setToolTip("Закрепить панель поиска")
        
        # Обновляем состояние кнопки поиска
        self._update_search_button_state()

    # Метод для добавления записи в MainWindow
    def _show_add_record_dialog(self, record_data=None):
        """Метод для добавления или редактирования записи."""
        if self.table_controller.model is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите Excel файл.")
            return
            
        columns = self.table_controller.get_columns()
        
        # Определяем, это добавление или редактирование
        is_editing = record_data is not None and isinstance(record_data, dict)
        
        # Если это редактирование, извлекаем ID строки
        row_id = None
        if is_editing and isinstance(record_data, dict) and '__row_id__' in record_data:
            row_id = record_data['__row_id__']
            # Удаляем служебное поле из данных
            del record_data['__row_id__']
        
        # Собираем существующие значения для автозаполнения
        column_values = {}
        for column in columns:
            if column.lower() not in ["excel #", "№", "№ (порядок)"]:
                try:
                    values = self.table_controller.get_column_values(column)
                    unique_values = list(set([str(v) for v in values if v and str(v).strip()]))
                    column_values[column] = unique_values
                except:
                    column_values[column] = []
        
        # Получаем группы для поля "место работы (учёбы)"
        work_place_groups = {}
        for column in columns:
            if "место работы" in column.lower() or "учёбы" in column.lower():
                try:
                    similar_groups = self.table_controller.data_processor.analyze_column(column)
                    if similar_groups:
                        work_place_groups[column] = similar_groups
                except Exception as e:
                    print(f"Ошибка при анализе колонки: {e}")
        
        # Определяем примерную длину текста для каждой колонки
        column_max_lengths = {}
        for column in columns:
            try:
                values = self.table_controller.get_column_values(column)
                max_length = max([len(str(val)) for val in values if val]) if values else 0
                column_max_lengths[column] = max_length
            except:
                column_max_lengths[column] = 0
                
        # Создаем диалог с передачей данных записи (если редактирование)
        dialog = RecordDialog(
            columns, 
            self,
            record_data=record_data if is_editing else None,  # None для добавления, данные для редактирования
            column_max_lengths=column_max_lengths,
            column_values=column_values,
            work_place_groups=work_place_groups,
            table_controller=self.table_controller
        )
        
        # Сохраняем ID строки в диалоге для последующего использования
        if is_editing and row_id is not None:
            dialog.row_id = row_id
        
        # Устанавливаем заголовок в зависимости от режима
        dialog.setWindowTitle("Редактирование записи" if is_editing else "Добавление записи")
        
        # Запускаем диалог и обновляем список ключевых слов при успехе
        dialog.exec()
        if dialog.success:
            # Обновляем список ключевых слов для текущей колонки
            current_column = self.column_box.currentText()
            if current_column:
                self.filter_controller.on_column_change(self.column_box.currentIndex())

    def _delete_record(self, row_id):
        """Удаление записи по ID."""
        if self.table_controller.model is None:
            return
            
        # Удаляем запись по ID
        success = self.table_controller.delete_record(row_id)
        
        if success:
            # Сбрасываем режим колонки номеров в "excel"
            self.table_controller.set_number_mode("excel")
            
            # Сообщаем об успехе
            QMessageBox.information(
                self, 
                "Запись удалена", 
                "Запись успешно удалена из таблицы и изменения сохранены в Excel-файле."
            )
            
            # Обновляем список ключевых слов
            current_column = self.column_box.currentText()
            if current_column:
                self.filter_controller.on_column_change(self.column_box.currentIndex())
        else:
            # Сообщаем об ошибке
            QMessageBox.critical(
                self, 
                "Ошибка удаления", 
                "Не удалось удалить запись. Возможно, Excel-файл заблокирован для записи или открыт в другой программе."
            )
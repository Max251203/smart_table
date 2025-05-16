from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool
from views.components.custom_combobox import SmartComboBox
from views.table_view import SmartTableView
from controllers.table_controller import TableController
from controllers.filter_controller import FilterController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_controllers()
        self.setup_connections()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("📊 Умная таблица с фильтром")
        self.setMinimumSize(1400, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Верхняя панель инструментов
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Компоненты панели инструментов
        self.column_label = QLabel("Колонка:")
        self.column_box = SmartComboBox()
        self.keyword_edit = SmartComboBox()
        self.keyword_edit.setEditable(True)
        
        self.search_button = QPushButton("🔍 Найти")
        self.reset_button = QPushButton("↺ Сбросить")
        self.load_button = QPushButton("📂 Загрузить Excel")

        # Добавление компонентов на панель инструментов
        toolbar.addWidget(self.column_label)
        toolbar.addWidget(self.column_box)
        toolbar.addWidget(self.keyword_edit)
        toolbar.addWidget(self.search_button)
        toolbar.addWidget(self.reset_button)
        toolbar.addWidget(self.load_button)
        toolbar.addStretch()

        # Таблица
        self.table_view = SmartTableView()

        # Добавление компонентов в главный layout
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.table_view)

    def setup_controllers(self):
        """Инициализация контроллеров"""
        self.table_controller = TableController(self.table_view)
        self.filter_controller = FilterController(
            self.column_box,
            self.keyword_edit,
            self.table_controller
        )
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)  # Ограничиваем количество потоков

    def setup_connections(self):
        """Настройка сигналов и слотов"""
        self.load_button.clicked.connect(self.load_excel)
        self.search_button.clicked.connect(self.filter_controller.apply_filter)
        self.reset_button.clicked.connect(self.filter_controller.reset_filter)
        self.column_box.currentIndexChanged.connect(self.filter_controller.on_column_change)
        self.keyword_edit.lineEdit().returnPressed.connect(self.filter_controller.apply_filter)
        self.table_view.numberModeChanged.connect(self.table_controller.toggle_number_mode)

    def load_excel(self):
        """Загрузка Excel файла"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Открыть Excel файл",
                "",
                "Excel Files (*.xlsx *.xls)"
            )
            
            if file_path:
                if self.table_controller.load_file(file_path):
                    self.filter_controller.update_columns(self.table_controller.get_columns())
                else:
                    QMessageBox.warning(
                        self,
                        "Предупреждение",
                        "Файл загружен, но возможны проблемы с форматом данных"
                    )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить файл: {str(e)}"
            )

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.threadpool.clear()  # Очищаем пул потоков перед закрытием
        super().closeEvent(event)
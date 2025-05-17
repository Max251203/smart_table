from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from ui.Main.main_ui import Ui_MainWindow
from controllers.table_controller import TableController
from controllers.filter_controller import FilterController
from ui.components.custom_combobox import SmartComboBox
from ui.components.table_view import SmartTableView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._init_custom_widgets()
        self._init_controllers()
        self._connect_signals()

    def _init_custom_widgets(self):
        # Подменяем comboBox на SmartComboBox
        self.column_box = SmartComboBox()
        self.keyword_box = SmartComboBox()
        self.keyword_box.setEditable(True)

        self.ui.toolbarLayout.replaceWidget(self.ui.comboColumns, self.column_box)
        self.ui.toolbarLayout.replaceWidget(self.ui.comboKeywords, self.keyword_box)
        self.ui.comboColumns.deleteLater()
        self.ui.comboKeywords.deleteLater()

        # Подменяем tableView на SmartTableView
        self.table_view = SmartTableView()
        self.ui.mainLayout.replaceWidget(self.ui.tableView, self.table_view)
        self.ui.tableView.deleteLater()

    def _init_controllers(self):
        self.table_controller = TableController(self.table_view)
        self.filter_controller = FilterController(
            column_box=self.column_box,
            keyword_edit=self.keyword_box,
            table_controller=self.table_controller,
        )

    def _connect_signals(self):
        self.ui.btnLoad.clicked.connect(self._load_excel)
        self.ui.btnSearch.clicked.connect(self.filter_controller.apply_filter)
        self.ui.btnReset.clicked.connect(self.filter_controller.reset_all)
        self.column_box.currentIndexChanged.connect(self.filter_controller.on_column_change)
        self.keyword_box.lineEdit().returnPressed.connect(self.filter_controller.apply_filter)
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
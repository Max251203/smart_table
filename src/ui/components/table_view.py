from PySide6.QtWidgets import QTableView, QAbstractItemView, QMenu, QDialog, QVBoxLayout, QTextEdit, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from ui.components.custom_header import SmartHeader

class CellDetailDialog(QDialog):
    def __init__(self, content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Содержимое ячейки")
        self.setModal(True)
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout(self)
        text = QTextEdit(content)
        text.setReadOnly(True)
        layout.addWidget(text)

class SmartTableView(QTableView):
    columnSelected = Signal(int)
    sortRequested = Signal(int, Qt.SortOrder)
    numberModeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.header = SmartHeader(Qt.Horizontal, self)
        self.setHorizontalHeader(self.header)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def setup_connections(self):
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.show_cell_detail)
        self.header.sortRequested.connect(self.sortRequested.emit)
        self.header.firstSectionClicked.connect(self.numberModeChanged.emit)

    def show_context_menu(self, position):
        index = self.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self)
        preview_action = menu.addAction("🔍 Просмотреть содержимое")
        copy_action = menu.addAction("📋 Копировать")
        action = menu.exec(self.viewport().mapToGlobal(position))

        if action == preview_action:
            self.show_cell_detail(index)
        elif action == copy_action:
            self.copy_cell_content(index)

    def show_cell_detail(self, index):
        if not index.isValid():
            return
        content = self.model().data(index, Qt.DisplayRole)
        dialog = CellDetailDialog(content, self)
        dialog.exec()

    def copy_cell_content(self, index):
        if not index.isValid():
            return
        content = self.model().data(index, Qt.DisplayRole)
        QApplication.clipboard().setText(content)

    def select_column(self, column_index: int):
        self.clearSelection()
        self.selectColumn(column_index)
        self.columnSelected.emit(column_index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_columns()

    def adjust_columns(self):
        if not self.model():
            return

        max_width = 350
        min_width = 60
        extra_space = 24
        font = self.font()
        metrics = QFontMetrics(font)
        limit = min(self.model().rowCount(), 100)  # Проверяем только первые 100 строк

        for col in range(self.model().columnCount()):
            max_content_width = 0
            for row in range(limit):
                idx = self.model().index(row, col)
                text = str(self.model().data(idx, Qt.DisplayRole))
                w = metrics.horizontalAdvance(text)
                if w > max_content_width:
                    max_content_width = w
            header = self.model().headerData(col, Qt.Horizontal, Qt.DisplayRole)
            header_width = metrics.horizontalAdvance(str(header)) + 24
            width = max(max_content_width, header_width) + extra_space

            if width > max_width:
                width = max_width
            elif width < min_width:
                width = min_width
            self.setColumnWidth(col, width)
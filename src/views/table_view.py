from PySide6.QtWidgets import QTableView, QAbstractItemView, QMenu, QDialog, QVBoxLayout, QTextEdit, QApplication
from PySide6.QtCore import Qt, Signal
from views.components.custom_header import SmartHeader

class CellDetailDialog(QDialog):
    """Диалог для отображения подробного содержимого ячейки"""
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
        """Настройка внешнего вида таблицы"""
        # Основные настройки таблицы
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Настройка заголовков
        self.header = SmartHeader(Qt.Horizontal, self)
        self.setHorizontalHeader(self.header)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

        # Настройка стилей
        self.setStyleSheet("""
            QTableView {
                gridline-color: #d0d0d0;
                selection-background-color: #0078d7;
                selection-color: white;
                alternate-background-color: #f5f5f5;
            }
            QTableView::item {
                padding: 5px;
            }
            QTableView::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)

    def setup_connections(self):
        """Настройка сигналов и слотов"""
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.show_cell_detail)
        self.header.sortRequested.connect(self.sortRequested.emit)
        self.header.firstSectionClicked.connect(self.numberModeChanged.emit)

    def show_context_menu(self, position):
        """Отображение контекстного меню"""
        index = self.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self)
        
        # Действия меню
        preview_action = menu.addAction("🔍 Просмотреть содержимое")
        copy_action = menu.addAction("📋 Копировать")
        
        action = menu.exec(self.viewport().mapToGlobal(position))
        
        if action == preview_action:
            self.show_cell_detail(index)
        elif action == copy_action:
            self.copy_cell_content(index)

    def show_cell_detail(self, index):
        """Показать диалог с подробным содержимым ячейки"""
        if not index.isValid():
            return
            
        content = self.model().data(index, Qt.DisplayRole)
        dialog = CellDetailDialog(content, self)
        dialog.exec()

    def copy_cell_content(self, index):
        """Копировать содержимое ячейки в буфер обмена"""
        if not index.isValid():
            return
            
        content = self.model().data(index, Qt.DisplayRole)
        QApplication.clipboard().setText(content)

    def select_column(self, column_index: int):
        """Выбрать колонку"""
        self.clearSelection()
        self.selectColumn(column_index)
        self.columnSelected.emit(column_index)

    def resizeEvent(self, event):
        """Обработка изменения размера виджета"""
        super().resizeEvent(event)
        self.adjust_columns()

    def adjust_columns(self):
        """Настройка размеров колонок"""
        total_width = self.viewport().width()
        column_count = self.model().columnCount() if self.model() else 0
        
        if column_count == 0:
            return

        # Установка минимальной ширины для колонки с номерами
        self.setColumnWidth(0, 70)
        
        # Распределение оставшегося пространства между остальными колонками
        remaining_width = total_width - 70
        if column_count > 1:
            column_width = min(max(150, remaining_width // (column_count - 1)), 400)
            for col in range(1, column_count):
                self.setColumnWidth(col, column_width)
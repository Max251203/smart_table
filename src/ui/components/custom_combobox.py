from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QListView
from PySide6.QtCore import QSize

class SmartComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(250)
        self.setMaxVisibleItems(15)
        self.setMaximumWidth(600)
        
        # Отключаем автодобавление элементов в список
        self.setInsertPolicy(QComboBox.NoInsert)

        list_view = QListView(self)
        list_view.setWordWrap(True)
        list_view.setSpacing(2)
        self.setView(list_view)

        self.setItemDelegate(ComboBoxDelegate())

    def showPopup(self):
        width = max(
            self.minimumWidth(),
            min(self.view().sizeHintForColumn(0) + 30, 600)  # ограничим ширину
        )
        self.view().setMinimumWidth(width)
        super().showPopup()

class ComboBoxDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(30)
        return size
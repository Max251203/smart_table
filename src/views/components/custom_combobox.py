from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QListView
from PySide6.QtCore import Qt, QSize

class SmartComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Базовые настройки
        self.setMinimumWidth(250)
        self.setMaxVisibleItems(15)
        self.setMaximumWidth(600)
        
        # Настройка списка
        list_view = QListView(self)
        list_view.setWordWrap(True)
        list_view.setSpacing(2)
        self.setView(list_view)
        
        # Настройка делегата
        self.setItemDelegate(ComboBoxDelegate())

        # Стили
        self.setStyleSheet("""
            QComboBox {
                padding: 5px 25px 5px 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                color: #666;
                font: 16px;
                content: "▼";
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                selection-background-color: #0078d7;
                selection-color: white;
                background: white;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 5px;
            }
        """)

    def showPopup(self):
        """Настройка размера выпадающего списка"""
        width = max(
            self.minimumWidth(),
            max(
                self.view().sizeHintForColumn(0) + 30,
                self.width()
            )
        )
        self.view().setMinimumWidth(width)
        super().showPopup()
    
    # def showPopup(self):
    #     """Настройка размера и позиции выпадающего списка"""
    #     width = max(self.width(), self.view().sizeHintForColumn(0) + 20)
    #     self.view().setFixedWidth(width)
        
    #     # Позиционируем список под комбобоксом
    #     pos = self.mapToGlobal(self.rect().bottomLeft())
    #     self.view().move(pos)
        
    #     super().showPopup()

class ComboBoxDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(30)
        return size
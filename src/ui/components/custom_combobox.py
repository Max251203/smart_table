from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QListView, QCompleter
from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtGui import QWheelEvent

class SmartComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(250)
        self.setMaxVisibleItems(15)
        
        # Отключаем автодобавление элементов в список
        self.setInsertPolicy(QComboBox.NoInsert)

        list_view = QListView(self)
        list_view.setWordWrap(True)
        list_view.setSpacing(2)
        self.setView(list_view)

        self.setItemDelegate(ComboBoxDelegate())
        
        # Блокируем прокрутку колесиком мыши
        self.setFocusPolicy(Qt.StrongFocus)
        
    def wheelEvent(self, event: QWheelEvent):
        """Переопределяем обработку события колесика мыши, чтобы заблокировать изменение выбора при прокрутке"""
        # Если выпадающий список не открыт, блокируем событие
        if not self.view().isVisible():
            event.ignore()
        else:
            # Если список открыт, разрешаем прокрутку списка
            super().wheelEvent(event)

    def setupCompleter(self, items=None):
        """Настраивает автодополнение с учетом введенного текста."""
        # Проверяем, является ли комбобокс редактируемым
        if not self.isEditable():
            return
            
        if items is None:
            items = [self.itemText(i) for i in range(self.count())]
        
        if not items:
            return
            
        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(completer)

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
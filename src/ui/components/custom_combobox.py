from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QListView, QCompleter
from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtGui import QWheelEvent, QKeyEvent

class SmartComboBox(QComboBox):
    def __init__(self, parent=None, editable=True):
        super().__init__(parent)

        self.setMinimumWidth(250)
        self.setMaxVisibleItems(15)
        
        # Отключаем автодобавление элементов в список
        self.setInsertPolicy(QComboBox.NoInsert)

        # Настраиваем представление списка
        list_view = QListView(self)
        list_view.setWordWrap(True)
        list_view.setSpacing(2)
        self.setView(list_view)

        self.setItemDelegate(ComboBoxDelegate())
        
        # Блокируем прокрутку колесиком мыши
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Всегда показываем стрелку выпадающего списка
        self.setStyleSheet("QComboBox::drop-down {subcontrol-origin: padding; subcontrol-position: top right; width: 20px;}")
        
        # Устанавливаем режим редактирования согласно параметру
        self.setEditable(editable)
        
    def wheelEvent(self, event: QWheelEvent):
        """Блокируем изменение выбора при прокрутке колесика мыши"""
        if not self.view().isVisible():
            event.ignore()
        else:
            super().wheelEvent(event)
            
    def keyPressEvent(self, event: QKeyEvent):
        """Обрабатываем клавишу Enter для автодополнения"""
        # Если нажата клавиша Enter и открыт выпадающий список автодополнения
        if self.isEditable() and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and self.completer() and self.completer().popup().isVisible():
            # Выбираем подсказку и предотвращаем дальнейшую обработку
            current_index = self.completer().popup().currentIndex()
            if current_index.isValid():
                text = self.completer().completionModel().data(current_index, Qt.DisplayRole)
                self.setCurrentText(text)
                # Закрываем выпадающий список
                self.completer().popup().hide()
                event.accept()
                return
                
        super().keyPressEvent(event)

    def showPopup(self):
        """Настраиваем отображение выпадающего списка"""
        # Адаптируем ширину выпадающего списка
        width = max(
            self.minimumWidth(),
            min(self.view().sizeHintForColumn(0) + 30, 600)
        )
        self.view().setMinimumWidth(width)
        
        # Обеспечиваем отображение выпадающего списка, даже если он пуст
        if self.count() == 0:
            self.addItem("")
            super().showPopup()
            self.removeItem(0)
        else:
            super().showPopup()
            
    def setup(self, items, editable=None):
        """Настраивает комбобокс с элементами и автодополнением"""
        # Очищаем текущие элементы
        self.clear()
        
        # Устанавливаем режим редактирования, если указан
        if editable is not None:
            self.setEditable(editable)
        
        if not items:
            return
            
        # Добавляем элементы в выпадающий список
        self.addItems(items)
        
        # Настраиваем автодополнение, если комбобокс редактируемый
        if self.isEditable():
            completer = QCompleter(items)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)  # Подсказки содержащие введенный текст
            self.setCompleter(completer)

class ComboBoxDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(30)
        return size
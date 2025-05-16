from PySide6.QtWidgets import QHeaderView, QStyleOptionButton, QStyle
from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtGui import QPainter

class SmartHeader(QHeaderView):
    sortRequested = Signal(int, Qt.SortOrder)
    firstSectionClicked = Signal()  # Изменено с Signal(int) на Signal()

    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSortIndicatorShown(True)
        self._button_rects = {}

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int):
        """Отрисовка секции заголовка с кнопками сортировки"""
        painter.save()
        
        # Получаем модель и настройки
        parent_table = self.parentWidget()
        model = parent_table.model() if parent_table else None
        num_mode = getattr(model, 'num_mode', 'excel') if model else 'excel'
        num_col_index = getattr(model, 'num_col_index', 0) if model else 0

        # Получаем текст заголовка
        text = self.model().headerData(logicalIndex, Qt.Horizontal, Qt.DisplayRole)
        
        # Рисуем текст
        text_rect = rect.adjusted(10, 0, -34, 0)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, str(text))

        # Не рисуем кнопки сортировки для колонки номеров в режиме order
        if logicalIndex == num_col_index and num_mode == "order":
            self._button_rects[logicalIndex] = (QRect(), QRect())
            painter.restore()
            return

        # Рисуем кнопки сортировки
        btn_size = 14
        y = rect.center().y() - btn_size // 2
        x = rect.right() - btn_size * 2 - 4

        up_rect = QRect(x, y, btn_size, btn_size)
        down_rect = QRect(x + btn_size, y, btn_size, btn_size)
        self._button_rects[logicalIndex] = (up_rect, down_rect)

        # Рисуем стрелки сортировки
        for rect, text in [(up_rect, "▲"), (down_rect, "▼")]:
            opt = QStyleOptionButton()
            opt.rect = rect
            opt.text = text
            opt.state = QStyle.State_Enabled
            self.style().drawControl(QStyle.CE_PushButtonLabel, opt, painter)

        painter.restore()

    def mousePressEvent(self, event):
        """Обработка клика по заголовку"""
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        
        # Проверяем клик по кнопкам сортировки
        for logicalIndex, (up_rect, down_rect) in self._button_rects.items():
            if up_rect.contains(pos):
                self.sortRequested.emit(logicalIndex, Qt.AscendingOrder)
                return
            elif down_rect.contains(pos):
                self.sortRequested.emit(logicalIndex, Qt.DescendingOrder)
                return

        # Обработка клика по колонке номеров
        logicalIndex = self.logicalIndexAt(pos)
        if logicalIndex == 0:  # Первая колонка для номеров
            if event.button() == Qt.LeftButton:
                self.firstSectionClicked.emit()
        
        super().mousePressEvent(event)

    def sizeHint(self):
        """Оптимальный размер заголовка"""
        baseSize = super().sizeHint()
        return baseSize.expandedTo(QSize(0, 30))
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QFont

class SmartHeader(QHeaderView):
    sortRequested = Signal(int, Qt.SortOrder)
    firstSectionClicked = Signal()

    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSortIndicatorShown(True)
        self._button_rects = {}
        self._current_sort_col = -1
        self._current_sort_order = Qt.AscendingOrder

    def setSortIndicator(self, col: int = -1, order: Qt.SortOrder = Qt.AscendingOrder):
        """Установить колонку сортировки или сбросить (col=-1)."""
        self._current_sort_col = col
        self._current_sort_order = order
        self.viewport().update()

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int):
        painter.save()
        parent_table = self.parentWidget()
        model = parent_table.model() if parent_table else None
        num_mode = getattr(model, 'num_mode', 'excel') if model else 'excel'
        num_col_index = getattr(model, 'num_col_index', 0) if model else 0

        text = self.model().headerData(logicalIndex, Qt.Horizontal, Qt.DisplayRole)
        text_rect = rect.adjusted(10, 0, -32, 0)
        painter.setPen(Qt.black)
        painter.setFont(self.font())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, str(text))

        if logicalIndex == num_col_index and num_mode == "order":
            self._button_rects[logicalIndex] = QRect()
            painter.restore()
            return

        btn_size = 24
        y = rect.center().y() - btn_size // 2
        x = rect.right() - btn_size - 6
        btn_rect = QRect(x, y, btn_size, btn_size)
        self._button_rects[logicalIndex] = btn_rect

        pen = QPen(QColor("#5dade2"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(btn_rect)

        painter.setPen(Qt.black)
        font = QFont(self.font())
        font.setPointSize(12)
        painter.setFont(font)

        if self._current_sort_col == logicalIndex:
            arrow = "▲" if self._current_sort_order == Qt.AscendingOrder else "▼"
            painter.drawText(btn_rect, Qt.AlignCenter, arrow)
        else:
            font.setPointSize(10)
            painter.setFont(font)
            half = btn_rect.height() // 2
            rect_up = QRect(btn_rect.left(), btn_rect.top(), btn_rect.width(), half)
            rect_dn = QRect(btn_rect.left(), btn_rect.top() + half, btn_rect.width(), half)
            painter.drawText(rect_up, Qt.AlignCenter, "▲")
            painter.drawText(rect_dn, Qt.AlignCenter, "▼")

        painter.restore()

    def mousePressEvent(self, event):
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        for logicalIndex, btn_rect in self._button_rects.items():
            if btn_rect.contains(pos):
                if self._current_sort_col == logicalIndex:
                    self._current_sort_order = (
                        Qt.DescendingOrder if self._current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
                    )
                else:
                    self._current_sort_col = logicalIndex
                    self._current_sort_order = Qt.AscendingOrder
                self.sortRequested.emit(logicalIndex, self._current_sort_order)
                self.viewport().update()
                return
        logicalIndex = self.logicalIndexAt(pos)
        if logicalIndex == 0:
            if event.button() == Qt.LeftButton:
                self.firstSectionClicked.emit()
        super().mousePressEvent(event)

    def sizeHint(self):
        baseSize = super().sizeHint()
        return baseSize.expandedTo(QSize(0, 30))
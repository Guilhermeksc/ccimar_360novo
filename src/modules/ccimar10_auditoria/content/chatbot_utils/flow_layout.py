from PyQt6.QtWidgets import QLayout, QSizePolicy
from PyQt6.QtCore import QPoint, QRect, QSize, Qt

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=5):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        # Obter as margens configuradas
        margins = self.contentsMargins()
        effectiveRect = QRect(rect.x() + margins.left(), rect.y() + margins.top(),
                               rect.width() - (margins.left() + margins.right()),
                               rect.height() - (margins.top() + margins.bottom()))
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self.itemList:
            widgetSize = item.sizeHint()
            nextX = x + widgetSize.width() + self.spacing()
            if nextX - self.spacing() > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + self.spacing()
                nextX = x + widgetSize.width() + self.spacing()
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), widgetSize))

            x = nextX
            lineHeight = max(lineHeight, widgetSize.height())

        return y + lineHeight - effectiveRect.y() + margins.bottom()

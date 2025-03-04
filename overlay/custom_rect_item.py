from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt


class CustomRectItem(QGraphicsRectItem):
    """Custom rectangle item that can detect clicks and hover effects."""

    def __init__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.click_callback = None

        # The default_pen will now be set when setPen is first called
        self.default_pen = None
        self.hover_pen = QPen(QColor("yellow"), 3)

        # Enable hover events and set the cursor shape
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def setPen(self, pen):
        # Store the first pen set as the default pen
        if self.default_pen is None:
            self.default_pen = QPen(pen)  # Create a copy of the pen
        super().setPen(pen)

    def setClickCallback(self, callback):
        """Assign the callback function for when this item is clicked."""
        self.click_callback = callback

    def hoverEnterEvent(self, event):
        # Save current pen if necessary
        if self.default_pen is None:
            self.default_pen = QPen(self.pen())
        self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # Return to the original pen color
        if self.default_pen:
            super().setPen(self.default_pen)  # Use super() to avoid our override
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if self.click_callback:
            self.click_callback()
        super().mousePressEvent(event)

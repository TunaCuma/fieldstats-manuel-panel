from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt

class CustomRectItem(QGraphicsRectItem):
    """Custom rectangle item that can detect clicks and hover effects."""
    
    def __init__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.click_callback = None
        self.default_pen = QPen(QColor("orange"), 3)
        self.hover_pen = QPen(QColor("yellow"), 3)
        self.setPen(self.default_pen)
        
        # Enable hover events and set the cursor shape.
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def setClickCallback(self, callback):
        """Assign the callback function for when this item is clicked."""
        self.click_callback = callback
        
    def hoverEnterEvent(self, event):
        self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.setPen(self.default_pen)
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        if self.click_callback:
            self.click_callback()
        super().mousePressEvent(event)

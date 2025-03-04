from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt
from .custom_rect_item import CustomRectItem


class OverlayCreator:
    """Responsible for creating overlay rectangles for different views"""

    def __init__(self, manager):
        self.manager = manager

    def create_overlays(self):
        """Create overlay rectangles for all views"""
        self.create_topdown_overlays()
        self.create_left_overlays()
        self.create_right_overlays()

    def create_topdown_overlays(self):
        """Create overlays for transformed view (bottom)"""
        max_overlays = 30

        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            orange_pen = QPen(QColor("orange"), 3)
            rect.setPen(orange_pen)
            self.manager.topdown_overlays.append(rect)
            self.manager.player.transform_view.scene.addItem(rect)
            rect.setVisible(False)

    def create_left_overlays(self):
        """Create overlays for left field view"""
        max_overlays = 30

        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            red_pen = QPen(QColor("red"), 3)
            rect.setPen(red_pen)
            self.manager.left_overlays.append(rect)
            self.manager.player.left_view.scene.addItem(rect)
            rect.setVisible(False)

    def create_right_overlays(self):
        """Create overlays for right field view"""
        max_overlays = 30

        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            blue_pen = QPen(QColor("blue"), 3)
            rect.setPen(blue_pen)
            self.manager.right_overlays.append(rect)
            self.manager.player.right_view.scene.addItem(rect)
            rect.setVisible(False)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPen

from .custom_rect_item import CustomRectItem


class DetachedOverlayManager:
    """Manages the creation and deletion of overlays for detached windows."""

    def __init__(self, manager):
        self.manager = manager

    def create_detached_left_overlays(self):
        """Create overlays for detached left field view."""
        if not self.manager.player.left_view.detached_window:
            return

        # Clean any existing overlays
        self.clean_detached_left_overlays()

        # Create new overlays
        max_overlays = 30
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            red_pen = QPen(QColor("red"), 3)
            rect.setPen(red_pen)
            self.manager.detached_left_overlays.append(rect)
            self.manager.player.left_view.detached_window.scene.addItem(rect)
            rect.setVisible(False)

    def create_detached_right_overlays(self):
        """Create overlays for detached right field view."""
        if not self.manager.player.right_view.detached_window:
            return

        # Clean any existing overlays
        self.clean_detached_right_overlays()

        # Create new overlays
        max_overlays = 30
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            blue_pen = QPen(QColor("blue"), 3)
            rect.setPen(blue_pen)
            self.manager.detached_right_overlays.append(rect)
            self.manager.player.right_view.detached_window.scene.addItem(rect)
            rect.setVisible(False)

    def create_detached_transform_overlays(self):
        """Create overlays for detached transform view."""
        if not self.manager.player.transform_view.detached_window:
            return

        # Clean any existing overlays
        self.clean_detached_transform_overlays()

        # Create new overlays
        max_overlays = 30
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            orange_pen = QPen(QColor("orange"), 3)
            rect.setPen(orange_pen)
            self.manager.detached_topdown_overlays.append(rect)
            self.manager.player.transform_view.detached_window.scene.addItem(rect)
            rect.setVisible(False)

    def clean_detached_left_overlays(self):
        """Clean overlays from detached left field view."""
        for rect in self.manager.detached_left_overlays:
            if rect.scene():
                rect.scene().removeItem(rect)
        self.manager.detached_left_overlays.clear()

    def clean_detached_right_overlays(self):
        """Clean overlays from detached right field view."""
        for rect in self.manager.detached_right_overlays:
            if rect.scene():
                rect.scene().removeItem(rect)
        self.manager.detached_right_overlays.clear()

    def clean_detached_transform_overlays(self):
        """Clean overlays from detached transform view."""
        for rect in self.manager.detached_topdown_overlays:
            if rect.scene():
                rect.scene().removeItem(rect)
        self.manager.detached_topdown_overlays.clear()

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal


class ViewBase(QWidget):
    """Base class for all video view widgets with common functionality"""
    
    # Signals
    toggledVisibility = pyqtSignal(bool)
    detachRequested = pyqtSignal()
    reattachRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_visible = True
        self.is_detached = False
    
    def toggle_visibility(self):
        """Toggle the visibility of this view"""
        self.is_visible = not self.is_visible
        self.setVisible(self.is_visible)
        self.toggledVisibility.emit(self.is_visible)
    
    def set_visible(self, visible):
        """Set the visibility to a specific state"""
        if self.is_visible != visible:
            self.toggle_visibility()
    
    def detach(self):
        """Detach this view to a separate window"""
        if not self.is_detached:
            self.is_detached = True
            self.detachRequested.emit()
    
    def reattach(self):
        """Reattach this view from a separate window"""
        if self.is_detached:
            self.is_detached = False
            self.reattachRequested.emit()

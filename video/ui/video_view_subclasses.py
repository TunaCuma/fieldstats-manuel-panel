from PyQt6.QtCore import pyqtSignal

from .video_view import VideoView


class LeftFieldView(VideoView):
    """Video view specifically for the left field camera"""

    detachRequested = pyqtSignal()
    reattachRequested = pyqtSignal()

    def __init__(self):
        super().__init__("Left Field", "red")

    def emit_detach_request(self):
        """Signal to parent that this view needs to be detached"""
        self.detachRequested.emit()

    def emit_reattach_request(self):
        """Signal to parent that this view needs to be reattached"""
        self.reattachRequested.emit()


class RightFieldView(VideoView):
    """Video view specifically for the right field camera"""

    detachRequested = pyqtSignal()
    reattachRequested = pyqtSignal()

    def __init__(self):
        super().__init__("Right Field", "blue")

    def emit_detach_request(self):
        """Signal to parent that this view needs to be detached"""
        self.detachRequested.emit()

    def emit_reattach_request(self):
        """Signal to parent that this view needs to be reattached"""
        self.reattachRequested.emit()


class TransformView(VideoView):
    """Video view specifically for the transformed view"""

    detachRequested = pyqtSignal()
    reattachRequested = pyqtSignal()

    def __init__(self):
        super().__init__("Transformed View", "orange")

    def emit_detach_request(self):
        """Signal to parent that this view needs to be detached"""
        self.detachRequested.emit()

    def emit_reattach_request(self):
        """Signal to parent that this view needs to be reattached"""
        self.reattachRequested.emit()

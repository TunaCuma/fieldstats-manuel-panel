from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import pyqtSignal

from .video_header import VideoHeader
from .video_content import VideoContent


class VideoView(QWidget):
    """A self-contained widget for displaying a video with controls"""

    videoResized = pyqtSignal()
    toggledVisibility = pyqtSignal(bool)
    detachRequested = pyqtSignal()
    reattachRequested = pyqtSignal()

    def __init__(self, title, color="white"):
        super().__init__()
        self.is_visible = True
        self.title = title
        self.color = color
        self.detached_window = None

        self.setupUI()

    def setupUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create header with title and controls
        self.header = VideoHeader(self.title, self.color)
        self.header.hideRequested.connect(self.toggle_visibility)
        self.header.detachRequested.connect(self.detach_view)
        self.layout.addWidget(self.header)

        # Create content area
        self.content = VideoContent()
        self.content.customContextMenuRequested(self.show_context_menu)
        self.layout.addWidget(self.content)

        # Setup sizing policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)

    def show_context_menu(self, pos):
        """Show context menu for the video view"""
        from .context_menu import create_video_view_context_menu

        menu = create_video_view_context_menu(self)
        menu.exec(self.content.view.mapToGlobal(pos))

    def toggle_visibility(self):
        """Toggle the visibility of the video content"""
        self.is_visible = not self.is_visible
        self.content.setVisible(self.is_visible)

        # Update header state
        self.header.update_visibility_state(self.is_visible)

        # Update size policy based on visibility
        if self.is_visible:
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.setMinimumSize(100, 100)
        else:
            self.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Minimum)
            self.setMinimumSize(0, self.header.height())

        # Emit signal for parent containers to adjust
        self.toggledVisibility.emit(self.is_visible)

        # Explicitly update UI
        self.updateGeometry()

    def detach_view(self):
        """Detach video view to a separate window"""
        from .detached_video_window import DetachedVideoWindow

        # Create detached window if it doesn't exist
        if not self.detached_window:
            self.detached_window = DetachedVideoWindow(self.title, self)
            self.detached_window.closed.connect(self.reattach_view)

            # Hide content but keep header
            self.content.setVisible(False)
            self.header.disable_detach_button()

            # Set minimal size to just the header
            self.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Minimum)
            self.setMinimumSize(0, self.header.height())

            # Signal to parent VideoPlayer
            self.detachRequested.emit()

            self.detached_window.show()

    def set_detached_video_output(self, media_player):
        """Set the detached window's video item as output for the media player"""
        if self.detached_window:
            media_player.setVideoOutput(self.detached_window.video_item)

    def reattach_view(self):
        """Reattach the video view after the detached window is closed"""
        self.detached_window = None

        # Restore view visibility if it was visible before
        if self.is_visible:
            self.content.setVisible(True)
            # Restore size policy
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.setMinimumSize(100, 100)

        self.header.enable_detach_button()

        # Signal that we need to restore the video output
        self.reattachRequested.emit()

    def resizeEvent(self, event):
        """Handle resize events to maintain proper video scaling"""
        super().resizeEvent(event)
        self.update_video_size()
        self.videoResized.emit()

    def update_video_size(self):
        """Update video size while maintaining aspect ratio"""
        if not self.is_visible:
            return

        self.content.update_video_size()

    def set_visible(self, visible):
        """Public method to programmatically set visibility"""
        if self.is_visible != visible:
            self.toggle_visibility()

    @property
    def video_item(self):
        """Access to video item for external connections"""
        return self.content.video_item

    @property
    def actual_video_rect(self):
        """Access to actual video rectangle dimensions"""
        return self.content.actual_video_rect

    @property
    def scene(self):
        """Access to video scene for external components"""
        return self.content.scene

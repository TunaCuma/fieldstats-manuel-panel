from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QGraphicsScene, QGraphicsView, QPushButton, QMenu, QFrame
)
from PyQt6.QtCore import Qt, QSizeF, pyqtSignal
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtGui import QAction, QIcon

class VideoView(QWidget):
    """A self-contained widget for displaying a video with controls"""
    videoResized = pyqtSignal()
    toggledVisibility = pyqtSignal(bool)
    
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
        
        # Header with title and controls
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(5, 2, 5, 2)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"font-weight: bold; color: {self.color};")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.header_layout.addWidget(self.title_label)
        
        # Status label (for showing "Hidden" when view is hidden)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.header_layout.addWidget(self.status_label)
        
        # Spacer
        self.header_layout.addStretch()
        
        # Control buttons
        self.pop_out_btn = QPushButton("⇱")  # Unicode for pop-out
        self.pop_out_btn.setToolTip("Detach to new window")
        self.pop_out_btn.setFixedSize(24, 24)
        self.pop_out_btn.clicked.connect(self.detach_view)
        self.header_layout.addWidget(self.pop_out_btn)
        
        self.hide_btn = QPushButton("−")  # Unicode for minus
        self.hide_btn.setToolTip("Hide panel")
        self.hide_btn.setFixedSize(24, 24)
        self.hide_btn.clicked.connect(self.toggle_visibility)
        self.header_layout.addWidget(self.hide_btn)
        
        self.layout.addWidget(self.header)
        
        # Container for video content (to easily hide/show)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Graphics view for video
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: black; padding: 0px; margin: 0px;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame
        
        # Video item
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        
        self.content_layout.addWidget(self.view)
        self.layout.addWidget(self.content_container)
        
        # Context menu
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Setup sizing policy for collapsed state
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def show_context_menu(self, pos):
        """Show context menu for the video view"""
        context_menu = QMenu(self)
        
        # Add actions
        detach_action = QAction("Detach to window", self)
        detach_action.triggered.connect(self.detach_view)
        context_menu.addAction(detach_action)
        
        # Change text based on current visibility
        visibility_text = "Show panel" if not self.is_visible else "Hide panel"
        hide_action = QAction(visibility_text, self)
        hide_action.triggered.connect(self.toggle_visibility)
        context_menu.addAction(hide_action)
        
        # Show the menu
        context_menu.exec(self.view.mapToGlobal(pos))
    
    def toggle_visibility(self):
        """Toggle the visibility of the video content"""
        self.is_visible = not self.is_visible
        self.content_container.setVisible(self.is_visible)
        
        # Update button text and status
        if self.is_visible:
            self.hide_btn.setText("−")  # Unicode for minus
            self.hide_btn.setToolTip("Hide panel")
            self.status_label.setText("")
            # Restore expanded size policy
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            self.hide_btn.setText("＋")  # Unicode for plus
            self.hide_btn.setToolTip("Show panel")
            self.status_label.setText("[Hidden]")
            # Collapse size when hidden
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Emit signal for parent containers to adjust
        self.toggledVisibility.emit(self.is_visible)
        
        # Explicitly update UI to fix any layout issues
        self.updateGeometry()
    
    def detach_view(self):
        """Detach video view to a separate window"""
        from detached_video_window import DetachedVideoWindow
        
        # Create detached window if it doesn't exist
        if not self.detached_window:
            self.detached_window = DetachedVideoWindow(self.title, self)
            self.detached_window.closed.connect(self.reattach_view)
            
            # Hide this view while it's detached
            self.content_container.setVisible(False)
            self.pop_out_btn.setEnabled(False)
            
            # We need to access the video player that this view belongs to
            # This signal will be caught by the parent VideoPlayer
            self.emit_detach_request()
            
            self.detached_window.show()
    
    def emit_detach_request(self):
        """Signal to parent that this view needs to be detached"""
        # This will be implemented by subclasses to emit the appropriate signal
        pass
    
    def set_detached_video_output(self, media_player):
        """Set the detached window's video item as output for the media player"""
        if self.detached_window:
            media_player.setVideoOutput(self.detached_window.video_item)
    
    def reattach_view(self):
        """Reattach the video view after the detached window is closed"""
        self.detached_window = None
        if self.is_visible:
            self.content_container.setVisible(True)
        self.pop_out_btn.setEnabled(True)
        
        # Signal that we need to restore the video output
        self.emit_reattach_request()
    
    def emit_reattach_request(self):
        """Signal to parent that this view needs to be reattached"""
        # This will be implemented by subclasses to emit the appropriate signal
        pass
    
    def resizeEvent(self, event):
        """Handle resize events to maintain proper video scaling"""
        super().resizeEvent(event)
        self.update_video_size()
        self.videoResized.emit()
    
    def update_video_size(self):
        """Update video size while maintaining aspect ratio"""
        if not self.is_visible:
            return
            
        view_size = self.view.size()
        self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())
        
        # Get the video item size
        video_size = self.video_item.size()
        
        # If we have a valid video size, scale it
        if video_size.width() > 0 and video_size.height() > 0:
            # Calculate scale to maintain aspect ratio
            scale = min(
                view_size.width() / video_size.width(),
                view_size.height() / video_size.height()
            )
            
            new_width = video_size.width() * scale
            new_height = video_size.height() * scale
            
            # Center the video
            x_offset = (view_size.width() - new_width) / 2
            y_offset = (view_size.height() - new_height) / 2
            
            self.video_item.setPos(x_offset, y_offset)
            self.video_item.setSize(QSizeF(new_width, new_height))
        else:
            # No valid video size, use view size
            self.video_item.setSize(QSizeF(view_size.width(), view_size.height()))
    
    def set_visible(self, visible):
        """Public method to programmatically set visibility"""
        if self.is_visible != visible:
            self.toggle_visibility()

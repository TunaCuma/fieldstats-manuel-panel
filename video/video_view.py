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
            self.setMinimumSize(100, 100)  # Restore minimum size
        else:
            self.hide_btn.setText("＋")  # Unicode for plus
            self.hide_btn.setToolTip("Show panel")
            self.status_label.setText("[Hidden]")
            # Collapse size when hidden
            self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
            self.setMinimumSize(0, self.header.height())  # Only header height needed
        
        # Emit signal for parent containers to adjust
        self.toggledVisibility.emit(self.is_visible)
        
        # Explicitly update UI to fix any layout issues
        self.updateGeometry()
    
    def detach_view(self):
        """Detach video view to a separate window"""
        from .detached_video_window import DetachedVideoWindow
        
        # Create detached window if it doesn't exist
        if not self.detached_window:
            self.detached_window = DetachedVideoWindow(self.title, self)
            self.detached_window.closed.connect(self.reattach_view)
            
            # Hide content but keep header
            self.content_container.setVisible(False)
            self.pop_out_btn.setEnabled(False)
            
            # Set minimal size to just the header
            self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
            self.setMinimumSize(0, self.header.height())
            
            # We need to access the video player that this view belongs to
            # This signal will be caught by the parent VideoPlayer
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
            self.content_container.setVisible(True)
            # Restore size policy
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setMinimumSize(100, 100)
        
        self.pop_out_btn.setEnabled(True)
        
        # Signal that we need to restore the video output
        self.reattachRequested.emit()
    
    def resizeEvent(self, event):
        """Handle resize events to maintain proper video scaling"""
        super().resizeEvent(event)
        self.update_video_size()
        self.videoResized.emit()
    
    def update_video_size(self):
        """Update video size while maintaining aspect ratio and tracking actual video size for overlays"""
        if not self.is_visible:
            return
                
        # Get the size of the view
        view_size = self.view.size()
        
        # Update the scene rectangle to match the view size
        self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())
        
        # Get the video item's native size (actual media dimensions)
        video_native_size = self.video_item.nativeSize()
        
        # If video has a valid native size, use it for aspect ratio calculations
        if video_native_size.width() > 0 and video_native_size.height() > 0:
            # Calculate scale to maintain aspect ratio while filling the view
            scale = min(
                view_size.width() / video_native_size.width(),
                view_size.height() / video_native_size.height()
            )
            
            # Calculate new dimensions
            new_width = video_native_size.width() * scale
            new_height = video_native_size.height() * scale
            
            # Center the video in the view
            x_offset = (view_size.width() - new_width) / 2
            y_offset = (view_size.height() - new_height) / 2
            
            # Set position and size
            self.video_item.setPos(x_offset, y_offset)
            self.video_item.setSize(QSizeF(new_width, new_height))
            
            # Store actual video display dimensions and offsets for overlay positioning
            self.actual_video_rect = {
                'x': x_offset,
                'y': y_offset,
                'width': new_width,
                'height': new_height,
                'scale': scale  # Store the scale factor for overlay scaling
            }
        else:
            # If no valid video size, set to view size and position at origin
            self.video_item.setSize(QSizeF(view_size.width(), view_size.height()))
            self.video_item.setPos(0, 0)
            
            # In this case, overlay should use the full view
            self.actual_video_rect = {
                'x': 0,
                'y': 0,
                'width': view_size.width(),
                'height': view_size.height(),
                'scale': 1.0
            }
            
        # Ensure view update
        self.view.update()
    
    def set_visible(self, visible):
        """Public method to programmatically set visibility"""
        if self.is_visible != visible:
            self.toggle_visibility()

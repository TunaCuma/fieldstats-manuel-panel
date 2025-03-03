from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView, QLabel, QFrame
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import Qt, QSizeF, pyqtSignal

class DetachedVideoWindow(QMainWindow):
    """A window for displaying detached video views"""
    closed = pyqtSignal()
    videoResized = pyqtSignal()
    
    def __init__(self, title, parent_view=None):
        super().__init__()
        self.parent_view = parent_view
        self.setWindowTitle(f"Detached: {title}")
        self.setGeometry(100, 100, 640, 480)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; color: orange; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        # Graphics scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: black; padding: 0px; margin: 0px;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame
        
        # Video item
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        
        self.layout.addWidget(self.view)
    
    def resizeEvent(self, event):
        """Handle resize events to maintain proper video scaling"""
        super().resizeEvent(event)
        self.update_video_size()
        self.videoResized.emit()
    
    def update_video_size(self):
        """Update video size while maintaining aspect ratio"""
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
        
        # Signal that overlays need to be updated
        if self.parent_view and hasattr(self.parent_view, "parent"):
            if hasattr(self.parent_view.parent(), "viewResized"):
                self.parent_view.parent().viewResized.emit()
    
    def closeEvent(self, event):
        """Handle window close event to notify parent"""
        self.closed.emit()
        super().closeEvent(event)

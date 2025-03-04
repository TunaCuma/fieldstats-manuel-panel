from PyQt6.QtCore import QSizeF, Qt, QTimer, pyqtSignal
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class DetachedVideoWindow(QMainWindow):
    """A window for displaying detached video views."""

    closed = pyqtSignal()
    videoResized = pyqtSignal()

    def __init__(self, title, parent_view=None):
        super().__init__()
        self.parent_view = parent_view
        self.setWindowTitle(f"Detached: {title}")
        self.setGeometry(100, 100, 640, 480)

        # Initialize actual_video_rect for overlay positioning
        self.actual_video_rect = {"x": 0, "y": 0, "width": 0, "height": 0, "scale": 1.0}

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "font-weight: bold; color: orange; font-size: 14px;"
        )
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

        # Add a timer to ensure proper initialization
        self.init_timer = QTimer(self)
        self.init_timer.setSingleShot(True)
        self.init_timer.timeout.connect(self.initial_update)
        self.init_timer.start(100)  # Short delay after UI setup

    def initial_update(self):
        """Force an initial update to ensure video sizes and overlays are
        correct."""
        self.update_video_size()
        self.videoResized.emit()

    def resizeEvent(self, event):
        """Handle resize events to maintain proper video scaling."""
        super().resizeEvent(event)
        self.update_video_size()
        self.videoResized.emit()

    def update_video_size(self):
        """Update video size while maintaining aspect ratio and tracking for
        overlays."""
        view_size = self.view.size()
        self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())

        # Get the video item's native size (actual media dimensions)
        video_native_size = self.video_item.nativeSize()

        # If video has a valid native size, use it for aspect ratio calculations
        if video_native_size.width() > 0 and video_native_size.height() > 0:
            # Calculate scale to maintain aspect ratio while filling the view
            scale = min(
                view_size.width() / video_native_size.width(),
                view_size.height() / video_native_size.height(),
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
                "x": x_offset,
                "y": y_offset,
                "width": new_width,
                "height": new_height,
                "scale": scale,  # Store the scale factor for overlay scaling
            }
        else:
            # If no valid video size, set to view size and position at origin
            self.video_item.setSize(QSizeF(view_size.width(), view_size.height()))
            self.video_item.setPos(0, 0)

            # In this case, overlay should use the full view
            self.actual_video_rect = {
                "x": 0,
                "y": 0,
                "width": view_size.width(),
                "height": view_size.height(),
                "scale": 1.0,
            }

        # Ensure view update
        self.view.update()

        # Signal that overlays need to be updated
        if self.parent_view and hasattr(self.parent_view, "parent"):
            if hasattr(self.parent_view.parent(), "viewResized"):
                self.parent_view.parent().viewResized.emit()

    def closeEvent(self, event):
        """Handle window close event to notify parent."""
        self.closed.emit()
        super().closeEvent(event)

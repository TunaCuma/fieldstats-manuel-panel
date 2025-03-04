from PyQt6.QtCore import QSizeF, Qt
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class VideoContent(QWidget):
    """Widget containing the video display area."""

    def __init__(self):
        super().__init__()
        self.actual_video_rect = {"x": 0, "y": 0, "width": 0, "height": 0, "scale": 1.0}
        self.setupUI()

    def setupUI(self):
        # Content layout
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Graphics view for video
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: black; padding: 0px; margin: 0px;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame

        # Video item
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        self.content_layout.addWidget(self.view)

        # Setup context menu
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def customContextMenuRequested(self, pos):
        """Connect to view's context menu signal."""
        self.view.customContextMenuRequested.connect(pos)

    def update_video_size(self):
        """Update video size while maintaining aspect ratio and tracking actual
        video size for overlays."""
        # Get the size of the view
        view_size = self.view.size()

        # Update the scene rectangle to match the view size
        self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())

        # Get the video item's native size (actual media dimensions)
        video_native_size = self.video_item.nativeSize()

        # If video has a valid native size, use it for aspect ratio
        # calculations
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

            # Store actual video display dimensions and offsets for overlay
            # positioning
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

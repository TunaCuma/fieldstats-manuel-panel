from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from typing_extensions import override

from .handlers.media_handler import MediaHandler
from .handlers.menu_handler import MenuHandler
from .handlers.playback_controller import PlaybackController
from .handlers.view_handler import ViewHandler
from .layout.layout_manager import LayoutManager
from .player.video_player_property_bridge import VideoPlayerPropertyBridge
from .player.video_player_signal_connector import VideoPlayerSignalConnector
from .ui.video_controls import VideoControls
from .ui.video_view_subclasses import LeftFieldView, RightFieldView, TransformView
from .utils.media_synchronizer import MediaSynchronizer


class VideoPlayer(QMainWindow):
    """Main video player application class that orchestrates all components.

    This class has been refactored to delegate functionality to
    specialized handler classes.
    """

    viewResized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Analysis Player")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize central widget and layout
        self._setup_main_layout()

        # Initialize property bridge
        self.prop_bridge = VideoPlayerPropertyBridge(self)

        # Setup UI components and handlers
        self._setup_ui_components()
        self._setup_handlers()

        # Setup signal connections
        self.signal_connector = VideoPlayerSignalConnector(self)
        self.signal_connector.connect_all_signals()

        # Expose media players for external access (for backward compatibility)
        self.media_player = self.media_handler.main_player
        self.left_player = self.media_handler.left_player
        self.right_player = self.media_handler.right_player

        # Setup timer for UI updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ui)
        self.timer.start(100)

    def _setup_main_layout(self):
        """Initialize the main window layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def _setup_ui_components(self):
        """Set up all UI components."""
        # Create layout manager
        self.layout_manager = LayoutManager()
        self.main_layout.addWidget(self.layout_manager)

        # Create video views
        self.left_view = LeftFieldView()
        self.right_view = RightFieldView()
        self.transform_view = TransformView()

        # Add views to layout manager
        self.layout_manager.add_left_view(self.left_view)
        self.layout_manager.add_right_view(self.right_view)
        self.layout_manager.add_transform_view(self.transform_view)

        # Create controls
        self.controls = VideoControls()
        self.main_layout.addWidget(self.controls)

        # Reference to click_info_label for JSONOverlayManager
        self.click_info_label = self.controls.click_info_label

        # Setup status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def _setup_handlers(self):
        """Set up all handler classes."""
        # Setup media synchronizer
        self.synchronizer = MediaSynchronizer()

        # Setup handlers
        self.media_handler = MediaHandler(
            self.transform_view,
            self.left_view,
            self.right_view,
            self.synchronizer,
            self.statusBar,
            self.controls,
            self,
        )

        self.menu_handler = MenuHandler(
            self, self.media_handler.open_videos, self.media_handler.open_project
        )

        self.view_handler = ViewHandler(
            self.left_view,
            self.right_view,
            self.transform_view,
            self.media_handler.left_player,
            self.media_handler.right_player,
            self.media_handler.main_player,
            self.statusBar,
            self.viewResized,
        )

        self.playback_controller = PlaybackController(
            self.synchronizer,
            self.controls,
            self.media_handler.main_player,
            self.statusBar,
            self.view_handler.handle_view_resized,
        )

    def _update_ui(self):
        """Update UI periodically."""
        # Delegate to playback controller
        self.playback_controller.update_ui()

        # Sync properties from handlers to maintain compatibility with external
        # code
        self.prop_bridge.sync_properties()

    def load_videos(self, transform_path, left_path, right_path):
        """Load all three videos and synchronize them."""
        self.media_handler.load_videos(transform_path, left_path, right_path)

    @override
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.view_handler.handle_view_resized()

    # Property proxies - forward to property bridge
    @property
    def current_frame(self):
        return self.prop_bridge.current_frame

    @property
    def total_frames(self):
        return self.prop_bridge.total_frames

    @property
    def fps(self):
        return self.prop_bridge.fps

    @property
    def duration(self):
        return self.prop_bridge.duration

    @property
    def position(self):
        return self.prop_bridge.position

    @property
    def is_playing(self):
        return self.prop_bridge.is_playing

    @property
    def frame_duration(self):
        return self.prop_bridge.frame_duration

    @property
    def is_left_visible(self):
        return self.prop_bridge.is_left_visible

    @property
    def is_right_visible(self):
        return self.prop_bridge.is_right_visible

    @property
    def is_transform_visible(self):
        return self.prop_bridge.is_transform_visible

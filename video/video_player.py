import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QStatusBar, QMenuBar
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from .layout_manager import LayoutManager
from .media_synchronizer import MediaSynchronizer
from .video_controls import VideoControls
from .video_view_subclasses import LeftFieldView, RightFieldView, TransformView
from .menu_handler import MenuHandler
from .media_handler import MediaHandler
from .view_handler import ViewHandler
from .playback_controller import PlaybackController

class VideoPlayer(QMainWindow):
    viewResized = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Analysis Player")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize properties that might be accessed by external components
        self._current_frame = 0
        self._total_frames = 0
        self._fps = 30
        self._frame_duration = 33.33
        self._is_playing = False
        self._duration = 0
        
        # View visibility flags
        self._is_left_visible = True
        self._is_right_visible = True
        self._is_transform_visible = True
        
        # Setup central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Setup UI components
        self._setup_ui_components()
        
        # Setup handlers
        self._setup_handlers()
        
        # Connect signals
        self._connect_signals()
        
        # Setup timer for UI updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)
        
        # Expose media players for external access
        self.media_player = self.media_handler.main_player
        self.left_player = self.media_handler.left_player
        self.right_player = self.media_handler.right_player

    def _setup_ui_components(self):
        """Set up all UI components"""
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
        """Set up all handler classes"""
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
            self
        )
        
        self.menu_handler = MenuHandler(
            self,
            self.media_handler.open_videos,
            self.media_handler.open_project
        )
        
        self.view_handler = ViewHandler(
            self.left_view,
            self.right_view,
            self.transform_view,
            self.media_handler.left_player,
            self.media_handler.right_player,
            self.media_handler.main_player,
            self.statusBar,
            self.viewResized
        )
        
        self.playback_controller = PlaybackController(
            self.synchronizer,
            self.controls,
            self.media_handler.main_player,
            self.statusBar,
            self.view_handler.handle_view_resized
        )
        
    def _connect_signals(self):
        """Connect all signals between components"""
        # Connect layout manager signals
        self.layout_manager.viewResized.connect(self.view_handler.handle_view_resized)
        
        # Connect control signals to playback controller
        self.controls.playPauseClicked.connect(self.playback_controller.play_pause)
        self.controls.stopClicked.connect(self.playback_controller.stop)
        self.controls.prevFrameClicked.connect(self.playback_controller.previous_frame)
        self.controls.nextFrameClicked.connect(self.playback_controller.next_frame)
        self.controls.sliderMoved.connect(self.playback_controller.set_position)
        self.controls.goToFrameRequested.connect(self.playback_controller.go_to_frame)
        
        # Connect view toggle signals
        self.menu_handler.toggleLeftAction.triggered.connect(self.view_handler.toggle_left_field)
        self.menu_handler.toggleRightAction.triggered.connect(self.view_handler.toggle_right_field)
        self.menu_handler.toggleTransformAction.triggered.connect(self.view_handler.toggle_transform_view)
        self.menu_handler.showAllViewsAction.triggered.connect(self.view_handler.show_all_views)
        self.menu_handler.manageViewsAction.triggered.connect(self.view_handler.show_view_control_dialog)
        
        # Connect detach/reattach signals
        self.left_view.detachRequested.connect(self.view_handler.handle_left_detach)
        self.right_view.detachRequested.connect(self.view_handler.handle_right_detach)
        self.transform_view.detachRequested.connect(self.view_handler.handle_transform_detach)
        
        self.left_view.reattachRequested.connect(self.view_handler.handle_left_reattach)
        self.right_view.reattachRequested.connect(self.view_handler.handle_right_reattach)
        self.transform_view.reattachRequested.connect(self.view_handler.handle_transform_reattach)
        
        # Connect visibility signals
        self.left_view.toggledVisibility.connect(self.view_handler.handle_left_visibility)
        self.right_view.toggledVisibility.connect(self.view_handler.handle_right_visibility)
        self.transform_view.toggledVisibility.connect(self.view_handler.handle_transform_visibility)
        
        # Connect resize signals
        self.left_view.videoResized.connect(self.view_handler.handle_view_resized)
        self.right_view.videoResized.connect(self.view_handler.handle_view_resized)
        self.transform_view.videoResized.connect(self.view_handler.handle_view_resized)
    
    def update_ui(self):
        """Update UI periodically"""
        # Delegate to playback controller
        self.playback_controller.update_ui()
        
        # Sync properties from handlers to maintain compatibility with external code
        self._sync_properties()
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.view_handler.handle_view_resized()
        
    def load_videos(self, transform_path, left_path, right_path):
        """Load all three videos and synchronize them"""
        self.media_handler.load_videos(transform_path, left_path, right_path)
        
    @property
    def current_frame(self):
        """Accessor for current frame number"""
        if hasattr(self, 'playback_controller'):
            return self.playback_controller.current_frame
        return self._current_frame
        
    @property
    def total_frames(self):
        """Accessor for total frames"""
        if hasattr(self, 'playback_controller'):
            return self.playback_controller.total_frames
        return self._total_frames
        
    @property
    def fps(self):
        """Accessor for frames per second"""
        if hasattr(self, 'playback_controller'):
            return self.playback_controller.fps
        return self._fps
        
    @property
    def duration(self):
        """Accessor for video duration in milliseconds"""
        if hasattr(self, 'media_handler'):
            return self.media_handler.duration
        return self._duration
        
    @property
    def position(self):
        """Accessor for current playback position in milliseconds"""
        if hasattr(self, 'media_player'):
            return self.media_player.position()
        return 0
        
    @property
    def is_playing(self):
        """Accessor for playback state"""
        if hasattr(self, 'playback_controller'):
            return self.playback_controller.is_playing
        return self._is_playing
        
    @property
    def frame_duration(self):
        """Accessor for frame duration in milliseconds"""
        if hasattr(self, 'media_handler'):
            return self.media_handler.frame_duration
        return self._frame_duration
        
    # View visibility properties
    @property
    def is_left_visible(self):
        """Accessor for left view visibility state"""
        if hasattr(self, 'view_handler'):
            return self.view_handler.is_left_visible
        return self._is_left_visible
        
    @property
    def is_right_visible(self):
        """Accessor for right view visibility state"""
        if hasattr(self, 'view_handler'):
            return self.view_handler.is_right_visible
        return self._is_right_visible
        
    @property
    def is_transform_visible(self):
        """Accessor for transform view visibility state"""
        if hasattr(self, 'view_handler'):
            return self.view_handler.is_transform_visible
        return self._is_transform_visible
        
    def _sync_properties(self):
        """Sync properties from handlers to maintain compatibility with external code"""
        # Update from media handler
        if hasattr(self, 'media_handler'):
            self._fps = self.media_handler.fps
            self._total_frames = self.media_handler.total_frames
            self._frame_duration = self.media_handler.frame_duration
            self._duration = self.media_handler.duration
            
        # Update from playback controller
        if hasattr(self, 'playback_controller'):
            self._current_frame = self.playback_controller.current_frame
            self._is_playing = self.playback_controller.is_playing
            
        # Update from view handler
        if hasattr(self, 'view_handler'):
            self._is_left_visible = self.view_handler.is_left_visible
            self._is_right_visible = self.view_handler.is_right_visible
            self._is_transform_visible = self.view_handler.is_transform_visible

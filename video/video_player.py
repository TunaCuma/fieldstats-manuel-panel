import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFileDialog, 
    QLabel, QMessageBox, QStatusBar, QMenuBar, QMenu, QDialog, QHBoxLayout, QCheckBox, QPushButton
)
from PyQt6.QtMultimedia import QMediaPlayer 
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QAction

from .video_view_subclasses import LeftFieldView, RightFieldView, TransformView
from .video_controls import VideoControls
from .layout_manager import LayoutManager
from .media_synchronizer import MediaSynchronizer

class VideoPlayer(QMainWindow):
    viewResized = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Analysis Player")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
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
        
        # Connect detach signals
        self.left_view.detachRequested.connect(self.handle_left_detach)
        self.right_view.detachRequested.connect(self.handle_right_detach)
        self.transform_view.detachRequested.connect(self.handle_transform_detach)
        
        # Connect reattach signals
        self.left_view.reattachRequested.connect(self.handle_left_reattach)
        self.right_view.reattachRequested.connect(self.handle_right_reattach)
        self.transform_view.reattachRequested.connect(self.handle_transform_reattach)
        
        # Create controls
        self.controls = VideoControls()
        self.main_layout.addWidget(self.controls)
        
        # Reference to click_info_label for JSONOverlayManager
        self.click_info_label = self.controls.click_info_label
        
        # Setup media players
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.transform_view.video_item)
        
        self.left_player = QMediaPlayer()
        self.left_player.setVideoOutput(self.left_view.video_item)
        
        self.right_player = QMediaPlayer()
        self.right_player.setVideoOutput(self.right_view.video_item)
        
        # Setup synchronizer
        self.synchronizer = MediaSynchronizer()
        self.synchronizer.add_player(self.media_player, is_primary=True)
        self.synchronizer.add_player(self.left_player)
        self.synchronizer.add_player(self.right_player)
        
        # Playback and frame state variables
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 0
        self.duration = 0
        self.frame_duration = 0
        self.is_playing = False
        
        # Visibility flags
        self.is_left_visible = True
        self.is_right_visible = True
        self.is_transform_visible = True
        
        # Connect view signals
        self.left_view.toggledVisibility.connect(self.handle_left_visibility)
        self.right_view.toggledVisibility.connect(self.handle_right_visibility)
        self.transform_view.toggledVisibility.connect(self.handle_transform_visibility)
        self.left_view.videoResized.connect(self.handle_view_resized)
        self.right_view.videoResized.connect(self.handle_view_resized)
        self.transform_view.videoResized.connect(self.handle_view_resized)
        
        # Connect layout manager signals
        self.layout_manager.viewResized.connect(self.handle_view_resized)
        
        # Connect control signals
        self.controls.playPauseClicked.connect(self.play_pause)
        self.controls.stopClicked.connect(self.stop)
        self.controls.prevFrameClicked.connect(self.previous_frame)
        self.controls.nextFrameClicked.connect(self.next_frame)
        self.controls.sliderMoved.connect(self.set_position)
        self.controls.goToFrameRequested.connect(self.go_to_frame)
        
        # Connect media player signals
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.errorOccurred.connect(self.handle_error)
        
        # Connect synchronizer signals
        self.synchronizer.playbackStateChanged.connect(self.handle_playback_state_changed)
        
        # Setup status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Setup menu bar
        self.setup_menu()
        
        # Timer for updating UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)
        
        self.media_player.mediaStatusChanged.connect(self.update_video_sizes)
        self.left_player.mediaStatusChanged.connect(self.update_video_sizes)
        self.right_player.mediaStatusChanged.connect(self.update_video_sizes)

    def update_video_sizes(self, status):
        """Update all video sizes when media status changes"""
        # Check if the media is loaded and ready
        if status in [QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia]:
            # Force update of all video sizes
            self.left_view.update_video_size()
            self.right_view.update_video_size()
            self.transform_view.update_video_size()
            
            # Emit signal for overlay adjustments
            self.viewResized.emit()
    
    def setup_menu(self):
        """Set up the menu bar"""
        self.menuBar = QMenuBar()
        self.setMenuBar(self.menuBar)
        
        # File menu
        self.fileMenu = QMenu("&File", self)
        self.menuBar.addMenu(self.fileMenu)
        
        self.openAction = QAction("&Open Videos...", self)
        self.openAction.triggered.connect(self.open_videos)
        self.fileMenu.addAction(self.openAction)
        
        self.openProjectAction = QAction("&Open Project...", self)
        self.openProjectAction.triggered.connect(self.open_project)
        self.fileMenu.addAction(self.openProjectAction)
        
        self.fileMenu.addSeparator()
        
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        
        # View menu
        self.viewMenu = QMenu("&View", self)
        self.menuBar.addMenu(self.viewMenu)
        
        self.toggleLeftAction = QAction("Toggle &Left Field", self)
        self.toggleLeftAction.triggered.connect(self.toggle_left_field)
        self.viewMenu.addAction(self.toggleLeftAction)
        
        self.toggleRightAction = QAction("Toggle &Right Field", self)
        self.toggleRightAction.triggered.connect(self.toggle_right_field)
        self.viewMenu.addAction(self.toggleRightAction)
        
        self.toggleTransformAction = QAction("Toggle &Transform View", self)
        self.toggleTransformAction.triggered.connect(self.toggle_transform_view)
        self.viewMenu.addAction(self.toggleTransformAction)
        
        # Add new view management options
        self.viewMenu.addSeparator()
        self.manageViewsAction = QAction("&Manage Views...", self)
        self.manageViewsAction.triggered.connect(self.show_view_control_dialog)
        self.viewMenu.addAction(self.manageViewsAction)
        
        # Optional shortcut for showing all views
        self.showAllViewsAction = QAction("Show &All Views", self)
        self.showAllViewsAction.triggered.connect(self.show_all_views)
        self.viewMenu.addAction(self.showAllViewsAction)
    
    def load_videos(self, transform_path, left_path, right_path):
        """Load all three videos and synchronize them"""
        self.media_player.setSource(QUrl.fromLocalFile(transform_path))
        self.left_player.setSource(QUrl.fromLocalFile(left_path))
        self.right_player.setSource(QUrl.fromLocalFile(right_path))
        
        self.statusBar.showMessage(f"Loaded videos")
        self.controls.set_play_icon(False)
    
    def open_videos(self):
        """Open video files via file dialog"""
        # This would typically use QFileDialog to let users select videos
        self.statusBar.showMessage("Open videos dialog not implemented yet")
    
    def open_project(self):
        """For future implementation to open a project file"""
        self.statusBar.showMessage("Project file support will be added in the future")
    
    def play_pause(self):
        """Toggle play/pause for all videos"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.synchronizer.pause()
            self.is_playing = False
            self.controls.set_play_icon(False)
        else:
            self.synchronizer.play()
            self.is_playing = True
            self.controls.set_play_icon(True)
    
    def stop(self):
        """Stop all videos"""
        self.synchronizer.stop()
        self.is_playing = False
        self.controls.set_play_icon(False)
    
    def set_position(self, position):
        """Set position for all videos"""
        self.synchronizer.set_position(position)
    
    def duration_changed(self, duration):
        """Handle duration change event"""
        self.duration = duration
        
        try:
            self.fps = 30 if duration > 0 and duration < 10000 else 60
        except Exception:
            self.fps = 30
        
        if self.fps > 0:
            self.total_frames = int(duration / 1000 * self.fps)
            self.frame_duration = 1000 / self.fps
        else:
            self.total_frames = int(duration / 33.33)
            self.frame_duration = 33.33
        
        self.frame_duration = round(self.frame_duration, 3)
        
        # Update controls
        self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
        self.controls.update_position_slider(0, duration)
    
    def position_changed(self, position):
        """Handle position change event"""
        if self.fps > 0:
            self.current_frame = int(position / 1000 * self.fps)
            self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
            self.controls.update_position_slider(position, self.duration)
    
    def update_ui(self):
        """Update UI periodically"""
        # Update current frame from position
        position = self.media_player.position()
        if self.fps > 0:
            self.current_frame = int(position / 1000 * self.fps)
            self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
    
    def handle_playback_state_changed(self, state):
        """Handle playback state changes"""
        self.is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.controls.set_play_icon(self.is_playing)
    
    def go_to_frame(self, frame_num):
        """Navigate to a specific frame"""
        if 0 <= frame_num < self.total_frames:
            if self.is_playing:
                self.synchronizer.pause()
                self.is_playing = False
                self.controls.set_play_icon(False)
                
            position = int(frame_num * self.frame_duration)
            self.synchronizer.set_position(position)
            self.current_frame = frame_num
            self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
            self.statusBar.showMessage(f"Moved to frame {frame_num}")
        else:
            self.statusBar.showMessage(f"Frame number out of range (0-{self.total_frames-1})")
    
    def next_frame(self):
        """Go to next frame"""
        if self.is_playing:
            self.synchronizer.pause()
            self.is_playing = False
            self.controls.set_play_icon(False)
            
        next_frame = min(self.current_frame + 1, self.total_frames - 1)
        position = int(next_frame * self.frame_duration)
        self.synchronizer.set_position(position)
        self.current_frame = next_frame
        self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
    
    def previous_frame(self):
        """Go to previous frame"""
        if self.is_playing:
            self.synchronizer.pause()
            self.is_playing = False
            self.controls.set_play_icon(False)
            
        prev_frame = max(self.current_frame - 1, 0)
        position = int(prev_frame * self.frame_duration)
        self.synchronizer.set_position(position)
        self.current_frame = prev_frame
        self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
    
    def handle_error(self, error, error_string):
        """Handle media player errors"""
        self.statusBar.showMessage(f"Error: {error_string}")
    
    def handle_view_resized(self):
        """Handle view resize events"""
        # Update all views' video sizes
        self.left_view.update_video_size()
        self.right_view.update_video_size()
        self.transform_view.update_video_size()
        
        # Emit signal for overlay adjustments
        self.viewResized.emit()
    
    def handle_left_detach(self):
        """Handle left view detach request"""
        if self.left_view.detached_window:
            self.left_view.set_detached_video_output(self.left_player)
            self.statusBar.showMessage("Left field view detached to separate window")
    
    def handle_right_detach(self):
        """Handle right view detach request"""
        if self.right_view.detached_window:
            self.right_view.set_detached_video_output(self.right_player)
            self.statusBar.showMessage("Right field view detached to separate window")
    
    def handle_transform_detach(self):
        """Handle transform view detach request"""
        if self.transform_view.detached_window:
            self.transform_view.set_detached_video_output(self.media_player)
            self.statusBar.showMessage("Transform view detached to separate window")
    
    def handle_left_reattach(self):
        """Handle left view reattach request"""
        self.left_player.setVideoOutput(self.left_view.video_item)
        self.statusBar.showMessage("Left field view reattached")
    
    def handle_right_reattach(self):
        """Handle right view reattach request"""
        self.right_player.setVideoOutput(self.right_view.video_item)
        self.statusBar.showMessage("Right field view reattached")
    
    def handle_transform_reattach(self):
        """Handle transform view reattach request"""
        self.media_player.setVideoOutput(self.transform_view.video_item)
        self.statusBar.showMessage("Transform view reattached")
    
    def handle_left_visibility(self, is_visible):
        """Handle left view visibility changes"""
        self.is_left_visible = is_visible
    
    def handle_right_visibility(self, is_visible):
        """Handle right view visibility changes"""
        self.is_right_visible = is_visible
    
    def handle_transform_visibility(self, is_visible):
        """Handle transform view visibility changes"""
        self.is_transform_visible = is_visible
    
    def toggle_left_field(self):
        """Toggle left field view visibility"""
        self.left_view.toggle_visibility()
    
    def toggle_right_field(self):
        """Toggle right field view visibility"""
        self.right_view.toggle_visibility()
    
    def toggle_transform_view(self):
        """Toggle transform view visibility"""
        self.transform_view.toggle_visibility()
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.handle_view_resized()

    def show_view_control_dialog(self):
        """Show a dialog to control visibility of all views"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Views")
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel("Show/Hide Video Panels")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Left field checkbox
        left_check = QCheckBox("Left Field View")
        left_check.setChecked(self.is_left_visible)
        layout.addWidget(left_check)
        
        # Right field checkbox
        right_check = QCheckBox("Right Field View")
        right_check.setChecked(self.is_right_visible)
        layout.addWidget(right_check)
        
        # Transform checkbox
        transform_check = QCheckBox("Transform View")
        transform_check.setChecked(self.is_transform_visible)
        layout.addWidget(transform_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")
        
        apply_button.clicked.connect(lambda: self.apply_view_visibility(
            left_check.isChecked(), 
            right_check.isChecked(), 
            transform_check.isChecked()
        ) or dialog.accept())
        
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        dialog.exec()

    def apply_view_visibility(self, left_visible, right_visible, transform_visible):
        """Apply visibility settings to all views"""
        # Only toggle if the state is different
        if self.is_left_visible != left_visible:
            self.toggle_left_field()
        
        if self.is_right_visible != right_visible:
            self.toggle_right_field()
        
        if self.is_transform_visible != transform_visible:
            self.toggle_transform_view()
        
        # Update the layout after changes
        self.handle_view_resized()
    
    def show_all_views(self):
        """Show all views that might be hidden"""
        if not self.is_left_visible:
            self.left_view.toggle_visibility()
        
        if not self.is_right_visible:
            self.right_view.toggle_visibility()
        
        if not self.is_transform_visible:
            self.transform_view.toggle_visibility()

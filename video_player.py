import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QFileDialog, QLineEdit, QStyle, QGraphicsScene, QGraphicsView,
    QSplitter
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import Qt, QUrl, QTimer, QSizeF, pyqtSignal
from PyQt6.QtGui import QAction

class VideoPlayer(QMainWindow):
    viewResized = pyqtSignal()
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Analysis Player")
        self.setGeometry(100, 100, 1200, 800)
        
        # Store native video dimensions for aspect ratio calculations
        self.native_sizes = {
            "main": QSizeF(0, 0),
            "left": QSizeF(0, 0),
            "right": QSizeF(0, 0)
        }
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create a splitter for top and bottom videos
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_layout.addWidget(self.main_splitter)
        
        # Top container for left and right field videos
        self.top_container = QWidget()
        self.top_layout = QHBoxLayout(self.top_container)
        self.main_splitter.addWidget(self.top_container)
        
        # Left field video
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_scene = QGraphicsScene()
        self.left_view = QGraphicsView(self.left_scene)
        self.left_view.setStyleSheet("background-color: black;")
        self.left_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.left_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.left_layout.addWidget(self.left_view)
        self.left_label = QLabel("Left Field")
        self.left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_label.setStyleSheet("font-weight: bold; color: white;")
        self.left_layout.addWidget(self.left_label)
        self.top_layout.addWidget(self.left_container)
        
        # Right field video
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_scene = QGraphicsScene()
        self.right_view = QGraphicsView(self.right_scene)
        self.right_view.setStyleSheet("background-color: black;")
        self.right_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.right_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.right_layout.addWidget(self.right_view)
        self.right_label = QLabel("Right Field")
        self.right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_label.setStyleSheet("font-weight: bold; color: white;")
        self.right_layout.addWidget(self.right_label)
        self.top_layout.addWidget(self.right_container)
        
        # Bottom container for transformed video
        self.bottom_container = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_container)
        self.main_splitter.addWidget(self.bottom_container)
        
        # Transformed video (main video)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: black;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bottom_layout.addWidget(self.view)
        self.transform_label = QLabel("Transformed View")
        self.transform_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transform_label.setStyleSheet("font-weight: bold; color: white;")
        self.bottom_layout.addWidget(self.transform_label)
        
        # Set the splitter's initial sizes (1:2 ratio for top:bottom)
        self.main_splitter.setSizes([300, 500])
        
        # Video items for each view
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        
        self.left_video_item = QGraphicsVideoItem()
        self.left_scene.addItem(self.left_video_item)
        
        self.right_video_item = QGraphicsVideoItem()
        self.right_scene.addItem(self.right_video_item)
        
        # Media players setup
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_item)
        
        self.left_player = QMediaPlayer()
        self.left_audio = QAudioOutput()
        self.left_player.setAudioOutput(self.left_audio)
        self.left_player.setVideoOutput(self.left_video_item)
        
        self.right_player = QMediaPlayer()
        self.right_audio = QAudioOutput()
        self.right_player.setAudioOutput(self.right_audio)
        self.right_player.setVideoOutput(self.right_video_item)
        
        # Mute side videos by default, keep only main audio
        self.left_audio.setMuted(True)
        self.right_audio.setMuted(True)

        # List for additional duration_changed callbacks
        self._duration_changed_callbacks = []
        
        # Frame information labels
        self.frame_info_layout = QHBoxLayout()
        self.current_frame_label = QLabel("Current Frame: 0")
        self.total_frames_label = QLabel("Total Frames: 0")
        self.fps_label = QLabel("FPS: 0")
        self.frame_info_layout.addWidget(self.current_frame_label)
        self.frame_info_layout.addWidget(self.total_frames_label)
        self.frame_info_layout.addWidget(self.fps_label)
        self.main_layout.addLayout(self.frame_info_layout)
        
        # Label for overlay clicks
        self.click_info_label = QLabel("Click on an overlay rectangle")
        self.click_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.click_info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
        self.main_layout.addWidget(self.click_info_label)
        
        # Frame navigation controls
        self.frame_nav_layout = QHBoxLayout()
        self.frame_input_label = QLabel("Go to Frame:")
        self.frame_input = QLineEdit()
        self.frame_input.setFixedWidth(100)
        self.frame_input.returnPressed.connect(self.go_to_frame)
        self.go_frame_btn = QPushButton("Go")
        self.go_frame_btn.clicked.connect(self.go_to_frame)
        self.frame_nav_layout.addWidget(self.frame_input_label)
        self.frame_nav_layout.addWidget(self.frame_input)
        self.frame_nav_layout.addWidget(self.go_frame_btn)
        self.main_layout.addLayout(self.frame_nav_layout)
        
        # Position slider for video navigation
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.main_layout.addWidget(self.position_slider)
        
        # Media control buttons
        self.controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play_pause)
        self.controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stop)
        self.controls_layout.addWidget(self.stop_btn)
        
        self.prev_frame_btn = QPushButton("Previous Frame")
        self.prev_frame_btn.clicked.connect(self.previous_frame)
        self.controls_layout.addWidget(self.prev_frame_btn)
        
        self.next_frame_btn = QPushButton("Next Frame")
        self.next_frame_btn.clicked.connect(self.next_frame)
        self.controls_layout.addWidget(self.next_frame_btn)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.controls_layout.addWidget(QLabel("Volume:"))
        self.controls_layout.addWidget(self.volume_slider)
        self.main_layout.addLayout(self.controls_layout)
        
        # Status bar and menu
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("Ready")
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu("&File")
        self.openAction = QAction("&Open Project", self)
        self.openAction.triggered.connect(self.open_project)
        self.fileMenu.addAction(self.openAction)
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        
        # Playback and frame state variables
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 0
        self.duration = 0
        self.frame_duration = 0
        self.is_playing = False
        
        # Timer for updating frame position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(100)
        
        # Connect media player signals
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.playbackStateChanged.connect(self.state_changed)
        self.media_player.errorOccurred.connect(self.handle_error)
        
        # Connect video sink signals to detect when video size is available
        self.media_player.videoSink().videoSizeChanged.connect(
            lambda size: self.video_size_changed("main", size))
        self.left_player.videoSink().videoSizeChanged.connect(
            lambda size: self.video_size_changed("left", size))
        self.right_player.videoSink().videoSizeChanged.connect(
            lambda size: self.video_size_changed("right", size))
        
        self.audio_output.setVolume(0.5)
    
    def load_videos(self, transform_path, left_path, right_path):
        """Load all three videos and synchronize them"""
        self.media_player.setSource(QUrl.fromLocalFile(transform_path))
        self.left_player.setSource(QUrl.fromLocalFile(left_path))
        self.right_player.setSource(QUrl.fromLocalFile(right_path))
        
        self.statusBar.showMessage(f"Loaded videos")
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    
    def open_project(self):
        """For future implementation to open a project file"""
        # For now, just show a message
        self.statusBar.showMessage("Project file support will be added in the future")
    
    def play_pause(self):
        """Synchronize play/pause for all three videos"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.left_player.pause()
            self.right_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
        else:
            self.media_player.play()
            self.left_player.play()
            self.right_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.is_playing = True
    
    def stop(self):
        """Stop all three videos"""
        self.media_player.stop()
        self.left_player.stop()
        self.right_player.stop()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.is_playing = False
    
    def set_position(self, position):
        """Set position for all three videos"""
        self.media_player.setPosition(position)
        self.left_player.setPosition(position)
        self.right_player.setPosition(position)
    
    def set_volume(self, volume):
        """Set volume for main video only"""
        self.audio_output.setVolume(volume / 100.0)
    
    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
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
        self.total_frames_label.setText(f"Total Frames: {self.total_frames}")
        self.fps_label.setText(f"FPS: {self.fps:.2f}")
        
        # Invoke all registered duration_changed callbacks
        for callback in self._duration_changed_callbacks:
            callback(duration)
    
    def position_changed(self, position):
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)
        if self.fps > 0:
            self.current_frame = int(position / 1000 * self.fps)
            self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
    
    def update_position(self):
        position = self.media_player.position()
        if self.fps > 0:
            self.current_frame = int(position / 1000 * self.fps)
            self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
    
    def state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
    
    def go_to_frame(self):
        try:
            frame_num = int(self.frame_input.text())
            if 0 <= frame_num < self.total_frames:
                if self.is_playing:
                    self.media_player.pause()
                    self.left_player.pause()
                    self.right_player.pause()
                    self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
                    self.is_playing = False
                position = int(frame_num * self.frame_duration)
                self.media_player.setPosition(position)
                self.left_player.setPosition(position)
                self.right_player.setPosition(position)
                self.current_frame = frame_num
                self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
                self.statusBar.showMessage(f"Moved to frame {frame_num}")
            else:
                self.statusBar.showMessage(f"Frame number out of range (0-{self.total_frames-1})")
        except ValueError:
            self.statusBar.showMessage("Please enter a valid frame number")
    
    def next_frame(self):
        if self.is_playing:
            self.media_player.pause()
            self.left_player.pause()
            self.right_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
        next_frame = min(self.current_frame + 1, self.total_frames - 1)
        position = int(next_frame * self.frame_duration)
        self.media_player.setPosition(position)
        self.left_player.setPosition(position)
        self.right_player.setPosition(position)
        self.current_frame = next_frame
        self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
        QApplication.processEvents()
    
    def previous_frame(self):
        if self.is_playing:
            self.media_player.pause()
            self.left_player.pause()
            self.right_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
        prev_frame = max(self.current_frame - 1, 0)
        position = int(prev_frame * self.frame_duration)
        self.media_player.setPosition(position)
        self.left_player.setPosition(position)
        self.right_player.setPosition(position)
        self.current_frame = prev_frame
        self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
        QApplication.processEvents()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scene_video_size()
        self.viewResized.emit()

    def update_scene_video_size(self):
        """Core functionality for maintaining scene/video item size while preserving aspect ratio"""
        # Update main view
        view_size = self.view.size()
        self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())
        
        # Get the natural video size if available
        if self.media_player.hasVideo():
            video_size = self.media_player.videoSink().videoSize()
            if video_size.width() > 0 and video_size.height() > 0:
                # Calculate scaling to maintain aspect ratio
                scale = min(view_size.width() / video_size.width(), 
                            view_size.height() / video_size.height())
                new_width = video_size.width() * scale
                new_height = video_size.height() * scale
                
                # Center the video in the view
                x_offset = (view_size.width() - new_width) / 2
                y_offset = (view_size.height() - new_height) / 2
                
                self.video_item.setPos(x_offset, y_offset)
                self.video_item.setSize(QSizeF(new_width, new_height))
            else:
                self.video_item.setSize(QSizeF(view_size))
        else:
            self.video_item.setSize(QSizeF(view_size))
        
        # Update left view
        left_size = self.left_view.size()
        self.left_scene.setSceneRect(0, 0, left_size.width(), left_size.height())
        
        if self.left_player.hasVideo():
            video_size = self.left_player.videoSink().videoSize()
            if video_size.width() > 0 and video_size.height() > 0:
                scale = min(left_size.width() / video_size.width(), 
                            left_size.height() / video_size.height())
                new_width = video_size.width() * scale
                new_height = video_size.height() * scale
                
                x_offset = (left_size.width() - new_width) / 2
                y_offset = (left_size.height() - new_height) / 2
                
                self.left_video_item.setPos(x_offset, y_offset)
                self.left_video_item.setSize(QSizeF(new_width, new_height))
            else:
                self.left_video_item.setSize(QSizeF(left_size))
        else:
            self.left_video_item.setSize(QSizeF(left_size))
        
        # Update right view
        right_size = self.right_view.size()
        self.right_scene.setSceneRect(0, 0, right_size.width(), right_size.height())
        
        if self.right_player.hasVideo():
            video_size = self.right_player.videoSink().videoSize()
            if video_size.width() > 0 and video_size.height() > 0:
                scale = min(right_size.width() / video_size.width(), 
                            right_size.height() / video_size.height())
                new_width = video_size.width() * scale
                new_height = video_size.height() * scale
                
                x_offset = (right_size.width() - new_width) / 2
                y_offset = (right_size.height() - new_height) / 2
                
                self.right_video_item.setPos(x_offset, y_offset)
                self.right_video_item.setSize(QSizeF(new_width, new_height))
            else:
                self.right_video_item.setSize(QSizeF(right_size))
        else:
            self.right_video_item.setSize(QSizeF(right_size))
        
    def get_position(self):
        return self.media_player.position()
    
    def handle_error(self, error, error_string):
        self.statusBar.showMessage(f"Error: {error_string}")
        
    def video_size_changed(self, view_name, size):
        """Handle video size changes to maintain proper aspect ratio"""
        if size.width() > 0 and size.height() > 0:
            self.native_sizes[view_name] = size
            
            # Update video item sizes
            self.update_scene_video_size()
            
            # Log video dimensions for debugging
            self.statusBar.showMessage(f"{view_name} video loaded: {size.width()}x{size.height()}", 2000)

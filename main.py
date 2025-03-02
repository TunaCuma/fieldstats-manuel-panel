import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QSlider, QLabel, 
                            QFileDialog, QLineEdit, QStyle, QSizePolicy,
                            QGraphicsScene, QGraphicsView, QGraphicsRectItem,
                            QGraphicsTextItem)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import Qt, QUrl, QTimer, QRectF, QSizeF
from PyQt6.QtGui import QIcon, QAction, QColor, QPen, QBrush, QFont


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("PyQt6 Video Player with Graphics Overlays")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create graphics scene for video and overlays
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: black;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.view)
        
        # Create video item for the scene
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        
        # Create media player components
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_item)
        
        # Create rectangle overlays
        self.rect1 = CustomRectItem(0, 0, 150, 80)
        self.rect1.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        self.scene.addItem(self.rect1)
        self.rect1.setClickCallback(self.rect1_clicked)
        
        self.rect2 = CustomRectItem(0, 0, 150, 80)
        self.rect2.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent fill
        self.scene.addItem(self.rect2)
        self.rect2.setClickCallback(self.rect2_clicked)
        
        # Position the rectangles
        self.adjust_items_position()
        
        # Frame information
        self.frame_info_layout = QHBoxLayout()
        self.current_frame_label = QLabel("Current Frame: 0")
        self.total_frames_label = QLabel("Total Frames: 0")
        self.fps_label = QLabel("FPS: 0")
        self.frame_info_layout.addWidget(self.current_frame_label)
        self.frame_info_layout.addWidget(self.total_frames_label)
        self.frame_info_layout.addWidget(self.fps_label)
        self.main_layout.addLayout(self.frame_info_layout)
        
        # Label to display which rectangle was clicked
        self.click_info_label = QLabel("Click on either rectangle overlay")
        self.click_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.click_info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
        self.main_layout.addWidget(self.click_info_label)
        
        # Create frame navigation controls
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
        
        # Create slider for video position
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.main_layout.addWidget(self.position_slider)
        
        # Create media control buttons
        self.controls_layout = QHBoxLayout()
        
        # Open button
        self.open_btn = QPushButton("Open Video")
        self.open_btn.clicked.connect(self.open_file)
        self.controls_layout.addWidget(self.open_btn)
        
        # Play button
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play_pause)
        self.controls_layout.addWidget(self.play_btn)
        
        # Stop button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stop)
        self.controls_layout.addWidget(self.stop_btn)
        
        # Previous frame button
        self.prev_frame_btn = QPushButton("Previous Frame")
        self.prev_frame_btn.clicked.connect(self.previous_frame)
        self.controls_layout.addWidget(self.prev_frame_btn)
        
        # Next frame button
        self.next_frame_btn = QPushButton("Next Frame")
        self.next_frame_btn.clicked.connect(self.next_frame)
        self.controls_layout.addWidget(self.next_frame_btn)
        
        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.controls_layout.addWidget(QLabel("Volume:"))
        self.controls_layout.addWidget(self.volume_slider)
        
        self.main_layout.addLayout(self.controls_layout)
        
        # Add status bar
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("Ready")
        
        # Create menu bar
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu("&File")
        
        # Open action
        self.openAction = QAction("&Open", self)
        self.openAction.triggered.connect(self.open_file)
        self.fileMenu.addAction(self.openAction)
        
        # Exit action
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        
        # State variables
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 0
        self.duration = 0
        self.frame_duration = 0
        self.is_playing = False
        
        # Timer for updating position during playback
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(100)  # Update position every 100ms
        
        # Connect media player signals
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.playbackStateChanged.connect(self.state_changed)
        self.media_player.errorOccurred.connect(self.handle_error)
        
        # Set default volume
        self.audio_output.setVolume(0.5)

    def resizeEvent(self, event):
        """Handle resizing the window"""
        super().resizeEvent(event)
        self.adjust_items_position()
        
    def adjust_items_position(self):
        """Adjust position of scene items based on view size"""
        # Update scene rect to match view size
        view_size = self.view.size()
        self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())
        
        # Resize video item to fill the scene
        # Convert QSize to QSizeF for the video item
        self.video_item.setSize(QSizeF(view_size))
        
        # Position rectangle 1 in top left area
        scene_width = self.scene.width()
        scene_height = self.scene.height()
        
        self.rect1.setPos(scene_width * 0.1, scene_height * 0.1)
        self.rect2.setPos(scene_width * 0.7, scene_height * 0.7)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", 
                                                 "Video Files (*.mp4 *.webm *.avi *.mkv *.mov *.wmv);;All Files (*)")
        
        if file_name:
            # Set the media to play
            self.media_player.setSource(QUrl.fromLocalFile(file_name))
            self.statusBar.showMessage(f"Loaded: {os.path.basename(file_name)}")
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
        else:
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.is_playing = True

    def stop(self):
        self.media_player.stop()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.is_playing = False

    def set_position(self, position):
        self.media_player.setPosition(position)

    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self.duration = duration
        
        # Estimate FPS and total frames
        try:
            if duration > 0:
                if duration < 10000:  # less than 10 seconds
                    self.fps = 30
                else:
                    self.fps = 25
            else:
                self.fps = 30
        except:
            self.fps = 30
        
        # Calculate frame count and frame duration in milliseconds
        if self.fps > 0:
            self.total_frames = int(duration / 1000 * self.fps)
            self.frame_duration = 1000 / self.fps
        else:
            self.total_frames = int(duration / 33.33)
            self.frame_duration = 33.33
        
        self.frame_duration = round(self.frame_duration, 3)
        
        self.total_frames_label.setText(f"Total Frames: {self.total_frames}")
        self.fps_label.setText(f"FPS: {self.fps:.2f}")

    def position_changed(self, position):
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)
        
        # Update current frame
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
                # Pause playback before jumping
                was_playing = self.is_playing
                if was_playing:
                    self.media_player.pause()
                    self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
                    self.is_playing = False
                
                # Convert frame number to time position
                position = int(frame_num * self.frame_duration)
                self.media_player.setPosition(position)
                
                # Update frame counter immediately
                self.current_frame = frame_num
                self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
                
                self.statusBar.showMessage(f"Moved to frame {frame_num}")
            else:
                self.statusBar.showMessage(f"Frame number out of range (0-{self.total_frames-1})")
        except ValueError:
            self.statusBar.showMessage("Please enter a valid frame number")

    def next_frame(self):
        """Move to the next frame with precise control"""
        # Always ensure we're paused for frame-by-frame navigation
        was_playing = self.is_playing
        if was_playing:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
        
        # Calculate exact position for the next frame
        next_frame = min(self.current_frame + 1, self.total_frames - 1)
        position = int(next_frame * self.frame_duration)
        
        # Set position and explicitly wait 
        self.media_player.setPosition(position)
        
        # Update the frame counter immediately to avoid flickering
        self.current_frame = next_frame
        self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
        
        # Process events to ensure position update is processed
        QApplication.processEvents()

    def previous_frame(self):
        """Move to the previous frame with precise control"""
        # Always ensure we're paused for frame-by-frame navigation
        was_playing = self.is_playing
        if was_playing:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.is_playing = False
        
        # Calculate exact position for the previous frame
        prev_frame = max(self.current_frame - 1, 0)
        position = int(prev_frame * self.frame_duration)
        
        # Set position and explicitly wait
        self.media_player.setPosition(position)
        
        # Update the frame counter immediately to avoid flickering
        self.current_frame = prev_frame
        self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
        
        # Process events to ensure position update is processed
        QApplication.processEvents()
    
    def handle_error(self, error, error_string):
        self.statusBar.showMessage(f"Error: {error_string}")
        
    def rect1_clicked(self):
        """Handle when the first rectangle is clicked"""
        self.click_info_label.setText("Rectangle 1 was clicked!")
        self.click_info_label.setStyleSheet("font-weight: bold; color: orange; font-size: 14px;")
        self.statusBar.showMessage("Rectangle 1 clicked")
        
    def rect2_clicked(self):
        """Handle when the second rectangle is clicked"""
        self.click_info_label.setText("Rectangle 2 was clicked!")
        self.click_info_label.setStyleSheet("font-weight: bold; color: orange; font-size: 14px;")
        self.statusBar.showMessage("Rectangle 2 clicked")


class CustomRectItem(QGraphicsRectItem):
    """Custom rectangle item that can detect clicks and hover effects"""
    
    def __init__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.click_callback = None
        self.default_pen = QPen(QColor("orange"), 3)
        self.hover_pen = QPen(QColor("yellow"), 3)
        self.setPen(self.default_pen)
        
        # Enable item to receive hover events
        self.setAcceptHoverEvents(True)
        # Set cursor to pointing hand
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def setClickCallback(self, callback):
        """Set the callback function for when this item is clicked"""
        self.click_callback = callback
        
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter events"""
        self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave events"""
        self.setPen(self.default_pen)
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press events on this item"""
        if self.click_callback:
            self.click_callback()
        super().mousePressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())

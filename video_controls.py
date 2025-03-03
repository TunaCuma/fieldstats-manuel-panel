from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSlider, QPushButton,
    QLabel, QLineEdit, QStyle, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class VideoControls(QWidget):
    """A widget providing video playback controls"""
    playPauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    nextFrameClicked = pyqtSignal()
    prevFrameClicked = pyqtSignal()
    sliderMoved = pyqtSignal(int)
    volumeChanged = pyqtSignal(int)
    goToFrameRequested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Frame information display
        self.frame_info_group = QGroupBox("Frame Information")
        self.frame_info_layout = QHBoxLayout(self.frame_info_group)
        
        self.current_frame_label = QLabel("Current Frame: 0")
        self.total_frames_label = QLabel("Total Frames: 0")
        self.fps_label = QLabel("FPS: 0")
        
        self.frame_info_layout.addWidget(self.current_frame_label)
        self.frame_info_layout.addWidget(self.total_frames_label)
        self.frame_info_layout.addWidget(self.fps_label)
        
        self.layout.addWidget(self.frame_info_group)
        
        # Overlay information area
        self.click_info_label = QLabel("Click on an overlay rectangle")
        self.click_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.click_info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
        self.layout.addWidget(self.click_info_label)
        
        # Frame navigation controls
        self.frame_nav_group = QGroupBox("Frame Navigation")
        self.frame_nav_layout = QHBoxLayout(self.frame_nav_group)
        
        self.frame_input_label = QLabel("Go to Frame:")
        self.frame_input = QLineEdit()
        self.frame_input.setFixedWidth(100)
        self.go_frame_btn = QPushButton("Go")
        
        self.frame_nav_layout.addWidget(self.frame_input_label)
        self.frame_nav_layout.addWidget(self.frame_input)
        self.frame_nav_layout.addWidget(self.go_frame_btn)
        self.frame_nav_layout.addStretch()
        
        self.layout.addWidget(self.frame_nav_group)
        
        # Position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.layout.addWidget(self.position_slider)
        
        # Playback controls
        self.controls_group = QGroupBox("Playback Controls")
        self.controls_layout = QHBoxLayout(self.controls_group)
        
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        
        self.prev_frame_btn = QPushButton("Previous Frame")
        self.next_frame_btn = QPushButton("Next Frame")
        
        self.controls_layout.addWidget(self.play_btn)
        self.controls_layout.addWidget(self.stop_btn)
        self.controls_layout.addWidget(self.prev_frame_btn)
        self.controls_layout.addWidget(self.next_frame_btn)
        
        # Volume control
        self.volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        
        self.controls_layout.addWidget(self.volume_label)
        self.controls_layout.addWidget(self.volume_slider)
        
        self.layout.addWidget(self.controls_group)
        
        # Connect signals
        self.position_slider.sliderMoved.connect(self.sliderMoved.emit)
        self.play_btn.clicked.connect(self.playPauseClicked.emit)
        self.stop_btn.clicked.connect(self.stopClicked.emit)
        self.prev_frame_btn.clicked.connect(self.prevFrameClicked.emit)
        self.next_frame_btn.clicked.connect(self.nextFrameClicked.emit)
        self.volume_slider.valueChanged.connect(self.volumeChanged.emit)
        self.frame_input.returnPressed.connect(self.go_to_frame)
        self.go_frame_btn.clicked.connect(self.go_to_frame)
    
    def go_to_frame(self):
        """Process go to frame request"""
        try:
            frame_num = int(self.frame_input.text())
            self.goToFrameRequested.emit(frame_num)
        except ValueError:
            # Inform the user that input is invalid
            self.click_info_label.setText("Please enter a valid frame number")
    
    def update_frame_info(self, current_frame, total_frames, fps):
        """Update frame information display"""
        self.current_frame_label.setText(f"Current Frame: {current_frame}")
        self.total_frames_label.setText(f"Total Frames: {total_frames}")
        self.fps_label.setText(f"FPS: {fps:.2f}")
    
    def update_position_slider(self, position, duration):
        """Update position slider value without triggering signals"""
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)
        
        if duration != self.position_slider.maximum():
            self.position_slider.setRange(0, duration)
    
    def set_play_icon(self, is_playing):
        """Update play/pause button icon based on state"""
        if is_playing:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

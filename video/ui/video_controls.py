from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QStyle,
    QWidget,
)


class VideoControls(QWidget):
    """A widget providing streamlined video playback controls in a single
    row."""

    playPauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    nextFrameClicked = pyqtSignal()
    prevFrameClicked = pyqtSignal()
    sliderMoved = pyqtSignal(int)
    goToFrameRequested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        # Single horizontal layout for all controls
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Frame information display - combined in one row
        self.current_frame_label = QLabel("Current Frame: 0")
        self.total_frames_label = QLabel("Total Frames: 0")
        self.fps_label = QLabel("FPS: 0")

        # Frame navigation - compacted in single row
        self.frame_input_label = QLabel("Go to:")
        self.frame_input = QLineEdit()
        self.frame_input.setFixedWidth(60)
        self.go_frame_btn = QPushButton("Go")
        self.go_frame_btn.setFixedWidth(40)

        # Playback controls - simplified
        self.play_btn = QPushButton()
        self.play_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.play_btn.setFixedWidth(40)

        # Set explicit focus policy for the play button
        self.play_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        )
        self.stop_btn.setFixedWidth(40)

        self.prev_frame_btn = QPushButton()
        self.prev_frame_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward)
        )
        self.prev_frame_btn.setFixedWidth(40)

        self.next_frame_btn = QPushButton()
        self.next_frame_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward)
        )
        self.next_frame_btn.setFixedWidth(40)

        # Position slider - simplified
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)

        # Click info label
        self.click_info_label = QLabel("Click on an overlay rectangle")
        self.click_info_label.setStyleSheet("font-weight: bold; color: orange;")

        # Add all widgets to the single row layout
        self.layout.addWidget(self.current_frame_label)
        self.layout.addWidget(self.total_frames_label)
        self.layout.addWidget(self.fps_label)
        self.layout.addWidget(self.position_slider, 1)  # Give slider more space
        self.layout.addWidget(self.prev_frame_btn)
        self.layout.addWidget(self.play_btn)
        self.layout.addWidget(self.stop_btn)
        self.layout.addWidget(self.next_frame_btn)
        self.layout.addWidget(self.frame_input_label)
        self.layout.addWidget(self.frame_input)
        self.layout.addWidget(self.go_frame_btn)
        self.layout.addWidget(self.click_info_label)

        # Connect signals
        self.position_slider.sliderMoved.connect(self.sliderMoved.emit)
        self.play_btn.clicked.connect(self.playPauseClicked.emit)
        self.stop_btn.clicked.connect(self.stopClicked.emit)
        self.prev_frame_btn.clicked.connect(self.prevFrameClicked.emit)
        self.next_frame_btn.clicked.connect(self.nextFrameClicked.emit)
        self.frame_input.returnPressed.connect(self.go_to_frame)
        self.go_frame_btn.clicked.connect(self.go_to_frame)

        # Schedule focus to be set after the widget is fully initialized
        # This ensures the focus request is processed after widget is displayed
        QTimer.singleShot(0, self.play_btn.setFocus)

    def go_to_frame(self):
        """Process go to frame request."""
        try:
            frame_num = int(self.frame_input.text())
            self.goToFrameRequested.emit(frame_num)
        except ValueError:
            # Inform the user that input is invalid
            self.click_info_label.setText("Please enter a valid frame number")

    def update_frame_info(self, current_frame, total_frames, fps):
        """Update frame information display."""
        self.current_frame_label.setText(f"Current Frame: {current_frame}")
        self.total_frames_label.setText(f"Total Frames: {total_frames}")
        self.fps_label.setText(f"FPS: {fps:.2f}")

    def update_position_slider(self, position, duration):
        """Update position slider value without triggering signals."""
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)

        if duration != self.position_slider.maximum():
            self.position_slider.setRange(0, duration)

    def set_play_icon(self, is_playing):
        """Update play/pause button icon based on state."""
        if is_playing:
            self.play_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.play_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def showEvent(self, event):
        """Override showEvent to set focus when the widget is shown."""
        super().showEvent(event)
        self.play_btn.setFocus()

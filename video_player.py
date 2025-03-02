import os
from PyQt6.QtWidgets import (
	QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
	QSlider, QLabel, QFileDialog, QLineEdit, QStyle, QGraphicsScene, QGraphicsView
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import Qt, QUrl, QTimer, QSizeF,pyqtSignal
from PyQt6.QtGui import QAction

class VideoPlayer(QMainWindow):
	viewResized = pyqtSignal()
	positionChanged = pyqtSignal(int)
	durationChanged = pyqtSignal(int)

	def __init__(self):
		super().__init__()
		self.setWindowTitle("PyQt6 Video Player")
		self.setGeometry(100, 100, 800, 600)
		
		# Central widget and layout
		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)
		self.main_layout = QVBoxLayout(self.central_widget)
		
		# Graphics scene and view
		self.scene = QGraphicsScene()
		self.view = QGraphicsView(self.scene)
		self.view.setStyleSheet("background-color: black;")
		self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.main_layout.addWidget(self.view)
		
		# Video item
		self.video_item = QGraphicsVideoItem()
		self.scene.addItem(self.video_item)
		
		# Media setup
		self.media_player = QMediaPlayer()
		self.audio_output = QAudioOutput()
		self.media_player.setAudioOutput(self.audio_output)
		self.media_player.setVideoOutput(self.video_item)

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
		self.open_btn = QPushButton("Open Video")
		self.open_btn.clicked.connect(self.open_file)
		self.controls_layout.addWidget(self.open_btn)
		
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
		self.openAction = QAction("&Open", self)
		self.openAction.triggered.connect(self.open_file)
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
		
		self.audio_output.setVolume(0.5)
	

	def open_file(self):
		file_name, _ = QFileDialog.getOpenFileName(
			self, "Open Video File", "",
			"Video Files (*.mp4 *.webm *.avi *.mkv *.mov *.wmv);;All Files (*)"
		)
		if file_name:
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
		
		try:
			self.fps = 30 if duration > 0 and duration < 10000 else 25
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
					self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
					self.is_playing = False
				position = int(frame_num * self.frame_duration)
				self.media_player.setPosition(position)
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
			self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
			self.is_playing = False
		next_frame = min(self.current_frame + 1, self.total_frames - 1)
		position = int(next_frame * self.frame_duration)
		self.media_player.setPosition(position)
		self.current_frame = next_frame
		self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
		QApplication.processEvents()
	
	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.update_scene_video_size()
		self.viewResized.emit()

	def update_scene_video_size(self):
		"""Core functionality for maintaining scene/video item size"""
		view_size = self.view.size()
		self.scene.setSceneRect(0, 0, view_size.width(), view_size.height())
		self.video_item.setSize(QSizeF(view_size))
		
	def get_position(self):
		return self.media_player.position()
		
	def previous_frame(self):
		if self.is_playing:
			self.media_player.pause()
			self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
			self.is_playing = False
		prev_frame = max(self.current_frame - 1, 0)
		position = int(prev_frame * self.frame_duration)
		self.media_player.setPosition(position)
		self.current_frame = prev_frame
		self.current_frame_label.setText(f"Current Frame: {self.current_frame}")
		QApplication.processEvents()
	
	def handle_error(self, error, error_string):
		self.statusBar.showMessage(f"Error: {error_string}")
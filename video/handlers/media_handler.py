from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer


class MediaHandler:
    """Handles media player instances and operations"""

    def __init__(
        self,
        transform_view,
        left_view,
        right_view,
        synchronizer,
        status_bar,
        controls,
        parent,
    ):
        self.transform_view = transform_view
        self.left_view = left_view
        self.right_view = right_view
        self.synchronizer = synchronizer
        self.status_bar = status_bar
        self.controls = controls
        self.parent = parent

        # Setup media players
        self.main_player = QMediaPlayer()
        self.main_player.setVideoOutput(self.transform_view.video_item)

        self.left_player = QMediaPlayer()
        self.left_player.setVideoOutput(self.left_view.video_item)

        self.right_player = QMediaPlayer()
        self.right_player.setVideoOutput(self.right_view.video_item)

        # Add players to synchronizer
        self.synchronizer.add_player(self.main_player, is_primary=True)
        self.synchronizer.add_player(self.left_player)
        self.synchronizer.add_player(self.right_player)

        # Add a reference to self in the media players for access from outside
        self.main_player.mediaHandler = self
        self.left_player.mediaHandler = self
        self.right_player.mediaHandler = self

        # Connect media player signals
        self.main_player.durationChanged.connect(self._duration_changed)
        self.main_player.positionChanged.connect(self._position_changed)
        self.main_player.errorOccurred.connect(self._handle_error)

        # Connect media status change signals
        self.main_player.mediaStatusChanged.connect(self._update_video_sizes)
        self.left_player.mediaStatusChanged.connect(self._update_video_sizes)
        self.right_player.mediaStatusChanged.connect(self._update_video_sizes)

        # Initialize state variables
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 30
        self.duration = 0
        self.frame_duration = 33.33

    def load_videos(self, transform_path, left_path, right_path):
        """Load all three videos and synchronize them"""
        self.main_player.setSource(QUrl.fromLocalFile(transform_path))
        self.left_player.setSource(QUrl.fromLocalFile(left_path))
        self.right_player.setSource(QUrl.fromLocalFile(right_path))

        self.status_bar.showMessage(f"Loaded videos")
        self.controls.set_play_icon(False)

    def open_videos(self):
        """Open video files via file dialog"""
        # For future implementation using QFileDialog
        self.status_bar.showMessage("Open videos dialog not implemented yet")

    def open_project(self):
        """For future implementation to open a project file"""
        self.status_bar.showMessage("Project file support will be added in the future")

    def _update_video_sizes(self, status):
        """Update all video sizes when media status changes"""
        # Check if the media is loaded and ready
        if status in [
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
        ]:
            # Force update of all video sizes
            self.left_view.update_video_size()
            self.right_view.update_video_size()
            self.transform_view.update_video_size()

            # Emit signal for overlay adjustments
            self.parent.viewResized.emit()

    def _duration_changed(self, duration):
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

    def _position_changed(self, position):
        """Handle position change event"""
        if self.fps > 0:
            self.current_frame = int(position / 1000 * self.fps)
            self.controls.update_frame_info(
                self.current_frame, self.total_frames, self.fps
            )
            self.controls.update_position_slider(position, self.duration)

    def _handle_error(self, error, error_string):
        """Handle media player errors"""
        self.status_bar.showMessage(f"Error: {error_string}")

    def get_current_frame(self):
        """Get current frame number"""
        return self.current_frame

    def get_total_frames(self):
        """Get total frames count"""
        return self.total_frames

    def get_fps(self):
        """Get current frames per second"""
        return self.fps

    def get_frame_duration(self):
        """Get duration of a single frame in milliseconds"""
        return self.frame_duration

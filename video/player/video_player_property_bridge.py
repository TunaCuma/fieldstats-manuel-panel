"""
VideoPlayer property bridge module to handle accessor properties between components
"""


class VideoPlayerPropertyBridge:
    """
    Handles property delegation between VideoPlayer components.
    Acts as a bridge to maintain compatibility with external code while using a refactored architecture.
    """

    def __init__(self, parent):
        """Initialize the property bridge with default values"""
        self.parent = parent

        # Initialize default property values
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

    def sync_properties(self):
        """Sync properties from handlers to maintain compatibility with external code"""
        # Update from media handler
        if hasattr(self.parent, "media_handler"):
            self._fps = self.parent.media_handler.fps
            self._total_frames = self.parent.media_handler.total_frames
            self._frame_duration = self.parent.media_handler.frame_duration
            self._duration = self.parent.media_handler.duration

        # Update from playback controller
        if hasattr(self.parent, "playback_controller"):
            self._current_frame = self.parent.playback_controller.current_frame
            self._is_playing = self.parent.playback_controller.is_playing

        # Update from view handler
        if hasattr(self.parent, "view_handler"):
            self._is_left_visible = self.parent.view_handler.is_left_visible
            self._is_right_visible = self.parent.view_handler.is_right_visible
            self._is_transform_visible = self.parent.view_handler.is_transform_visible

    # Playback properties
    @property
    def current_frame(self):
        """Accessor for current frame number"""
        if hasattr(self.parent, "playback_controller"):
            return self.parent.playback_controller.current_frame
        return self._current_frame

    @property
    def total_frames(self):
        """Accessor for total frames"""
        if hasattr(self.parent, "playback_controller"):
            return self.parent.playback_controller.total_frames
        return self._total_frames

    @property
    def fps(self):
        """Accessor for frames per second"""
        if hasattr(self.parent, "playback_controller"):
            return self.parent.playback_controller.fps
        return self._fps

    @property
    def duration(self):
        """Accessor for video duration in milliseconds"""
        if hasattr(self.parent, "media_handler"):
            return self.parent.media_handler.duration
        return self._duration

    @property
    def position(self):
        """Accessor for current playback position in milliseconds"""
        if hasattr(self.parent, "media_player"):
            return self.parent.media_player.position()
        return 0

    @property
    def is_playing(self):
        """Accessor for playback state"""
        if hasattr(self.parent, "playback_controller"):
            return self.parent.playback_controller.is_playing
        return self._is_playing

    @property
    def frame_duration(self):
        """Accessor for frame duration in milliseconds"""
        if hasattr(self.parent, "media_handler"):
            return self.parent.media_handler.frame_duration
        return self._frame_duration

    # View visibility properties
    @property
    def is_left_visible(self):
        """Accessor for left view visibility state"""
        if hasattr(self.parent, "view_handler"):
            return self.parent.view_handler.is_left_visible
        return self._is_left_visible

    @property
    def is_right_visible(self):
        """Accessor for right view visibility state"""
        if hasattr(self.parent, "view_handler"):
            return self.parent.view_handler.is_right_visible
        return self._is_right_visible

    @property
    def is_transform_visible(self):
        """Accessor for transform view visibility state"""
        if hasattr(self.parent, "view_handler"):
            return self.parent.view_handler.is_transform_visible
        return self._is_transform_visible

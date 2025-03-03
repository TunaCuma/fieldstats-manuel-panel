from PyQt6.QtMultimedia import QMediaPlayer

class PlaybackController:
    """Controls playback functionality"""
    
    def __init__(self, synchronizer, controls, main_player, status_bar, view_resize_handler):
        self.synchronizer = synchronizer
        self.controls = controls
        self.main_player = main_player
        self.status_bar = status_bar
        self.view_resize_handler = view_resize_handler
        
        # Playback state
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.frame_duration = 33.33
        
        # Try to get media handler reference if available
        self.media_handler = getattr(main_player, 'mediaHandler', None)
        
        # Connect synchronizer signals
        self.synchronizer.playbackStateChanged.connect(self.handle_playback_state_changed)
    
    def play_pause(self):
        """Toggle play/pause for all videos"""
        if self.main_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
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
    
    def update_ui(self):
        """Update UI periodically"""
        # Update current frame from position
        position = self.main_player.position()
        
        # Get media properties from media handler if available
        try:
            # First try to get updated values from media handler
            if self.media_handler:
                self.fps = self.media_handler.fps
                self.total_frames = self.media_handler.total_frames
                self.frame_duration = self.media_handler.frame_duration
            elif hasattr(self.main_player, 'mediaHandler'):
                self.media_handler = self.main_player.mediaHandler
                self.fps = self.media_handler.fps
                self.total_frames = self.media_handler.total_frames
                self.frame_duration = self.media_handler.frame_duration
            
            if self.fps > 0:
                self.current_frame = int(position / 1000 * self.fps)
                self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
        except Exception as e:
            # Silently handle any errors during UI update
            pass
    
    def handle_playback_state_changed(self, state):
        """Handle playback state changes"""
        self.is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.controls.set_play_icon(self.is_playing)
    
    def go_to_frame(self, frame_num):
        """Navigate to a specific frame"""
        if frame_num < 0:
            return
            
        if self.total_frames == 0:
            # If total_frames is not set yet, try to get it from mediaHandler
            if hasattr(self.main_player, 'mediaHandler'):
                self.total_frames = self.main_player.mediaHandler.total_frames
                self.frame_duration = self.main_player.mediaHandler.frame_duration
            
        if 0 <= frame_num < self.total_frames:
            if self.is_playing:
                self.synchronizer.pause()
                self.is_playing = False
                self.controls.set_play_icon(False)
                
            position = int(frame_num * self.frame_duration)
            self.synchronizer.set_position(position)
            self.current_frame = frame_num
            self.controls.update_frame_info(self.current_frame, self.total_frames, self.fps)
            self.status_bar.showMessage(f"Moved to frame {frame_num}")
        else:
            self.status_bar.showMessage(f"Frame number out of range (0-{self.total_frames-1})")
    
    def next_frame(self):
        """Go to next frame"""
        if self.is_playing:
            self.synchronizer.pause()
            self.is_playing = False
            self.controls.set_play_icon(False)
            
        next_frame = min(self.current_frame + 1, self.total_frames - 1) if self.total_frames > 0 else self.current_frame + 1
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

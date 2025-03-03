from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer

class MediaSynchronizer(QObject):
    """Handles synchronization between multiple QMediaPlayer instances"""
    positionChanged = pyqtSignal(int)
    playbackStateChanged = pyqtSignal(QMediaPlayer.PlaybackState)
    
    def __init__(self):
        super().__init__()
        self.players = []
        self.primary_player = None
        self.is_playing = False
        self.current_position = 0
        
        # Timer for periodic synchronization check
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.check_synchronization)
        self.sync_timer.setInterval(500)  # Check every 500ms
    
    def add_player(self, player, is_primary=False):
        """Add a media player to be synchronized"""
        self.players.append(player)
        
        if is_primary or self.primary_player is None:
            self.primary_player = player
            # Connect signals from primary player
            player.positionChanged.connect(self.handle_position_changed)
            player.playbackStateChanged.connect(self.handle_state_changed)
    
    def handle_position_changed(self, position):
        """Handle position change from primary player"""
        self.current_position = position
        self.positionChanged.emit(position)
    
    def handle_state_changed(self, state):
        """Handle playback state change from primary player"""
        self.is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.playbackStateChanged.emit(state)
        
        # Start/stop sync timer based on playback state
        if self.is_playing and not self.sync_timer.isActive():
            self.sync_timer.start()
        elif not self.is_playing and self.sync_timer.isActive():
            self.sync_timer.stop()
    
    def check_synchronization(self):
        """Check and correct synchronization between players"""
        if not self.primary_player or not self.is_playing:
            return
            
        primary_pos = self.primary_player.position()
        
        # Threshold for sync correction (in ms)
        sync_threshold = 50
        
        for player in self.players:
            if player != self.primary_player:
                # Check if player is out of sync
                if abs(player.position() - primary_pos) > sync_threshold:
                    player.setPosition(primary_pos)
    
    def play(self):
        """Start playback of all media players"""
        for player in self.players:
            player.play()
        self.is_playing = True
        self.sync_timer.start()
    
    def pause(self):
        """Pause playback of all media players"""
        for player in self.players:
            player.pause()
        self.is_playing = False
        self.sync_timer.stop()
    
    def stop(self):
        """Stop playback of all media players"""
        for player in self.players:
            player.stop()
        self.is_playing = False
        self.sync_timer.stop()
    
    def set_position(self, position):
        """Set position of all media players"""
        for player in self.players:
            player.setPosition(position)
        self.current_position = position
    
    def set_muted(self, player, muted):
        """Set muted state for a specific player"""
        if player in self.players:
            player.audioOutput().setMuted(muted)

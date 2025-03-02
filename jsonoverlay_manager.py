import sys
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt, QRectF
from custom_rect_item import CustomRectItem
from video_player import VideoPlayer

class JSONOverlayManager:
    def __init__(self, player, json_path):
        self.player = player
        self.overlays = []
        self.frame_data = {}
        self.current_visible = 0
        self.video_width = 752  # Default, will be updated from metadata
        self.video_height = 300
        
        # Load and parse JSON data
        self.load_json_data(json_path)
        self.create_overlays()
        self.connect_signals()

    def load_json_data(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Store video dimensions from metadata
        if 'metadata' in data and 'width' in data['metadata'] and 'height' in data['metadata']:
            self.video_width = data['metadata']['width']
            self.video_height = data['metadata']['height']
            
        # Convert frames list to dictionary for faster lookup
        self.frame_data = {frame['fr']: frame['obj'] for frame in data['frames']}

    def create_overlays(self):
        # Create maximum number of rectangles (23)
        for _ in range(23):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            rect.setPen(QPen(Qt.GlobalColor.red, 2))
            self.overlays.append(rect)
            self.player.scene.addItem(rect)

    def connect_signals(self):
        self.player.viewResized.connect(self.update_view_size)
        self.player.media_player.positionChanged.connect(self.update_overlays)
        self.player.viewResized.connect(self.update_all_overlays)

    def update_view_size(self):
        self.view_width = self.player.view.width()
        self.view_height = self.player.view.height()
        self.scale_x = self.view_width / self.video_width
        self.scale_y = self.view_height / self.video_height

    def update_all_overlays(self):
        current_frame = self.player.current_frame
        self.update_overlays(self.player.media_player.position())

    def update_overlays(self, position):
        if not self.player.duration:
            return
            
        # Calculate current frame
        current_frame = self.player.current_frame 
        
        # Get objects for current frame
        frame_objects = self.frame_data.get(self.player.current_frame, [])
        
        # Update overlays
        for idx, overlay in enumerate(self.overlays):
            if idx < len(frame_objects):
                obj = frame_objects[idx]
                # Convert coordinates to view space
                x = (obj['t_c'][0] + (347 if obj['src'] == 1  else 0 )) * self.scale_x
                y = (300-obj['t_c'][1]) * self.scale_y
                w = 20 * self.scale_x #(obj['bbox'][2] - obj['bbox'][0]) * self.scale_x
                h = 20 * self.scale_y #(obj['bbox'][3] - obj['bbox'][1]) * self.scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
            else:
                overlay.setVisible(False)


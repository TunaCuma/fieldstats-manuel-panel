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
        self.topdown_overlays = []  # For transformed view (bottom)
        self.left_overlays = []     # For left field view
        self.right_overlays = []    # For right field view
        self.frame_data = {}
        
        # Default dimensions - will be updated from metadata if available
        self.topdown_width = 752
        self.topdown_height = 300
        self.field_width = 1920
        self.field_height = 1080
        
        # Scale factors for each view
        self.topdown_scale_x = 1.0
        self.topdown_scale_y = 1.0
        self.left_scale_x = 1.0
        self.left_scale_y = 1.0
        self.right_scale_x = 1.0
        self.right_scale_y = 1.0
        
        # Load and parse JSON data
        self.load_json_data(json_path)
        self.create_overlays()
        self.connect_signals()
    
    def load_json_data(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Store video dimensions from metadata if available
        if 'metadata' in data:
            metadata = data['metadata']
            if 'width' in metadata and 'height' in metadata:
                self.topdown_width = metadata.get('width', self.topdown_width)
                self.topdown_height = metadata.get('height', self.topdown_height)
            if 'field_width' in metadata and 'field_height' in metadata:
                self.field_width = metadata.get('field_width', self.field_width)
                self.field_height = metadata.get('field_height', self.field_height)
            
        # Convert frames list to dictionary for faster lookup
        self.frame_data = {frame['fr']: frame['obj'] for frame in data['frames']}
    
    def create_overlays(self):
        # Maximum number of rectangles per view
        max_overlays = 30
        
        # Create overlays for transformed view (bottom)
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            orange_pen = QPen(QColor("orange"), 3)
            rect.setPen(orange_pen)
            self.topdown_overlays.append(rect)
            self.player.scene.addItem(rect)
            rect.setVisible(False)

        # Create overlays for left field view
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            green_pen = QPen(QColor("green"), 3)
            rect.setPen(green_pen)
            self.left_overlays.append(rect)
            self.player.left_scene.addItem(rect)
            rect.setVisible(False)

        # Create overlays for right field view
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            blue_pen = QPen(QColor("blue"), 3)
            rect.setPen(blue_pen)
            self.right_overlays.append(rect)
            self.player.right_scene.addItem(rect)
            rect.setVisible(False)
    
    def connect_signals(self):
        self.player.viewResized.connect(self.update_view_sizes)
        self.player.media_player.positionChanged.connect(self.update_overlays)
        self.player.viewResized.connect(self.update_all_overlays)
    
    def update_view_sizes(self):
        """Update scaling factors based on the actual video item sizes rather than view sizes"""
        # Get the video item sizes (respecting aspect ratio)
        # For transformed view
        if self.player.video_item.size().width() > 0:
            self.topdown_view_width = self.player.video_item.size().width()
            self.topdown_view_height = self.player.video_item.size().height()
        else:
            self.topdown_view_width = self.player.view.width()
            self.topdown_view_height = self.player.view.height()
            
        # For left field view
        if self.player.left_video_item.size().width() > 0:
            self.left_view_width = self.player.left_video_item.size().width()
            self.left_view_height = self.player.left_video_item.size().height()
        else:
            self.left_view_width = self.player.left_view.width()
            self.left_view_height = self.player.left_view.height()
            
        # For right field view
        if self.player.right_video_item.size().width() > 0:
            self.right_view_width = self.player.right_video_item.size().width()
            self.right_view_height = self.player.right_video_item.size().height()
        else:
            self.right_view_width = self.player.right_view.width()
            self.right_view_height = self.player.right_view.height()
        
        # Calculate scale factors
        self.topdown_scale_x = self.topdown_view_width / self.topdown_width
        self.topdown_scale_y = self.topdown_view_height / self.topdown_height
        self.left_scale_x = self.left_view_width / self.field_width
        self.left_scale_y = self.left_view_height / self.field_height
        self.right_scale_x = self.right_view_width / self.field_width
        self.right_scale_y = self.right_view_height / self.field_height
    
    def update_all_overlays(self):
        self.update_overlays(self.player.media_player.position())
    
    def update_overlays(self, position):
        if not self.player.duration:
            return
            
        # Calculate current frame
        current_frame = self.player.current_frame 
        
        # Get objects for current frame
        frame_objects = self.frame_data.get(current_frame, [])
        
        # Lists to store objects by source
        transformed_objects = []  # For topdown view
        left_objects = []         # For left field (src=0)
        right_objects = []        # For right field (src=1)
        
        # Separate objects by source
        for obj in frame_objects:
            # Add to transformed view (all objects)
            transformed_objects.append(obj)
            
            # Add to appropriate field view based on src
            if obj['src'] == 0:
                left_objects.append(obj)
            elif obj['src'] == 1:
                right_objects.append(obj)
        
        # Update topdown view overlays (using t_c coordinates)
        for idx, overlay in enumerate(self.topdown_overlays):
            if idx < len(transformed_objects):
                obj = transformed_objects[idx]
                # Use transformed center coordinates
                # Account for video item position offset due to aspect ratio scaling
                x_offset = self.player.video_item.pos().x()
                y_offset = self.player.video_item.pos().y()
                
                # Add half the video width to objects from right field (src=1)
                x_position = obj['t_c'][0]
                if obj['src'] == 1:
                    x_position += self.topdown_width / 2 - 20  # Adjust by 20 pixels to fix positioning
                
                x = x_offset + (x_position - 10) * self.topdown_scale_x
                y = y_offset + (obj['t_c'][1] - 10) * self.topdown_scale_y
                w = 20 * self.topdown_scale_x
                h = 20 * self.topdown_scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback to show info about the object
                obj_info = obj.copy()  # Create a copy for the callback closure
                overlay.setClickCallback(lambda info=obj_info: self.show_object_info(info))
            else:
                overlay.setVisible(False)
        
        # Update left field overlays (using bbox coordinates)
        for idx, overlay in enumerate(self.left_overlays):
            if idx < len(left_objects):
                obj = left_objects[idx]
                # Use bounding box coordinates
                # Account for video item position offset due to aspect ratio scaling
                x_offset = self.player.left_video_item.pos().x()
                y_offset = self.player.left_video_item.pos().y()
                
                x = x_offset + obj['bbox'][0] * self.left_scale_x
                y = y_offset + obj['bbox'][1] * self.left_scale_y
                w = (obj['bbox'][2] - obj['bbox'][0]) * self.left_scale_x
                h = (obj['bbox'][3] - obj['bbox'][1]) * self.left_scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.show_object_info(info))
            else:
                overlay.setVisible(False)
        
        # Update right field overlays (using bbox coordinates)
        for idx, overlay in enumerate(self.right_overlays):
            if idx < len(right_objects):
                obj = right_objects[idx]
                # Use bounding box coordinates
                # Account for video item position offset due to aspect ratio scaling
                x_offset = self.player.right_video_item.pos().x()
                y_offset = self.player.right_video_item.pos().y()
                
                x = x_offset + obj['bbox'][0] * self.right_scale_x
                y = y_offset + obj['bbox'][1] * self.right_scale_y
                w = (obj['bbox'][2] - obj['bbox'][0]) * self.right_scale_x
                h = (obj['bbox'][3] - obj['bbox'][1]) * self.right_scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def show_object_info(self, obj_info):
        """Display information about the clicked object"""
        source = "Left Field" if obj_info['src'] == 0 else "Right Field"
        # Display adjusted position for right field objects in topdown view
        x_position = obj_info['t_c'][0]
        if obj_info['src'] == 1:
            x_position += self.topdown_width / 2 - 20  # Apply the same 20 pixel adjustment
        info_text = f"Source: {source}, Position: ({x_position:.1f}, {obj_info['t_c'][1]:.1f})"
        self.player.click_info_label.setText(info_text)

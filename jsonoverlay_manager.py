import json
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt, QRectF
from custom_rect_item import CustomRectItem

class JSONOverlayManager:
    def __init__(self, player, json_path):
        self.player = player
        self.topdown_overlays = []  # For transformed view (bottom)
        self.left_overlays = []     # For left field view
        self.right_overlays = []    # For right field view
        self.detached_topdown_overlays = []  # For detached transformed view
        self.detached_left_overlays = []     # For detached left field view
        self.detached_right_overlays = []    # For detached right field view
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
            self.player.transform_view.scene.addItem(rect)
            rect.setVisible(False)

        # Create overlays for left field view
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            green_pen = QPen(QColor("green"), 3)
            rect.setPen(green_pen)
            self.left_overlays.append(rect)
            self.player.left_view.scene.addItem(rect)
            rect.setVisible(False)

        # Create overlays for right field view
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            # Set the pen before any hover events occur
            blue_pen = QPen(QColor("blue"), 3)
            rect.setPen(blue_pen)
            self.right_overlays.append(rect)
            self.player.right_view.scene.addItem(rect)
            rect.setVisible(False)
    
    def connect_signals(self):
        self.player.viewResized.connect(self.update_view_sizes)
        self.player.media_player.positionChanged.connect(self.update_overlays)
        self.player.viewResized.connect(self.update_all_overlays)
        
        # Connect signals for detached windows
        self.player.left_view.detachRequested.connect(self.create_detached_left_overlays)
        self.player.right_view.detachRequested.connect(self.create_detached_right_overlays)
        self.player.transform_view.detachRequested.connect(self.create_detached_transform_overlays)
        
        # Connect signals for reattaching
        self.player.left_view.reattachRequested.connect(self.clean_detached_left_overlays)
        self.player.right_view.reattachRequested.connect(self.clean_detached_right_overlays)
        self.player.transform_view.reattachRequested.connect(self.clean_detached_transform_overlays)
    
    def update_view_sizes(self):
        """Update scaling factors based on the actual video item sizes rather than view sizes"""
        # Get the video item sizes (respecting aspect ratio)
        # For transformed view
        if self.player.transform_view.video_item.size().width() > 0:
            self.topdown_view_width = self.player.transform_view.video_item.size().width()
            self.topdown_view_height = self.player.transform_view.video_item.size().height()
        else:
            self.topdown_view_width = self.player.transform_view.view.width()
            self.topdown_view_height = self.player.transform_view.view.height()
            
        # For left field view
        if self.player.left_view.video_item.size().width() > 0:
            self.left_view_width = self.player.left_view.video_item.size().width()
            self.left_view_height = self.player.left_view.video_item.size().height()
        else:
            self.left_view_width = self.player.left_view.view.width()
            self.left_view_height = self.player.left_view.view.height()
            
        # For right field view
        if self.player.right_view.video_item.size().width() > 0:
            self.right_view_width = self.player.right_view.video_item.size().width()
            self.right_view_height = self.player.right_view.video_item.size().height()
        else:
            self.right_view_width = self.player.right_view.view.width()
            self.right_view_height = self.player.right_view.view.height()
        
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
        self.update_topdown_overlays(transformed_objects)
        
        # Update left field overlays (using bbox coordinates)
        self.update_left_overlays(left_objects)
        
        # Update right field overlays (using bbox coordinates)
        self.update_right_overlays(right_objects)
        
        # Update detached window overlays if they exist
        if self.player.transform_view.detached_window and self.detached_topdown_overlays:
            self.update_detached_topdown_overlays(transformed_objects)
            
        if self.player.left_view.detached_window and self.detached_left_overlays:
            self.update_detached_left_overlays(left_objects)
            
        if self.player.right_view.detached_window and self.detached_right_overlays:
            self.update_detached_right_overlays(right_objects)
    
    def update_topdown_overlays(self, transformed_objects):
        """Update overlays for the main transform view"""
        for idx, overlay in enumerate(self.topdown_overlays):
            if idx < len(transformed_objects):
                obj = transformed_objects[idx]
                
                # Use transformed center coordinates
                # Get the direct video item position 
                video_rect = self.player.transform_view.video_item.boundingRect()
                x_offset = self.player.transform_view.video_item.pos().x()
                y_offset = self.player.transform_view.video_item.pos().y()
                
                # Add half the video width to objects from right field (src=1)
                x_position = obj['t_c'][0]
                if obj['src'] == 1:
                    x_position += self.topdown_width / 2 - 20  # Adjust by 20 pixels to fix positioning
                
                # Position in the middle of the object with correct scaling
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
    
    def update_left_overlays(self, left_objects):
        """Update overlays for the main left field view"""
        for idx, overlay in enumerate(self.left_overlays):
            if idx < len(left_objects) and self.player.is_left_visible:
                obj = left_objects[idx]
                
                # Get the direct video item position
                video_rect = self.player.left_view.video_item.boundingRect()
                x_offset = self.player.left_view.video_item.pos().x()
                y_offset = self.player.left_view.video_item.pos().y()
                
                # Calculate rectangle position and size
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
    
    def update_right_overlays(self, right_objects):
        """Update overlays for the main right field view"""
        for idx, overlay in enumerate(self.right_overlays):
            if idx < len(right_objects) and self.player.is_right_visible:
                obj = right_objects[idx]
                
                # Get the direct video item position
                video_rect = self.player.right_view.video_item.boundingRect()
                x_offset = self.player.right_view.video_item.pos().x()
                y_offset = self.player.right_view.video_item.pos().y()
                
                # Calculate rectangle position and size
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
    
    def create_detached_left_overlays(self):
        """Create overlays for detached left field view"""
        if not self.player.left_view.detached_window:
            return
            
        # Clean any existing overlays
        self.clean_detached_left_overlays()
        
        # Create new overlays
        max_overlays = 30
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            green_pen = QPen(QColor("green"), 3)
            rect.setPen(green_pen)
            self.detached_left_overlays.append(rect)
            self.player.left_view.detached_window.scene.addItem(rect)
            rect.setVisible(False)
    
    def create_detached_right_overlays(self):
        """Create overlays for detached right field view"""
        if not self.player.right_view.detached_window:
            return
            
        # Clean any existing overlays
        self.clean_detached_right_overlays()
        
        # Create new overlays
        max_overlays = 30
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            blue_pen = QPen(QColor("blue"), 3)
            rect.setPen(blue_pen)
            self.detached_right_overlays.append(rect)
            self.player.right_view.detached_window.scene.addItem(rect)
            rect.setVisible(False)
    
    def create_detached_transform_overlays(self):
        """Create overlays for detached transform view"""
        if not self.player.transform_view.detached_window:
            return
            
        # Clean any existing overlays
        self.clean_detached_transform_overlays()
        
        # Create new overlays
        max_overlays = 30
        for _ in range(max_overlays):
            rect = CustomRectItem(0, 0, 0, 0)
            rect.setBrush(QBrush(Qt.GlobalColor.transparent))
            orange_pen = QPen(QColor("orange"), 3)
            rect.setPen(orange_pen)
            self.detached_topdown_overlays.append(rect)
            self.player.transform_view.detached_window.scene.addItem(rect)
            rect.setVisible(False)
    
    def clean_detached_left_overlays(self):
        """Clean overlays from detached left field view"""
        for rect in self.detached_left_overlays:
            if rect.scene():
                rect.scene().removeItem(rect)
        self.detached_left_overlays.clear()
    
    def clean_detached_right_overlays(self):
        """Clean overlays from detached right field view"""
        for rect in self.detached_right_overlays:
            if rect.scene():
                rect.scene().removeItem(rect)
        self.detached_right_overlays.clear()
    
    def clean_detached_transform_overlays(self):
        """Clean overlays from detached transform view"""
        for rect in self.detached_topdown_overlays:
            if rect.scene():
                rect.scene().removeItem(rect)
        self.detached_topdown_overlays.clear()
    
    def update_detached_topdown_overlays(self, transformed_objects):
        """Update overlays for the detached transform view"""
        detached_window = self.player.transform_view.detached_window
        if not detached_window:
            return
            
        # Calculate scale factors for detached window
        video_size = detached_window.video_item.size()
        if video_size.width() > 0:
            scale_x = video_size.width() / self.topdown_width
            scale_y = video_size.height() / self.topdown_height
        else:
            scale_x = self.topdown_scale_x
            scale_y = self.topdown_scale_y
            
        for idx, overlay in enumerate(self.detached_topdown_overlays):
            if idx < len(transformed_objects):
                obj = transformed_objects[idx]
                
                # Get video item position
                video_rect = detached_window.video_item.boundingRect()
                x_offset = detached_window.video_item.pos().x()
                y_offset = detached_window.video_item.pos().y()
                
                # Add half the video width to objects from right field (src=1)
                x_position = obj['t_c'][0]
                if obj['src'] == 1:
                    x_position += self.topdown_width / 2 - 20
                
                # Position overlay
                x = x_offset + (x_position - 10) * scale_x
                y = y_offset + (obj['t_c'][1] - 10) * scale_y
                w = 20 * scale_x
                h = 20 * scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_detached_left_overlays(self, left_objects):
        """Update overlays for the detached left field view"""
        detached_window = self.player.left_view.detached_window
        if not detached_window:
            return
            
        # Calculate scale factors for detached window
        video_size = detached_window.video_item.size()
        if video_size.width() > 0:
            scale_x = video_size.width() / self.field_width
            scale_y = video_size.height() / self.field_height
        else:
            scale_x = self.left_scale_x
            scale_y = self.left_scale_y
            
        for idx, overlay in enumerate(self.detached_left_overlays):
            if idx < len(left_objects):
                obj = left_objects[idx]
                
                # Get video item position
                video_rect = detached_window.video_item.boundingRect()
                x_offset = detached_window.video_item.pos().x()
                y_offset = detached_window.video_item.pos().y()
                
                # Position overlay
                x = x_offset + obj['bbox'][0] * scale_x
                y = y_offset + obj['bbox'][1] * scale_y
                w = (obj['bbox'][2] - obj['bbox'][0]) * scale_x
                h = (obj['bbox'][3] - obj['bbox'][1]) * scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_detached_right_overlays(self, right_objects):
        """Update overlays for the detached right field view"""
        detached_window = self.player.right_view.detached_window
        if not detached_window:
            return
            
        # Calculate scale factors for detached window
        video_size = detached_window.video_item.size()
        if video_size.width() > 0:
            scale_x = video_size.width() / self.field_width
            scale_y = video_size.height() / self.field_height
        else:
            scale_x = self.right_scale_x
            scale_y = self.right_scale_y
            
        for idx, overlay in enumerate(self.detached_right_overlays):
            if idx < len(right_objects):
                obj = right_objects[idx]
                
                # Get video item position
                video_rect = detached_window.video_item.boundingRect()
                x_offset = detached_window.video_item.pos().x()
                y_offset = detached_window.video_item.pos().y()
                
                # Position overlay
                x = x_offset + obj['bbox'][0] * scale_x
                y = y_offset + obj['bbox'][1] * scale_y
                w = (obj['bbox'][2] - obj['bbox'][0]) * scale_x
                h = (obj['bbox'][3] - obj['bbox'][1]) * scale_y
                
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

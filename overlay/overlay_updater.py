from PyQt6.QtCore import QRectF

class OverlayUpdater:
    """Responsible for updating overlay positions and visibility"""
    
    def __init__(self, manager):
        self.manager = manager
    
    def update_topdown_overlays(self, transformed_objects):
        """Update overlays for the main transform view"""
        for idx, overlay in enumerate(self.manager.topdown_overlays):
            if idx < len(transformed_objects):
                obj = transformed_objects[idx]
                
                # Use transformed center coordinates
                # Get the direct video item position 
                video_rect = self.manager.player.transform_view.video_item.boundingRect()
                x_offset = self.manager.player.transform_view.video_item.pos().x()
                y_offset = self.manager.player.transform_view.video_item.pos().y()
                
                # Add half the video width to objects from right field (src=1)
                x_position = obj['t_c'][0]
                if obj['src'] == 1:
                    x_position += self.manager.topdown_width / 2 - 20  # Adjust by 20 pixels to fix positioning
                
                # Position in the middle of the object with correct scaling
                x = x_offset + (x_position - 10) * self.manager.topdown_scale_x
                y = y_offset + (obj['t_c'][1] - 10) * self.manager.topdown_scale_y
                w = 20 * self.manager.topdown_scale_x
                h = 20 * self.manager.topdown_scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback to show info about the object
                obj_info = obj.copy()  # Create a copy for the callback closure
                overlay.setClickCallback(lambda info=obj_info: self.manager.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_left_overlays(self, left_objects):
        """Update overlays for the main left field view"""
        for idx, overlay in enumerate(self.manager.left_overlays):
            if idx < len(left_objects) and self.manager.player.is_left_visible:
                obj = left_objects[idx]
                
                # Get the direct video item position
                video_rect = self.manager.player.left_view.video_item.boundingRect()
                x_offset = self.manager.player.left_view.video_item.pos().x()
                y_offset = self.manager.player.left_view.video_item.pos().y()
                
                # Calculate rectangle position and size
                x = x_offset + obj['bbox'][0] * self.manager.left_scale_x
                y = y_offset + obj['bbox'][1] * self.manager.left_scale_y
                w = (obj['bbox'][2] - obj['bbox'][0]) * self.manager.left_scale_x
                h = (obj['bbox'][3] - obj['bbox'][1]) * self.manager.left_scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.manager.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_right_overlays(self, right_objects):
        """Update overlays for the main right field view"""
        for idx, overlay in enumerate(self.manager.right_overlays):
            if idx < len(right_objects) and self.manager.player.is_right_visible:
                obj = right_objects[idx]
                
                # Get the direct video item position
                video_rect = self.manager.player.right_view.video_item.boundingRect()
                x_offset = self.manager.player.right_view.video_item.pos().x()
                y_offset = self.manager.player.right_view.video_item.pos().y()
                
                # Calculate rectangle position and size
                x = x_offset + obj['bbox'][0] * self.manager.right_scale_x
                y = y_offset + obj['bbox'][1] * self.manager.right_scale_y
                w = (obj['bbox'][2] - obj['bbox'][0]) * self.manager.right_scale_x
                h = (obj['bbox'][3] - obj['bbox'][1]) * self.manager.right_scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.manager.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_detached_topdown_overlays(self, transformed_objects):
        """Update overlays for the detached transform view"""
        detached_window = self.manager.player.transform_view.detached_window
        if not detached_window:
            return
            
        # Calculate scale factors for detached window
        video_size = detached_window.video_item.size()
        if video_size.width() > 0:
            scale_x = video_size.width() / self.manager.topdown_width
            scale_y = video_size.height() / self.manager.topdown_height
        else:
            scale_x = self.manager.topdown_scale_x
            scale_y = self.manager.topdown_scale_y
            
        for idx, overlay in enumerate(self.manager.detached_topdown_overlays):
            if idx < len(transformed_objects):
                obj = transformed_objects[idx]
                
                # Get video item position
                video_rect = detached_window.video_item.boundingRect()
                x_offset = detached_window.video_item.pos().x()
                y_offset = detached_window.video_item.pos().y()
                
                # Add half the video width to objects from right field (src=1)
                x_position = obj['t_c'][0]
                if obj['src'] == 1:
                    x_position += self.manager.topdown_width / 2 - 20
                
                # Position overlay
                x = x_offset + (x_position - 10) * scale_x
                y = y_offset + (obj['t_c'][1] - 10) * scale_y
                w = 20 * scale_x
                h = 20 * scale_y
                
                overlay.setRect(QRectF(x, y, w, h))
                overlay.setVisible(True)
                
                # Setup click callback
                obj_info = obj.copy()
                overlay.setClickCallback(lambda info=obj_info: self.manager.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_detached_left_overlays(self, left_objects):
        """Update overlays for the detached left field view"""
        detached_window = self.manager.player.left_view.detached_window
        if not detached_window:
            return
            
        # Calculate scale factors for detached window
        video_size = detached_window.video_item.size()
        if video_size.width() > 0:
            scale_x = video_size.width() / self.manager.field_width
            scale_y = video_size.height() / self.manager.field_height
        else:
            scale_x = self.manager.left_scale_x
            scale_y = self.manager.left_scale_y
            
        for idx, overlay in enumerate(self.manager.detached_left_overlays):
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
                overlay.setClickCallback(lambda info=obj_info: self.manager.show_object_info(info))
            else:
                overlay.setVisible(False)
    
    def update_detached_right_overlays(self, right_objects):
        """Update overlays for the detached right field view"""
        detached_window = self.manager.player.right_view.detached_window
        if not detached_window:
            return
            
        # Calculate scale factors for detached window
        video_size = detached_window.video_item.size()
        if video_size.width() > 0:
            scale_x = video_size.width() / self.manager.field_width
            scale_y = video_size.height() / self.manager.field_height
        else:
            scale_x = self.manager.right_scale_x
            scale_y = self.manager.right_scale_y
            
        for idx, overlay in enumerate(self.manager.detached_right_overlays):
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
                overlay.setClickCallback(lambda info=obj_info: self.manager.show_object_info(info))
            else:
                overlay.setVisible(False)

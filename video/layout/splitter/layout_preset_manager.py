class LayoutPresetManager:
    """Manages layout presets for splitters"""
    
    def __init__(self, vertical_manager, horizontal_manager):
        """
        Initialize with references to the splitter managers
        
        Args:
            vertical_manager: The vertical splitter manager
            horizontal_manager: The horizontal splitter manager
        """
        self.vertical_manager = vertical_manager
        self.horizontal_manager = horizontal_manager
    
    def apply_preset(self, preset):
        """
        Apply a layout preset
        
        Args:
            preset: The preset name to apply ("equal", "top", or "bottom")
        """
        # Get direct references to the containers
        top_container = self.vertical_manager.top_container
        bottom_container = self.vertical_manager.bottom_container
        
        top_container.setMaximumHeight(16777215)  # Qt's QWIDGETSIZE_MAX
        bottom_container.setMaximumHeight(16777215)  # Qt's QWIDGETSIZE_MAX
        
        if preset == "equal":
            # Equal split between top and bottom
            self.vertical_manager.set_sizes([500, 500])
            # Equal split between left and right
            self.horizontal_manager.set_sizes([500, 500])
            # Update saved sizes
            self.vertical_manager.save_sizes()
            self.horizontal_manager.save_sizes()
            
        elif preset == "top":
            # More space for the top views
            self.vertical_manager.set_sizes([700, 300])
            self.vertical_manager.save_sizes()
            
        elif preset == "bottom":
            # More space for the bottom view
            self.vertical_manager.set_sizes([300, 700])
            self.vertical_manager.save_sizes()

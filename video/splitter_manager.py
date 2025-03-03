from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt


class SplitterManager:
    """Manages splitters for resizing view containers"""
    
    def __init__(self):
        # Remember original splitter proportions to restore them when unhiding
        self.last_horizontal_sizes = None
        self.last_vertical_sizes = None
        
        self.setup_splitters()
        
    def setup_splitters(self):
        # Create main vertical splitter
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setContentsMargins(0, 0, 0, 0)
        self.main_splitter.setHandleWidth(8)  # Thicker handle for better visibility
        
        # Apply the dark theme splitter styling
        self.splitter_style = """
            QSplitter::handle {
                background-color: #353535;
                border: 1px solid #424242;
            }
            QSplitter::handle:hover {
                background-color: #454545;
                border: 1px solid #555555;
            }
            QSplitter::handle:pressed {
                background-color: #505050;
            }
        """
        self.main_splitter.setStyleSheet(self.splitter_style)
        
        # Top container for left and right field videos
        self.top_container = QWidget()
        self.top_layout = QVBoxLayout(self.top_container)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        
        # Create horizontal splitter for left and right views
        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.horizontal_splitter.setContentsMargins(0, 0, 0, 0)
        self.horizontal_splitter.setHandleWidth(8)  # Thicker handle for better visibility
        # Use the same styling as main splitter
        self.horizontal_splitter.setStyleSheet(self.splitter_style)
        self.top_layout.addWidget(self.horizontal_splitter)
        
        # Add the top container to the main splitter
        self.main_splitter.addWidget(self.top_container)
        
        # Bottom container for transformed view
        self.bottom_container = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_container)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(0)
        
        # Add bottom container to main splitter
        self.main_splitter.addWidget(self.bottom_container)
        
        # Set initial sizes (1:1 for top:bottom)
        self.main_splitter.setSizes([300, 300])
        self.last_vertical_sizes = [300, 300]

    def add_left_view(self, view):
        """Add view to the left side of the horizontal splitter"""
        self.horizontal_splitter.addWidget(view)
        
    def add_right_view(self, view):
        """Add view to the right side of the horizontal splitter"""
        self.horizontal_splitter.addWidget(view)
        
        # Save initial sizes after both views are added
        self.last_horizontal_sizes = self.horizontal_splitter.sizes()
        
    def add_transform_view(self, view):
        """Add view to the bottom container"""
        self.bottom_layout.addWidget(view)
    
    def handle_view_detach(self, view_name, views):
        """Handle when a view is detached to separate window"""
        # Handle horizontal splitter adjustments (left and right views)
        if view_name in ['left', 'right']:
            # Save current sizes before detaching
            if views['left']['visible'] and views['right']['visible']:
                self.last_horizontal_sizes = self.horizontal_splitter.sizes()
            
            # Get the indexes of the views in the splitter
            left_idx = self.horizontal_splitter.indexOf(views['left']['view'])
            right_idx = self.horizontal_splitter.indexOf(views['right']['view'])
            
            # When detaching left view
            if view_name == 'left' and views['right']['visible']:
                # Get the total width before changing
                total_width = sum(self.horizontal_splitter.sizes())
                # Create new sizes list with 0 for detached view
                new_sizes = [0] * self.horizontal_splitter.count()
                new_sizes[right_idx] = total_width
                self.horizontal_splitter.setSizes(new_sizes)
                
            # When detaching right view
            elif view_name == 'right' and views['left']['visible']:
                # Get the total width before changing
                total_width = sum(self.horizontal_splitter.sizes())
                # Create new sizes list with 0 for detached view
                new_sizes = [0] * self.horizontal_splitter.count()
                new_sizes[left_idx] = total_width
                self.horizontal_splitter.setSizes(new_sizes)
                
        # Handle vertical splitter for transform view
        elif view_name == 'transform':
            # Save current sizes
            self.last_vertical_sizes = self.main_splitter.sizes()
            
            # Get the indexes of the containers in the main splitter
            top_idx = self.main_splitter.indexOf(self.top_container)
            bottom_idx = self.main_splitter.indexOf(self.bottom_container)
            
            # Get the total height
            total_height = sum(self.main_splitter.sizes())
            
            # Create new sizes list with a minimal size for the detached section
            new_sizes = [0] * self.main_splitter.count()
            new_sizes[top_idx] = total_height - 30
            new_sizes[bottom_idx] = 30  # Just enough for the splitter handle
            self.main_splitter.setSizes(new_sizes)
    
    def handle_view_reattach(self, view_name):
        """Handle when a view is reattached from separate window"""
        # Restore the view
        if view_name in ['left', 'right'] and self.last_horizontal_sizes:
            self.horizontal_splitter.setSizes(self.last_horizontal_sizes)
        elif view_name == 'transform' and self.last_vertical_sizes:
            self.main_splitter.setSizes(self.last_vertical_sizes)
        
    def handle_view_visibility(self, view_name, is_visible, views):
        """Respond to view visibility changes and adjust layout"""
        # Handle horizontal splitter adjustments (left and right views)
        if view_name in ['left', 'right']:
            # Save current sizes before hiding
            if not is_visible and views['left']['visible'] and views['right']['visible']:
                self.last_horizontal_sizes = self.horizontal_splitter.sizes()
            
            # If hiding one view, give all space to the other view
            if not is_visible:
                # First get the indexes of the views in the splitter
                left_idx = self.horizontal_splitter.indexOf(views['left']['view'])
                right_idx = self.horizontal_splitter.indexOf(views['right']['view'])
                
                # When hiding left view
                if view_name == 'left' and views['right']['visible']:
                    # Get the total width before changing
                    total_width = sum(self.horizontal_splitter.sizes())
                    # Create new sizes list with 0 for hidden view
                    new_sizes = [0] * self.horizontal_splitter.count()
                    new_sizes[right_idx] = total_width
                    self.horizontal_splitter.setSizes(new_sizes)
                    
                # When hiding right view
                elif view_name == 'right' and views['left']['visible']:
                    # Get the total width before changing
                    total_width = sum(self.horizontal_splitter.sizes())
                    # Create new sizes list with 0 for hidden view
                    new_sizes = [0] * self.horizontal_splitter.count()
                    new_sizes[left_idx] = total_width
                    self.horizontal_splitter.setSizes(new_sizes)
                    
            # If unhiding a view and both are now visible, restore original proportions
            elif is_visible and views['left']['visible'] and views['right']['visible'] and self.last_horizontal_sizes:
                self.horizontal_splitter.setSizes(self.last_horizontal_sizes)
        
        # Handle vertical splitter adjustments (top vs bottom)
        # Save current sizes before hiding
        if (view_name in ['left', 'right'] and all(not views[v]['visible'] for v in ['left', 'right'])) or \
           (view_name == 'transform' and not is_visible):
            self.last_vertical_sizes = self.main_splitter.sizes()
        
        # If both top views are hidden, give all space to bottom
        if all(not views[v]['visible'] for v in ['left', 'right']) and views['transform']['visible']:
            # Get the indexes of the containers in the main splitter
            top_idx = self.main_splitter.indexOf(self.top_container)
            bottom_idx = self.main_splitter.indexOf(self.bottom_container)
            
            # Get the total height
            total_height = sum(self.main_splitter.sizes())
            
            # Create new sizes list with a minimal size for the hidden section
            new_sizes = [0] * self.main_splitter.count()
            new_sizes[top_idx] = 30  # Just enough for the splitter handle
            new_sizes[bottom_idx] = total_height - 30
            self.main_splitter.setSizes(new_sizes)
            
        # If bottom view is hidden, give all space to top
        elif not views['transform']['visible'] and any(views[v]['visible'] for v in ['left', 'right']):
            # Get the indexes of the containers in the main splitter
            top_idx = self.main_splitter.indexOf(self.top_container)
            bottom_idx = self.main_splitter.indexOf(self.bottom_container)
            
            # Get the total height
            total_height = sum(self.main_splitter.sizes())
            
            # Create new sizes list with a minimal size for the hidden section
            new_sizes = [0] * self.main_splitter.count()
            new_sizes[top_idx] = total_height - 30
            new_sizes[bottom_idx] = 30  # Just enough for the splitter handle
            self.main_splitter.setSizes(new_sizes)
            
        # If everything is visible again, restore original proportions
        elif any(views[v]['visible'] for v in ['left', 'right']) and views['transform']['visible'] and self.last_vertical_sizes:
            self.main_splitter.setSizes(self.last_vertical_sizes)

    def apply_layout_preset(self, preset):
        """Apply a layout preset"""
        # First ensure containers have no maximum height constraints
        self.top_container.setMaximumHeight(16777215)  # Qt's QWIDGETSIZE_MAX
        self.bottom_container.setMaximumHeight(16777215)  # Qt's QWIDGETSIZE_MAX
        
        if preset == "equal":
            # Equal split between top and bottom
            self.main_splitter.setSizes([500, 500])
            # Equal split between left and right
            self.horizontal_splitter.setSizes([500, 500])
            # Update saved sizes
            self.last_vertical_sizes = [500, 500]
            self.last_horizontal_sizes = [500, 500]
            
        elif preset == "top":
            # More space for the top views
            self.main_splitter.setSizes([700, 300])
            self.last_vertical_sizes = [700, 300]
            
        elif preset == "bottom":
            # More space for the bottom view
            self.main_splitter.setSizes([300, 700])
            self.last_vertical_sizes = [300, 700]

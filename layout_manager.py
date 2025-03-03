from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QMenu, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

class LayoutManager(QWidget):
    """Manages the layout of video views with splitters for resizing"""
    viewResized = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Track view visibility status
        self.views = {
            'left': {'view': None, 'visible': True, 'container': None},
            'right': {'view': None, 'visible': True, 'container': None},
            'transform': {'view': None, 'visible': True, 'container': None}
        }
        
        # Remember original splitter proportions to restore them when unhiding
        self.last_horizontal_sizes = None
        self.last_vertical_sizes = None
        
        self.setupUI()
        
    def setupUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create main vertical splitter
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setContentsMargins(0, 0, 0, 0)
        self.main_splitter.setHandleWidth(1)  # Smaller handle
        
        # Top container for left and right field videos
        self.top_container = QWidget()
        self.top_layout = QVBoxLayout(self.top_container)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        
        # Create horizontal splitter for left and right views
        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.horizontal_splitter.setContentsMargins(0, 0, 0, 0)
        self.horizontal_splitter.setHandleWidth(1)  # Smaller handle
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
        
        # Add the main splitter to the layout
        self.layout.addWidget(self.main_splitter)
        
        # Set initial sizes (1:1 for top:bottom)
        self.main_splitter.setSizes([300, 300])
        self.last_vertical_sizes = [300, 300]
        
        # Layout customization menu button
        self.layout_menu_btn = QPushButton("Layout ▼")
        self.layout_menu_btn.clicked.connect(self.show_layout_menu)
        
        # Add layout menu button to a separate widget at the top
        self.menu_container = QWidget()
        self.menu_layout = QHBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(5, 5, 5, 5)
        
        self.layout_title = QLabel("Football Analysis Player")
        self.layout_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.menu_layout.addWidget(self.layout_title)
        self.menu_layout.addStretch()
        self.menu_layout.addWidget(self.layout_menu_btn)
        
        # Add to main layout at the top
        self.layout.insertWidget(0, self.menu_container)
        
    def add_left_view(self, view):
        """Add view to the left side of the horizontal splitter"""
        self.horizontal_splitter.addWidget(view)
        view.toggledVisibility.connect(lambda visible: self.handle_view_visibility('left', visible))
        self.views['left']['view'] = view
        self.views['left']['container'] = self.horizontal_splitter
        
    def add_right_view(self, view):
        """Add view to the right side of the horizontal splitter"""
        self.horizontal_splitter.addWidget(view)
        view.toggledVisibility.connect(lambda visible: self.handle_view_visibility('right', visible))
        self.views['right']['view'] = view
        self.views['right']['container'] = self.horizontal_splitter
        
        # Save initial sizes after both views are added
        self.last_horizontal_sizes = self.horizontal_splitter.sizes()
        
    def add_transform_view(self, view):
        """Add view to the bottom container"""
        self.bottom_layout.addWidget(view)
        view.toggledVisibility.connect(lambda visible: self.handle_view_visibility('transform', visible))
        self.views['transform']['view'] = view
        self.views['transform']['container'] = self.bottom_container
        
    def handle_view_visibility(self, view_name, is_visible):
        """Respond to view visibility changes and adjust layout"""
        # Update visibility state
        self.views[view_name]['visible'] = is_visible
        
        # Handle horizontal splitter adjustments (left and right views)
        if view_name in ['left', 'right']:
            # Save current sizes before hiding
            if not is_visible and self.views['left']['visible'] and self.views['right']['visible']:
                self.last_horizontal_sizes = self.horizontal_splitter.sizes()
            
            # If hiding one view, give all space to the other view
            if not is_visible:
                if view_name == 'left' and self.views['right']['visible']:
                    # Right view gets all space
                    self.horizontal_splitter.setSizes([0, 1])
                elif view_name == 'right' and self.views['left']['visible']:
                    # Left view gets all space
                    self.horizontal_splitter.setSizes([1, 0])
            # If unhiding a view and both are now visible, restore original proportions
            elif is_visible and self.views['left']['visible'] and self.views['right']['visible'] and self.last_horizontal_sizes:
                self.horizontal_splitter.setSizes(self.last_horizontal_sizes)
        
        # Handle vertical splitter adjustments (top vs bottom)
        # Save current sizes before hiding
        if (view_name in ['left', 'right'] and all(not self.views[v]['visible'] for v in ['left', 'right'])) or \
           (view_name == 'transform' and not is_visible):
            self.last_vertical_sizes = self.main_splitter.sizes()
        
        # If both top views are hidden, give all space to bottom
        if all(not self.views[v]['visible'] for v in ['left', 'right']) and self.views['transform']['visible']:
            self.main_splitter.setSizes([0, 1])
        # If bottom view is hidden, give all space to top
        elif not self.views['transform']['visible'] and any(self.views[v]['visible'] for v in ['left', 'right']):
            self.main_splitter.setSizes([1, 0])
        # If everything is visible again, restore original proportions
        elif any(self.views[v]['visible'] for v in ['left', 'right']) and self.views['transform']['visible'] and self.last_vertical_sizes:
            self.main_splitter.setSizes(self.last_vertical_sizes)
        
        # Emit signal for parent to handle resizing
        self.viewResized.emit()
    
    def show_layout_menu(self):
        """Show layout customization menu with view toggle options"""
        menu = QMenu(self)
        
        # Add layout presets
        split_equal_action = menu.addAction("Equal Split")
        split_equal_action.triggered.connect(lambda: self.apply_layout_preset("equal"))
        
        top_focus_action = menu.addAction("Focus on Fields")
        top_focus_action.triggered.connect(lambda: self.apply_layout_preset("top"))
        
        bottom_focus_action = menu.addAction("Focus on Transform")
        bottom_focus_action.triggered.connect(lambda: self.apply_layout_preset("bottom"))
        
        # Visibility options
        menu.addSeparator()
        menu.addAction("Show/Hide Views:").setEnabled(False)  # Section title
        
        # Add toggles for each view
        left_action = menu.addAction("Left Field")
        left_action.setCheckable(True)
        left_action.setChecked(self.views['left']['visible'])
        left_action.triggered.connect(lambda checked: self.toggle_view_visibility('left', checked))
        
        right_action = menu.addAction("Right Field")
        right_action.setCheckable(True)
        right_action.setChecked(self.views['right']['visible'])
        right_action.triggered.connect(lambda checked: self.toggle_view_visibility('right', checked))
        
        transform_action = menu.addAction("Transformed View")
        transform_action.setCheckable(True)
        transform_action.setChecked(self.views['transform']['visible'])
        transform_action.triggered.connect(lambda checked: self.toggle_view_visibility('transform', checked))
        
        # Show the menu below the button
        menu.exec(self.layout_menu_btn.mapToGlobal(
            self.layout_menu_btn.rect().bottomLeft()
        ))
    
    def toggle_view_visibility(self, view_name, should_be_visible):
        """Toggle visibility of a specific view from the menu"""
        view = self.views[view_name]['view']
        
        # Only act if the visibility state is changing
        if view and view.is_visible != should_be_visible:
            view.toggle_visibility()
    
    def apply_layout_preset(self, preset):
        """Apply a layout preset"""
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

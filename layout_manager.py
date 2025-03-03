from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QMenu, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

class LayoutManager(QWidget):
    """Manages the layout of video views with splitters for resizing"""
    viewResized = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create main vertical splitter
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top container for left and right field videos
        self.top_container = QWidget()
        self.top_layout = QVBoxLayout(self.top_container)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        
        # Create horizontal splitter for left and right views
        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
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
        view.toggledVisibility.connect(self.handle_view_visibility)
        
    def add_right_view(self, view):
        """Add view to the right side of the horizontal splitter"""
        self.horizontal_splitter.addWidget(view)
        view.toggledVisibility.connect(self.handle_view_visibility)
        
    def add_transform_view(self, view):
        """Add view to the bottom container"""
        self.bottom_layout.addWidget(view)
        view.toggledVisibility.connect(self.handle_view_visibility)
        
    def handle_view_visibility(self, is_visible):
        """Respond to view visibility changes"""
        self.viewResized.emit()
    
    def show_layout_menu(self):
        """Show layout customization menu"""
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
        menu.addAction("Show/Hide Panels")
        
        # Show the menu below the button
        menu.exec(self.layout_menu_btn.mapToGlobal(
            self.layout_menu_btn.rect().bottomLeft()
        ))
    
    def apply_layout_preset(self, preset):
        """Apply a layout preset"""
        if preset == "equal":
            # Equal split between top and bottom
            self.main_splitter.setSizes([500, 500])
            # Equal split between left and right
            self.horizontal_splitter.setSizes([500, 500])
            
        elif preset == "top":
            # More space for the top views
            self.main_splitter.setSizes([700, 300])
            
        elif preset == "bottom":
            # More space for the bottom view
            self.main_splitter.setSizes([300, 700])

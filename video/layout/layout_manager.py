from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .layout_menu import LayoutMenu
from .splitter.splitter_manager import SplitterManager
from .view_tracker import ViewTracker


class LayoutManager(QWidget):
    """Manages the layout of video views with splitters for resizing."""

    viewResized = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the view tracker
        self.view_tracker = ViewTracker()

        # Create the splitter manager
        self.splitter_manager = SplitterManager()

        # Setup the UI
        self.setupUI()

        # Create the layout menu handler
        self.layout_menu = LayoutMenu(
            self.layout_menu_btn, self.view_tracker, self.splitter_manager
        )

    def setupUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Add all splitters from the splitter manager
        self.layout.addWidget(self.splitter_manager.main_splitter)

        # Layout customization menu button
        self.layout_menu_btn = QPushButton("Layout ▼")
        self.layout_menu_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #424242;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #424242;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
        """
        )

        # Add layout menu button to a separate widget at the top
        self.menu_container = QWidget()
        self.menu_layout = QHBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(5, 5, 5, 5)

        self.layout_title = QLabel("Football Analysis Player")
        self.layout_title.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #ffffff;"
        )
        self.menu_layout.addWidget(self.layout_title)
        self.menu_layout.addStretch()
        self.menu_layout.addWidget(self.layout_menu_btn)

        # Add to main layout at the top
        self.layout.insertWidget(0, self.menu_container)

    def add_left_view(self, view):
        """Add view to the left side of the horizontal splitter."""
        self.splitter_manager.add_left_view(view)
        self.connect_view_signals(view, "left")
        self.view_tracker.register_view(
            "left", view, self.splitter_manager.horizontal_splitter
        )

    def add_right_view(self, view):
        """Add view to the right side of the horizontal splitter."""
        self.splitter_manager.add_right_view(view)
        self.connect_view_signals(view, "right")
        self.view_tracker.register_view(
            "right", view, self.splitter_manager.horizontal_splitter
        )

    def add_transform_view(self, view):
        """Add view to the bottom container."""
        self.splitter_manager.add_transform_view(view)
        self.connect_view_signals(view, "transform")
        self.view_tracker.register_view(
            "transform", view, self.splitter_manager.bottom_container
        )

    def connect_view_signals(self, view, view_name):
        """Connect signals from a view to our handlers."""
        view.toggledVisibility.connect(
            lambda visible: self.handle_view_visibility(view_name, visible)
        )
        view.detachRequested.connect(lambda: self.handle_view_detach(view_name))
        view.reattachRequested.connect(
            lambda: self.handle_view_reattach(view_name, self.view_tracker.views)
        )

    def handle_view_detach(self, view_name):
        """Handle when a view is detached to separate window."""
        self.splitter_manager.handle_view_detach(view_name, self.view_tracker.views)
        self.viewResized.emit()

    def handle_view_reattach(self, view_name, views):
        """Handle when a view is reattached from separate window."""
        self.splitter_manager.handle_view_reattach(view_name, views)
        self.viewResized.emit()

    def handle_view_visibility(self, view_name, is_visible):
        """Respond to view visibility changes and adjust layout."""
        self.view_tracker.update_visibility(view_name, is_visible)
        self.splitter_manager.handle_view_visibility(
            view_name, is_visible, self.view_tracker.views
        )
        self.viewResized.emit()

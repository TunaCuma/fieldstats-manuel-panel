from PyQt6.QtWidgets import QSplitter
from PyQt6.QtCore import Qt
from .styles import Styles


class HorizontalSplitterManager:
    """Manages horizontal splitting for left and right views"""

    def __init__(self):
        # Create horizontal splitter for left and right views
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)

        # Apply styling
        self.splitter.setStyleSheet(Styles.SPLITTER_STYLE)
        self.splitter.setHandleWidth(8)  # Thicker handle for better visibility

        # Store last sizes for restoration
        self.last_sizes = None

        # For compatibility with old code
        self.left_view = None
        self.right_view = None

    def get_splitter(self):
        """Returns the horizontal splitter widget"""
        return self.splitter

    def add_left_view(self, view):
        """Add view to the left side of the horizontal splitter"""
        self.splitter.addWidget(view)
        self.left_view = view

    def add_right_view(self, view):
        """Add view to the right side of the horizontal splitter and save initial sizes"""
        self.splitter.addWidget(view)
        self.right_view = view
        self.last_sizes = self.splitter.sizes()

    def save_sizes(self):
        """Save current sizes of the splitter"""
        self.last_sizes = self.splitter.sizes()
        return self.last_sizes

    def get_sizes(self):
        """Get current sizes of the splitter"""
        return self.splitter.sizes()

    def set_sizes(self, sizes):
        """Set sizes of the splitter"""
        self.splitter.setSizes(sizes)

    def restore_saved_sizes(self):
        """Restore previously saved sizes"""
        if self.last_sizes:
            self.splitter.setSizes(self.last_sizes)

    def handle_view_visibility(self, view_name, is_visible, views):
        """Respond to view visibility changes and adjust layout"""
        # Skip if no last sizes available
        if not self.last_sizes:
            return

        # Save current sizes before hiding
        if not is_visible and views["left"]["visible"] and views["right"]["visible"]:
            self.last_sizes = self.splitter.sizes()

        # Get the indices of the views in the splitter
        left_idx = self.splitter.indexOf(views["left"]["view"])
        right_idx = self.splitter.indexOf(views["right"]["view"])

        # If hiding one view, give all space to the other view
        if not is_visible:
            # When hiding left view
            if view_name == "left" and views["right"]["visible"]:
                total_width = sum(self.splitter.sizes())
                new_sizes = [0] * self.splitter.count()
                new_sizes[right_idx] = total_width
                self.splitter.setSizes(new_sizes)

            # When hiding right view
            elif view_name == "right" and views["left"]["visible"]:
                total_width = sum(self.splitter.sizes())
                new_sizes = [0] * self.splitter.count()
                new_sizes[left_idx] = total_width
                self.splitter.setSizes(new_sizes)

        # If unhiding a view and both are now visible, restore original proportions
        elif is_visible and views["left"]["visible"] and views["right"]["visible"]:
            self.restore_saved_sizes()

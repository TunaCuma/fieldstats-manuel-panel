from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from .styles import Styles


class VerticalSplitterManager:
    """Manages vertical splitting for top and bottom views."""

    def __init__(self):
        # Create main vertical splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setContentsMargins(0, 0, 0, 0)

        # Apply styling
        self.splitter.setStyleSheet(Styles.SPLITTER_STYLE)
        self.splitter.setHandleWidth(8)  # Thicker handle for better visibility

        # Top container for horizontal splitter
        self.top_container = QWidget()
        self.top_layout = QVBoxLayout(self.top_container)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)

        # Bottom container for transformed view
        self.bottom_container = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_container)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(0)

        # Add containers to splitter
        self.splitter.addWidget(self.top_container)
        self.splitter.addWidget(self.bottom_container)

        # Set initial sizes and save them
        self.splitter.setSizes([300, 300])
        self.last_sizes = [300, 300]

    def get_splitter(self):
        """Returns the vertical splitter widget."""
        return self.splitter

    def get_top_layout(self):
        """Returns the top layout for adding widgets."""
        return self.top_layout

    def get_bottom_layout(self):
        """Returns the bottom layout for adding widgets."""
        return self.bottom_layout

    def add_to_top(self, widget):
        """Add widget to the top container."""
        self.top_layout.addWidget(widget)

    def add_to_bottom(self, widget):
        """Add widget to the bottom container."""
        self.bottom_layout.addWidget(widget)

    def save_sizes(self):
        """Save current sizes of the splitter."""
        self.last_sizes = self.splitter.sizes()
        return self.last_sizes

    def get_sizes(self):
        """Get current sizes of the splitter."""
        return self.splitter.sizes()

    def set_sizes(self, sizes):
        """Set sizes of the splitter."""
        self.splitter.setSizes(sizes)

    def restore_saved_sizes(self):
        """Restore previously saved sizes."""
        if self.last_sizes:
            self.splitter.setSizes(self.last_sizes)

    def handle_view_visibility(self, view_name, is_visible, views):
        """Respond to view visibility changes and adjust vertical layout."""
        # Get the indices of the containers in the splitter
        top_idx = self.splitter.indexOf(self.top_container)
        bottom_idx = self.splitter.indexOf(self.bottom_container)

        # Save current sizes before hiding
        if (
            view_name in ["left", "right"]
            and all(not views[v]["visible"] for v in ["left", "right"])
        ) or (view_name == "transform" and not is_visible):
            self.last_sizes = self.splitter.sizes()

        # If both top views are hidden, give all space to bottom
        if (
            all(not views[v]["visible"] for v in ["left", "right"])
            and views["transform"]["visible"]
        ):
            total_height = sum(self.splitter.sizes())
            new_sizes = [0] * self.splitter.count()
            new_sizes[top_idx] = 30  # Just enough for the splitter handle
            new_sizes[bottom_idx] = total_height - 30
            self.splitter.setSizes(new_sizes)

        # If bottom view is hidden, give all space to top
        elif not views["transform"]["visible"] and any(
            views[v]["visible"] for v in ["left", "right"]
        ):
            total_height = sum(self.splitter.sizes())
            new_sizes = [0] * self.splitter.count()
            new_sizes[top_idx] = total_height - 30
            new_sizes[bottom_idx] = 30  # Just enough for the splitter handle
            self.splitter.setSizes(new_sizes)

        # If everything is visible again, restore original proportions
        elif (
            any(views[v]["visible"] for v in ["left", "right"])
            and views["transform"]["visible"]
        ):
            self.restore_saved_sizes()

from .horizontal_splitter import HorizontalSplitterManager
from .layout_preset_manager import LayoutPresetManager
from .styles import Styles
from .vertical_splitter import VerticalSplitterManager


class SplitterManager:
    """
    Main manager class that coordinates the horizontal and vertical splitters
    and handles view visibility and detachment.
    """

    def __init__(self):
        # Create the vertical splitter manager
        self.vertical_manager = VerticalSplitterManager()

        # Create the horizontal splitter manager
        self.horizontal_manager = HorizontalSplitterManager()

        # Add the horizontal splitter to the top container of the vertical
        # splitter
        self.vertical_manager.add_to_top(self.horizontal_manager.get_splitter())

        # Create the layout preset manager
        self.layout_manager = LayoutPresetManager(
            self.vertical_manager, self.horizontal_manager
        )

        # Create properties for backwards compatibility
        self.main_splitter = self.vertical_manager.get_splitter()
        self.horizontal_splitter = self.horizontal_manager.get_splitter()

        # Add direct references to containers for compatibility
        self.top_container = self.vertical_manager.top_container
        self.bottom_container = self.vertical_manager.bottom_container
        self.top_layout = self.vertical_manager.top_layout
        self.bottom_layout = self.vertical_manager.bottom_layout

        # Add compatibility for size tracking
        self.last_horizontal_sizes = self.horizontal_manager.last_sizes
        self.last_vertical_sizes = self.vertical_manager.last_sizes

        # Add splitter style for compatibility
        self.splitter_style = Styles.SPLITTER_STYLE

    def get_main_splitter(self):
        """Returns the main (vertical) splitter widget for adding to layouts"""
        return self.vertical_manager.get_splitter()

    def add_left_view(self, view):
        """Add view to the left side of the horizontal splitter"""
        self.horizontal_manager.add_left_view(view)

    def add_right_view(self, view):
        """Add view to the right side of the horizontal splitter"""
        self.horizontal_manager.add_right_view(view)

    def add_transform_view(self, view):
        """Add view to the bottom container"""
        self.vertical_manager.add_to_bottom(view)

    def handle_view_detach(self, view_name, views):
        """Handle when a view is detached to separate window"""
        # Handle horizontal splitter adjustments (left and right views)
        if view_name in ["left", "right"]:
            # Save current sizes before detaching if both views are visible
            if views["left"]["visible"] and views["right"]["visible"]:
                self.horizontal_manager.save_sizes()
                # Update the compatibility property
                self.last_horizontal_sizes = self.horizontal_manager.last_sizes

            # Get the current view dictionary and delegate to horizontal
            # manager
            self.horizontal_manager.handle_view_visibility(view_name, False, views)

        # Handle vertical splitter for transform view
        elif view_name == "transform":
            # Save current sizes
            self.vertical_manager.save_sizes()
            # Update the compatibility property
            self.last_vertical_sizes = self.vertical_manager.last_sizes

            # Update views dictionary to mark transform as not visible
            views_copy = views.copy()
            views_copy["transform"]["visible"] = False

            # Delegate to vertical manager
            self.vertical_manager.handle_view_visibility(view_name, False, views_copy)

    def handle_view_reattach(self, view_name, views):
        """Handle when a view is reattached from separate window"""
        # Update views dictionary
        views_copy = views.copy()
        views_copy[view_name]["visible"] = True

        # Restore the appropriate splitter
        if view_name in ["left", "right"]:
            self.horizontal_manager.handle_view_visibility(view_name, True, views_copy)
            # Update the compatibility property
            self.last_horizontal_sizes = self.horizontal_manager.last_sizes
        elif view_name == "transform":
            self.vertical_manager.handle_view_visibility(view_name, True, views_copy)
            # Update the compatibility property
            self.last_vertical_sizes = self.vertical_manager.last_sizes

    def handle_view_visibility(self, view_name, is_visible, views):
        """Respond to view visibility changes and adjust layout"""
        # For horizontal views, delegate to horizontal manager
        if view_name in ["left", "right"]:
            self.horizontal_manager.handle_view_visibility(view_name, is_visible, views)
            # Update the compatibility property
            self.last_horizontal_sizes = self.horizontal_manager.last_sizes

        # Always update vertical manager for any visibility change
        self.vertical_manager.handle_view_visibility(view_name, is_visible, views)
        # Update the compatibility property
        self.last_vertical_sizes = self.vertical_manager.last_sizes

    def apply_layout_preset(self, preset):
        """Apply a layout preset"""
        self.layout_manager.apply_preset(preset)
        # Update the compatibility properties
        self.last_horizontal_sizes = self.horizontal_manager.last_sizes
        self.last_vertical_sizes = self.vertical_manager.last_sizes

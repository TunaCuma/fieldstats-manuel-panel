class ViewTracker:
    """Tracks the visibility and state of views"""

    def __init__(self):
        # Track view visibility status
        self.views = {
            "left": {"view": None, "visible": True, "container": None},
            "right": {"view": None, "visible": True, "container": None},
            "transform": {"view": None, "visible": True, "container": None},
        }

    def register_view(self, view_name, view, container):
        """Register a view for tracking"""
        self.views[view_name]["view"] = view
        self.views[view_name]["container"] = container

    def update_visibility(self, view_name, is_visible):
        """Update the visibility state of a view"""
        self.views[view_name]["visible"] = is_visible

    def is_view_visible(self, view_name):
        """Check if a view is visible"""
        return self.views[view_name]["visible"]

    def get_view(self, view_name):
        """Get a view by name"""
        return self.views[view_name]["view"]

    def get_all_views(self):
        """Get all views"""
        return {name: info["view"] for name, info in self.views.items()}

    def get_visible_views(self):
        """Get all visible views"""
        return {
            name: info["view"] for name, info in self.views.items() if info["visible"]
        }

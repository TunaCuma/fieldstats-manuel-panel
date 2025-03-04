from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu


def create_video_view_context_menu(video_view):
    """Create context menu for video view."""
    context_menu = QMenu(video_view)

    # Add actions
    detach_action = QAction("Detach to window", video_view)
    detach_action.triggered.connect(video_view.detach_view)
    context_menu.addAction(detach_action)

    # Change text based on current visibility
    visibility_text = "Show panel" if not video_view.is_visible else "Hide panel"
    hide_action = QAction(visibility_text, video_view)
    hide_action.triggered.connect(video_view.toggle_visibility)
    context_menu.addAction(hide_action)

    return context_menu

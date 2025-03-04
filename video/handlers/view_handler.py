from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
)


class ViewHandler:
    """Handles view-related functionality"""

    def __init__(
        self,
        left_view,
        right_view,
        transform_view,
        left_player,
        right_player,
        main_player,
        status_bar,
        view_resized_signal,
    ):
        self.left_view = left_view
        self.right_view = right_view
        self.transform_view = transform_view
        self.left_player = left_player
        self.right_player = right_player
        self.main_player = main_player
        self.status_bar = status_bar
        self.view_resized_signal = view_resized_signal

        # Visibility flags
        self.is_left_visible = True
        self.is_right_visible = True
        self.is_transform_visible = True

    def handle_view_resized(self):
        """Handle view resize events"""
        # Update all views' video sizes
        self.left_view.update_video_size()
        self.right_view.update_video_size()
        self.transform_view.update_video_size()

        # Emit signal for overlay adjustments
        self.view_resized_signal.emit()

    def handle_left_detach(self):
        """Handle left view detach request"""
        if self.left_view.detached_window:
            self.left_view.set_detached_video_output(self.left_player)
            self.status_bar.showMessage(
                "Left field view detached to separate window")

    def handle_right_detach(self):
        """Handle right view detach request"""
        if self.right_view.detached_window:
            self.right_view.set_detached_video_output(self.right_player)
            self.status_bar.showMessage(
                "Right field view detached to separate window")

    def handle_transform_detach(self):
        """Handle transform view detach request"""
        if self.transform_view.detached_window:
            self.transform_view.set_detached_video_output(self.main_player)
            self.status_bar.showMessage(
                "Transform view detached to separate window")

    def handle_left_reattach(self):
        """Handle left view reattach request"""
        self.left_player.setVideoOutput(self.left_view.video_item)
        self.status_bar.showMessage("Left field view reattached")

    def handle_right_reattach(self):
        """Handle right view reattach request"""
        self.right_player.setVideoOutput(self.right_view.video_item)
        self.status_bar.showMessage("Right field view reattached")

    def handle_transform_reattach(self):
        """Handle transform view reattach request"""
        self.main_player.setVideoOutput(self.transform_view.video_item)
        self.status_bar.showMessage("Transform view reattached")

    def handle_left_visibility(self, is_visible):
        """Handle left view visibility changes"""
        self.is_left_visible = is_visible

    def handle_right_visibility(self, is_visible):
        """Handle right view visibility changes"""
        self.is_right_visible = is_visible

    def handle_transform_visibility(self, is_visible):
        """Handle transform view visibility changes"""
        self.is_transform_visible = is_visible

    def toggle_left_field(self):
        """Toggle left field view visibility"""
        self.left_view.toggle_visibility()

    def toggle_right_field(self):
        """Toggle right field view visibility"""
        self.right_view.toggle_visibility()

    def toggle_transform_view(self):
        """Toggle transform view visibility"""
        self.transform_view.toggle_visibility()

    def show_all_views(self):
        """Show all views that might be hidden"""
        if not self.is_left_visible:
            self.left_view.toggle_visibility()

        if not self.is_right_visible:
            self.right_view.toggle_visibility()

        if not self.is_transform_visible:
            self.transform_view.toggle_visibility()

    def show_view_control_dialog(self, parent=None):
        """Show a dialog to control visibility of all views"""
        dialog = QDialog(parent)
        dialog.setWindowTitle("Manage Views")
        layout = QVBoxLayout(dialog)

        # Title
        title_label = QLabel("Show/Hide Video Panels")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Left field checkbox
        left_check = QCheckBox("Left Field View")
        left_check.setChecked(self.is_left_visible)
        layout.addWidget(left_check)

        # Right field checkbox
        right_check = QCheckBox("Right Field View")
        right_check.setChecked(self.is_right_visible)
        layout.addWidget(right_check)

        # Transform checkbox
        transform_check = QCheckBox("Transform View")
        transform_check.setChecked(self.is_transform_visible)
        layout.addWidget(transform_check)

        # Buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")

        apply_button.clicked.connect(
            lambda: self.apply_view_visibility(
                left_check.isChecked(),
                right_check.isChecked(),
                transform_check.isChecked(),
            )
            or dialog.accept()
        )

        cancel_button.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        dialog.exec()

    def apply_view_visibility(
            self,
            left_visible,
            right_visible,
            transform_visible):
        """Apply visibility settings to all views"""
        # Only toggle if the state is different
        if self.is_left_visible != left_visible:
            self.toggle_left_field()

        if self.is_right_visible != right_visible:
            self.toggle_right_field()

        if self.is_transform_visible != transform_visible:
            self.toggle_transform_view()

        # Update the layout after changes
        self.handle_view_resized()

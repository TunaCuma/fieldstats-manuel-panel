from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QGraphicsTextItem

from tracking.app import update_data


class TrackingOverlayManager:
    """Manages overlays for displaying player tracking IDs."""

    def __init__(self, player, json_overlay_manager):
        self.player = player
        self.json_manager = json_overlay_manager

        # Overlay containers for IDs
        self.topdown_id_overlays = []
        self.left_id_overlays = []
        self.right_id_overlays = []

        # Tracking data
        self.tracking_data = {}
        self.current_tracking_frame = None

        # Connect signals
        self.player.media_player.positionChanged.connect(self.update_id_overlays)
        self.player.viewResized.connect(self.update_id_overlays)

    def initialize_with_ids(self, num_ids=23):
        """Initialize tracking with IDs from 1 to num_ids."""
        initial_coords = []

        # Get current frame objects from the JSON manager
        current_frame = self.player.current_frame
        frame_objects = self.json_manager.frame_data.get(current_frame, [])

        # Assign initial IDs to objects
        for i, obj in enumerate(frame_objects):
            if i < num_ids:
                obj_id = i + 1  # IDs from 1 to num_ids
                initial_coords.append(
                    {
                        "id": obj_id,
                        "c": obj.get("t_c", obj.get("c", [0, 0])),
                        "src": obj.get("src", 0),
                    }
                )

        # Call update_data with initial coordinates
        if initial_coords:
            response = update_data(
                {"frame_id": current_frame, "coords": initial_coords}
            )

            # Store the tracking data
            if "tracks" in response:
                self.tracking_data = response["tracks"]

            # Navigate to lost_frame_id if provided
            if "lost_frame_id" in response and response["lost_frame_id"]:
                self.player.controls.frame_input.setText(str(response["lost_frame_id"]))
                self.player.controls.go_to_frame()

            return response
        return {"error": "No objects found in current frame"}

    def create_id_overlays(self, scene, max_overlays=30):
        """Create text overlays for displaying IDs."""
        overlays = []

        for _ in range(max_overlays):
            text_item = QGraphicsTextItem()
            text_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            text_item.setDefaultTextColor(QColor(255, 0, 0))  # Red color for IDs
            text_item.setZValue(10)  # Ensure IDs are on top
            text_item.setVisible(False)

            scene.addItem(text_item)
            overlays.append(text_item)

        return overlays

    def setup_overlays(self):
        """Set up ID overlays for all views."""
        # Clear previous overlays
        self.clear_overlays()

        # Create new overlays
        self.topdown_id_overlays = self.create_id_overlays(
            self.player.transform_view.scene
        )
        self.left_id_overlays = self.create_id_overlays(self.player.left_view.scene)
        self.right_id_overlays = self.create_id_overlays(self.player.right_view.scene)

    def clear_overlays(self):
        """Clear all ID overlays."""
        for overlays in [
            self.topdown_id_overlays,
            self.left_id_overlays,
            self.right_id_overlays,
        ]:
            for overlay in overlays:
                if overlay.scene():
                    overlay.scene().removeItem(overlay)
            overlays.clear()

    def update_id_overlays(self, position=None):
        """Update ID overlays based on tracking data."""
        if not self.player.duration:
            return

        # Calculate current frame
        current_frame = self.player.current_frame

        # Find the closest frame in tracking data
        if isinstance(self.tracking_data, list):
            for track in self.tracking_data:
                if track.get("fr") == current_frame:
                    self.update_frame_overlays(track.get("obj", []))
                    break

    def update_frame_overlays(self, objects):
        """Update overlays for the current frame objects."""
        # Update topdown view
        self.update_topdown_id_overlays(objects)

        # Update field views
        left_objects = [obj for obj in objects if obj.get("src") == 0]
        right_objects = [obj for obj in objects if obj.get("src") == 1]

        self.update_left_id_overlays(left_objects)
        self.update_right_id_overlays(right_objects)

    def update_topdown_id_overlays(self, objects):
        """Update ID overlays for the transform view."""
        for idx, overlay in enumerate(self.topdown_id_overlays):
            if idx < len(objects):
                obj = objects[idx]

                # Get the direct video item position
                x_offset = self.player.transform_view.video_item.pos().x()
                y_offset = self.player.transform_view.video_item.pos().y()

                # Add half the video width to objects from right field (src=1)
                x_position = obj.get("c", [0, 0])[0]
                if obj.get("src") == 1:
                    x_position += self.json_manager.topdown_width / 2 - 20

                # Position the text item
                x = x_offset + x_position * self.json_manager.topdown_scale_x
                y = (
                    y_offset
                    + obj.get("c", [0, 0])[1] * self.json_manager.topdown_scale_y
                )

                overlay.setPlainText(str(obj.get("id", "")))
                overlay.setPos(x, y)
                overlay.setVisible(True)
            else:
                overlay.setVisible(False)

    def update_left_id_overlays(self, objects):
        """Update ID overlays for the left field view."""
        if not self.player.is_left_visible:
            for overlay in self.left_id_overlays:
                overlay.setVisible(False)
            return

        for idx, overlay in enumerate(self.left_id_overlays):
            if idx < len(objects):
                obj = objects[idx]

                # Get the direct video item position
                x_offset = self.player.left_view.video_item.pos().x()
                y_offset = self.player.left_view.video_item.pos().y()

                # Get coordinates
                coords = obj.get("c", [0, 0])

                # Position the text item
                x = x_offset + coords[0] * self.json_manager.left_scale_x
                y = y_offset + coords[1] * self.json_manager.left_scale_y

                overlay.setPlainText(str(obj.get("id", "")))
                overlay.setPos(x, y)
                overlay.setVisible(True)
            else:
                overlay.setVisible(False)

    def update_right_id_overlays(self, objects):
        """Update ID overlays for the right field view."""
        if not self.player.is_right_visible:
            for overlay in self.right_id_overlays:
                overlay.setVisible(False)
            return

        for idx, overlay in enumerate(self.right_id_overlays):
            if idx < len(objects):
                obj = objects[idx]

                # Get the direct video item position
                x_offset = self.player.right_view.video_item.pos().x()
                y_offset = self.player.right_view.video_item.pos().y()

                # Get coordinates
                coords = obj.get("c", [0, 0])

                # Position the text item
                x = x_offset + coords[0] * self.json_manager.right_scale_x
                y = y_offset + coords[1] * self.json_manager.right_scale_y

                overlay.setPlainText(str(obj.get("id", "")))
                overlay.setPos(x, y)
                overlay.setVisible(True)
            else:
                overlay.setVisible(False)

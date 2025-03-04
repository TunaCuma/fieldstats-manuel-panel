import json

from .detached_overlay_manager import DetachedOverlayManager
from .overlay_creator import OverlayCreator
from .overlay_updater import OverlayUpdater


class JSONOverlayManager:
    def __init__(self, player, json_path):
        self.player = player

        # Overlay containers
        self.topdown_overlays = []  # For transformed view (bottom)
        self.left_overlays = []  # For left field view
        self.right_overlays = []  # For right field view
        self.detached_topdown_overlays = []  # For detached transformed view
        self.detached_left_overlays = []  # For detached left field view
        self.detached_right_overlays = []  # For detached right field view

        # Frame data
        self.frame_data = {}

        # Default dimensions - will be updated from metadata if available
        self.topdown_width = 752
        self.topdown_height = 300
        self.field_width = 1920
        self.field_height = 1080

        # Scale factors for each view
        self.topdown_scale_x = 1.0
        self.topdown_scale_y = 1.0
        self.left_scale_x = 1.0
        self.left_scale_y = 1.0
        self.right_scale_x = 1.0
        self.right_scale_y = 1.0

        # Create helper classes
        self.overlay_creator = OverlayCreator(self)
        self.overlay_updater = OverlayUpdater(self)
        self.detached_manager = DetachedOverlayManager(self)

        # Initialize
        self.load_json_data(json_path)
        self.overlay_creator.create_overlays()
        self.connect_signals()

    def load_json_data(self, json_path):
        with open(json_path) as f:
            data = json.load(f)

        # Store video dimensions from metadata if available
        if "metadata" in data:
            metadata = data["metadata"]
            if "width" in metadata and "height" in metadata:
                self.topdown_width = metadata.get("width", self.topdown_width)
                self.topdown_height = metadata.get("height", self.topdown_height)
            if "field_width" in metadata and "field_height" in metadata:
                self.field_width = metadata.get("field_width", self.field_width)
                self.field_height = metadata.get("field_height", self.field_height)

        # Convert frames list to dictionary for faster lookup
        self.frame_data = {frame["fr"]: frame["obj"] for frame in data["frames"]}

    def connect_signals(self):
        self.player.viewResized.connect(self.update_view_sizes)
        self.player.media_player.positionChanged.connect(self.update_overlays)
        self.player.viewResized.connect(self.update_all_overlays)

        # Connect signals for detached windows
        self.player.left_view.detachRequested.connect(
            self.detached_manager.create_detached_left_overlays
        )
        self.player.right_view.detachRequested.connect(
            self.detached_manager.create_detached_right_overlays
        )
        self.player.transform_view.detachRequested.connect(
            self.detached_manager.create_detached_transform_overlays
        )

        # Connect signals for reattaching
        self.player.left_view.reattachRequested.connect(
            self.detached_manager.clean_detached_left_overlays
        )
        self.player.right_view.reattachRequested.connect(
            self.detached_manager.clean_detached_right_overlays
        )
        self.player.transform_view.reattachRequested.connect(
            self.detached_manager.clean_detached_transform_overlays
        )

    def update_view_sizes(self):
        """Update scaling factors based on the actual video display area."""
        # For transformed view - use actual_video_rect if available
        if hasattr(self.player.transform_view, "actual_video_rect"):
            rect = self.player.transform_view.actual_video_rect
            self.topdown_view_width = rect["width"]
            self.topdown_view_height = rect["height"]
            # Store offset for positioning overlays correctly
            self.topdown_offset_x = rect["x"]
            self.topdown_offset_y = rect["y"]
        else:
            # Fallback to video item size
            if self.player.transform_view.video_item.size().width() > 0:
                self.topdown_view_width = (
                    self.player.transform_view.video_item.size().width()
                )
                self.topdown_view_height = (
                    self.player.transform_view.video_item.size().height()
                )
            else:
                self.topdown_view_width = self.player.transform_view.view.width()
                self.topdown_view_height = self.player.transform_view.view.height()
            self.topdown_offset_x = 0
            self.topdown_offset_y = 0

        # For left field view
        if hasattr(self.player.left_view, "actual_video_rect"):
            rect = self.player.left_view.actual_video_rect
            self.left_view_width = rect["width"]
            self.left_view_height = rect["height"]
            self.left_offset_x = rect["x"]
            self.left_offset_y = rect["y"]
        else:
            if self.player.left_view.video_item.size().width() > 0:
                self.left_view_width = self.player.left_view.video_item.size().width()
                self.left_view_height = self.player.left_view.video_item.size().height()
            else:
                self.left_view_width = self.player.left_view.view.width()
                self.left_view_height = self.player.left_view.view.height()
            self.left_offset_x = 0
            self.left_offset_y = 0

        # For right field view
        if hasattr(self.player.right_view, "actual_video_rect"):
            rect = self.player.right_view.actual_video_rect
            self.right_view_width = rect["width"]
            self.right_view_height = rect["height"]
            self.right_offset_x = rect["x"]
            self.right_offset_y = rect["y"]
        else:
            if self.player.right_view.video_item.size().width() > 0:
                self.right_view_width = self.player.right_view.video_item.size().width()
                self.right_view_height = (
                    self.player.right_view.video_item.size().height()
                )
            else:
                self.right_view_width = self.player.right_view.view.width()
                self.right_view_height = self.player.right_view.view.height()
            self.right_offset_x = 0
            self.right_offset_y = 0

        # Calculate scale factors
        self.topdown_scale_x = self.topdown_view_width / self.topdown_width
        self.topdown_scale_y = self.topdown_view_height / self.topdown_height
        self.left_scale_x = self.left_view_width / self.field_width
        self.left_scale_y = self.left_view_height / self.field_height
        self.right_scale_x = self.right_view_width / self.field_width
        self.right_scale_y = self.right_view_height / self.field_height

    def update_all_overlays(self):
        self.update_overlays(self.player.media_player.position())

    def update_overlays(self, position):
        if not self.player.duration:
            return

        # Calculate current frame
        current_frame = self.player.current_frame

        # Get objects for current frame
        frame_objects = self.frame_data.get(current_frame, [])

        # Lists to store objects by source
        transformed_objects = []  # For topdown view
        left_objects = []  # For left field (src=0)
        right_objects = []  # For right field (src=1)

        # Separate objects by source
        for obj in frame_objects:
            # Add to transformed view (all objects)
            transformed_objects.append(obj)

            # Add to appropriate field view based on src
            if obj["src"] == 0:
                left_objects.append(obj)
            elif obj["src"] == 1:
                right_objects.append(obj)

        # Update main view overlays
        self.overlay_updater.update_topdown_overlays(transformed_objects)
        self.overlay_updater.update_left_overlays(left_objects)
        self.overlay_updater.update_right_overlays(right_objects)

        # Update detached window overlays if they exist
        if (
            self.player.transform_view.detached_window
            and self.detached_topdown_overlays
        ):
            self.overlay_updater.update_detached_topdown_overlays(transformed_objects)

        if self.player.left_view.detached_window and self.detached_left_overlays:
            self.overlay_updater.update_detached_left_overlays(left_objects)

        if self.player.right_view.detached_window and self.detached_right_overlays:
            self.overlay_updater.update_detached_right_overlays(right_objects)

    def show_object_info(self, obj_info):
        """Display information about the clicked object."""
        source = "Left Field" if obj_info["src"] == 0 else "Right Field"
        # Display adjusted position for right field objects in topdown view
        x_position = obj_info["t_c"][0]
        if obj_info["src"] == 1:
            x_position += (
                self.topdown_width / 2 - 20
            )  # Apply the same 20 pixel adjustment
        info_text = (
            f"Source: {source}, Position: ({x_position:.1f}, {obj_info['t_c'][1]:.1f})"
        )
        self.player.click_info_label.setText(info_text)

"""VideoPlayer signal connector module to handle connecting signals between
components."""


class VideoPlayerSignalConnector:
    """Handles signal connections between different VideoPlayer components.

    Centralizes all signal connection logic.
    """

    def __init__(self, parent):
        """Initialize the signal connector with a reference to the parent
        object."""
        self.parent = parent

    def connect_all_signals(self):
        """Connect all signals between components."""
        self._connect_layout_signals()
        self._connect_control_signals()
        self._connect_view_signals()
        self._connect_media_signals()
        self.parent.controls.initTrackingClicked.connect(self.init_tracking)

    def init_tracking(self):
        """Initialize tracking with IDs from 1 to 23."""
        # Check if JSON overlay manager is available
        if hasattr(self, "json_overlay_manager") and self.json_overlay_manager:
            if hasattr(self.json_overlay_manager, "tracking_manager"):
                # Set up tracking overlays
                self.json_overlay_manager.tracking_manager.setup_overlays()

                # Initialize with IDs
                response = (
                    self.json_overlay_manager.tracking_manager.initialize_with_ids(23)
                )

                # Show result in status bar
                if "error" in response:
                    self.parent.statusBar.showMessage(
                        f"Tracking error: {response['error']}"
                    )
                else:
                    lost_frame = response.get("lost_frame_id")
                    if lost_frame:
                        self.parent.statusBar.showMessage(
                            f"Tracking initialized. Lost frame found at: {lost_frame}"
                        )
                    else:
                        self.parent.statusBar.showMessage(
                            "Tracking initialized successfully"
                        )
            else:
                self.parent.statusBar.showMessage("Tracking manager not available")
        else:
            self.parent.statusBar.showMessage("JSON overlay manager not available")

    def _connect_layout_signals(self):
        """Connect layout-related signals."""
        # Connect layout manager signals
        self.parent.layout_manager.viewResized.connect(
            self.parent.view_handler.handle_view_resized
        )

    def _connect_control_signals(self):
        """Connect control-related signals."""
        # Connect control signals to playback controller
        self.parent.controls.playPauseClicked.connect(
            self.parent.playback_controller.play_pause
        )
        self.parent.controls.stopClicked.connect(self.parent.playback_controller.stop)
        self.parent.controls.prevFrameClicked.connect(
            self.parent.playback_controller.previous_frame
        )
        self.parent.controls.nextFrameClicked.connect(
            self.parent.playback_controller.next_frame
        )
        self.parent.controls.sliderMoved.connect(
            self.parent.playback_controller.set_position
        )
        self.parent.controls.goToFrameRequested.connect(
            self.parent.playback_controller.go_to_frame
        )

    def _connect_view_signals(self):
        """Connect view-related signals."""
        # Connect view toggle signals from menu
        self.parent.menu_handler.toggleLeftAction.triggered.connect(
            self.parent.view_handler.toggle_left_field
        )
        self.parent.menu_handler.toggleRightAction.triggered.connect(
            self.parent.view_handler.toggle_right_field
        )
        self.parent.menu_handler.toggleTransformAction.triggered.connect(
            self.parent.view_handler.toggle_transform_view
        )
        self.parent.menu_handler.showAllViewsAction.triggered.connect(
            self.parent.view_handler.show_all_views
        )
        self.parent.menu_handler.manageViewsAction.triggered.connect(
            self.parent.view_handler.show_view_control_dialog
        )

        # Connect detach/reattach signals
        self.parent.left_view.detachRequested.connect(
            self.parent.view_handler.handle_left_detach
        )
        self.parent.right_view.detachRequested.connect(
            self.parent.view_handler.handle_right_detach
        )
        self.parent.transform_view.detachRequested.connect(
            self.parent.view_handler.handle_transform_detach
        )

        self.parent.left_view.reattachRequested.connect(
            self.parent.view_handler.handle_left_reattach
        )
        self.parent.right_view.reattachRequested.connect(
            self.parent.view_handler.handle_right_reattach
        )
        self.parent.transform_view.reattachRequested.connect(
            self.parent.view_handler.handle_transform_reattach
        )

        # Connect visibility signals
        self.parent.left_view.toggledVisibility.connect(
            self.parent.view_handler.handle_left_visibility
        )
        self.parent.right_view.toggledVisibility.connect(
            self.parent.view_handler.handle_right_visibility
        )
        self.parent.transform_view.toggledVisibility.connect(
            self.parent.view_handler.handle_transform_visibility
        )

    def _connect_media_signals(self):
        """Connect media-related signals."""
        # Connect resize signals
        self.parent.left_view.videoResized.connect(
            self.parent.view_handler.handle_view_resized
        )
        self.parent.right_view.videoResized.connect(
            self.parent.view_handler.handle_view_resized
        )
        self.parent.transform_view.videoResized.connect(
            self.parent.view_handler.handle_view_resized
        )

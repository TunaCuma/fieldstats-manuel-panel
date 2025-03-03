from PyQt6.QtWidgets import QMenu


class LayoutMenu:
    """Handles the layout menu functionality"""
    
    def __init__(self, menu_button, view_tracker, splitter_manager):
        self.menu_button = menu_button
        self.view_tracker = view_tracker
        self.splitter_manager = splitter_manager
        
        # Connect the menu button click to show the menu
        self.menu_button.clicked.connect(self.show_layout_menu)
    
    def show_layout_menu(self):
        """Show layout customization menu with view toggle options"""
        menu = QMenu(self.menu_button)
        menu.setStyleSheet("""
            QMenu {
                background-color: #353535;
                color: #ffffff;
                border: 1px solid #424242;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #2a82da;
            }
            QMenu::separator {
                height: 1px;
                background-color: #424242;
                margin: 5px 0px 5px 0px;
            }
        """)
        
        # Add layout presets
        split_equal_action = menu.addAction("Equal Split")
        split_equal_action.triggered.connect(
            lambda: self.apply_layout_preset("equal")
        )
        
        top_focus_action = menu.addAction("Focus on Fields")
        top_focus_action.triggered.connect(
            lambda: self.apply_layout_preset("top")
        )
        
        bottom_focus_action = menu.addAction("Focus on Transform")
        bottom_focus_action.triggered.connect(
            lambda: self.apply_layout_preset("bottom")
        )
        
        # Visibility options
        menu.addSeparator()
        menu.addAction("Show/Hide Views:").setEnabled(False)  # Section title
        
        # Add toggles for each view
        left_action = menu.addAction("Left Field")
        left_action.setCheckable(True)
        left_action.setChecked(self.view_tracker.is_view_visible('left'))
        left_action.triggered.connect(
            lambda checked: self.toggle_view_visibility('left', checked)
        )
        
        right_action = menu.addAction("Right Field")
        right_action.setCheckable(True)
        right_action.setChecked(self.view_tracker.is_view_visible('right'))
        right_action.triggered.connect(
            lambda checked: self.toggle_view_visibility('right', checked)
        )
        
        transform_action = menu.addAction("Transformed View")
        transform_action.setCheckable(True)
        transform_action.setChecked(self.view_tracker.is_view_visible('transform'))
        transform_action.triggered.connect(
            lambda checked: self.toggle_view_visibility('transform', checked)
        )
        
        # Show the menu below the button
        menu.exec(self.menu_button.mapToGlobal(
            self.menu_button.rect().bottomLeft()
        ))
    
    def toggle_view_visibility(self, view_name, should_be_visible):
        """Toggle visibility of a specific view from the menu"""
        view = self.view_tracker.get_view(view_name)
        
        # Only act if the visibility state is changing
        if view and view.is_visible != should_be_visible:
            view.toggle_visibility()
    
    def apply_layout_preset(self, preset):
        """Apply a layout preset"""
        # Make sure views are shown if they were hidden
        for view_name in ['left', 'right', 'transform']:
            view = self.view_tracker.get_view(view_name)
            if not self.view_tracker.is_view_visible(view_name):
                # Show the view
                view.set_visible(True)  # This will call toggle_visibility if needed
        
        # Apply the preset to the splitter manager
        self.splitter_manager.apply_layout_preset(preset)

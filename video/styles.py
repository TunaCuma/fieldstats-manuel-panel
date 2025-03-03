class Styles:
    """Contains style definitions used across the application"""
    
    # Splitter style
    SPLITTER_STYLE = """
        QSplitter::handle {
            background-color: #353535;
            border: 1px solid #424242;
        }
        QSplitter::handle:hover {
            background-color: #454545;
            border: 1px solid #555555;
        }
        QSplitter::handle:pressed {
            background-color: #505050;
        }
    """
    
    # Button style
    BUTTON_STYLE = """
        QPushButton {
            background-color: #353535;
            color: #ffffff;
            border: 1px solid #424242;
            padding: 4px 8px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #424242;
        }
        QPushButton:pressed {
            background-color: #2a82da;
        }
    """
    
    # Menu style
    MENU_STYLE = """
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
    """
    
    # Title style
    TITLE_STYLE = "font-weight: bold; font-size: 16px; color: #ffffff;"

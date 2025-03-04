from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction


class MenuHandler:
    """Handles menu bar and associated actions"""

    def __init__(self, parent, open_videos_callback, open_project_callback):
        self.parent = parent
        self.open_videos_callback = open_videos_callback
        self.open_project_callback = open_project_callback

        # Create menu bar
        self.menuBar = QMenuBar()
        parent.setMenuBar(self.menuBar)

        # Setup menus
        self._setup_file_menu()
        self._setup_view_menu()

    def _setup_file_menu(self):
        """Set up the File menu"""
        self.fileMenu = QMenu("&File", self.parent)
        self.menuBar.addMenu(self.fileMenu)

        self.openAction = QAction("&Open Videos...", self.parent)
        self.openAction.triggered.connect(self.open_videos_callback)
        self.fileMenu.addAction(self.openAction)

        self.openProjectAction = QAction("&Open Project...", self.parent)
        self.openProjectAction.triggered.connect(self.open_project_callback)
        self.fileMenu.addAction(self.openProjectAction)

        self.fileMenu.addSeparator()

        self.exitAction = QAction("&Exit", self.parent)
        self.exitAction.triggered.connect(self.parent.close)
        self.fileMenu.addAction(self.exitAction)

    def _setup_view_menu(self):
        """Set up the View menu"""
        self.viewMenu = QMenu("&View", self.parent)
        self.menuBar.addMenu(self.viewMenu)

        self.toggleLeftAction = QAction("Toggle &Left Field", self.parent)
        self.viewMenu.addAction(self.toggleLeftAction)

        self.toggleRightAction = QAction("Toggle &Right Field", self.parent)
        self.viewMenu.addAction(self.toggleRightAction)

        self.toggleTransformAction = QAction("Toggle &Transform View", self.parent)
        self.viewMenu.addAction(self.toggleTransformAction)

        # Add view management options
        self.viewMenu.addSeparator()
        self.manageViewsAction = QAction("&Manage Views...", self.parent)
        self.viewMenu.addAction(self.manageViewsAction)

        # Optional shortcut for showing all views
        self.showAllViewsAction = QAction("Show &All Views", self.parent)
        self.viewMenu.addAction(self.showAllViewsAction)

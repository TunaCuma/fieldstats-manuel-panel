from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class VideoHeader(QWidget):
    """Widget for video header with title and control buttons"""
    hideRequested = pyqtSignal()
    detachRequested = pyqtSignal()
    
    def __init__(self, title, color="white"):
        super().__init__()
        self.title = title
        self.color = color
        self.setupUI()
        
    def setupUI(self):
        # Header layout
        self.header_layout = QHBoxLayout(self)
        self.header_layout.setContentsMargins(5, 2, 5, 2)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"font-weight: bold; color: {self.color};")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.header_layout.addWidget(self.title_label)
        
        # Status label (for showing "Hidden" when view is hidden)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.header_layout.addWidget(self.status_label)
        
        # Spacer
        self.header_layout.addStretch()
        
        # Control buttons
        self.pop_out_btn = QPushButton("⇱")  # Unicode for pop-out
        self.pop_out_btn.setToolTip("Detach to new window")
        self.pop_out_btn.setFixedSize(24, 24)
        self.pop_out_btn.clicked.connect(self.detachRequested.emit)
        self.header_layout.addWidget(self.pop_out_btn)
        
        self.hide_btn = QPushButton("−")  # Unicode for minus
        self.hide_btn.setToolTip("Hide panel")
        self.hide_btn.setFixedSize(24, 24)
        self.hide_btn.clicked.connect(self.hideRequested.emit)
        self.header_layout.addWidget(self.hide_btn)
    
    def update_visibility_state(self, is_visible):
        """Update UI elements based on visibility state"""
        if is_visible:
            self.hide_btn.setText("−")  # Unicode for minus
            self.hide_btn.setToolTip("Hide panel")
            self.status_label.setText("")
        else:
            self.hide_btn.setText("＋")  # Unicode for plus
            self.hide_btn.setToolTip("Show panel")
            self.status_label.setText("[Hidden]")
    
    def disable_detach_button(self):
        """Disable detach button when in detached state"""
        self.pop_out_btn.setEnabled(False)
    
    def enable_detach_button(self):
        """Enable detach button when reattached"""
        self.pop_out_btn.setEnabled(True)

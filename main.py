import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QBrush, QColor
from custom_rect_item import CustomRectItem
from jsonoverlay_manager import JSONOverlayManager
from overlay_manager import OverlayManager
from video_player import VideoPlayer

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    
    # Initialize overlay manager with JSON data
    overlay_manager = JSONOverlayManager(
        player,
        "turkmen.json"  # Replace with actual JSON path
    )
    
    player.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
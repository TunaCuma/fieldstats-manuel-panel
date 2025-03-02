import sys
from PyQt6.QtWidgets import QApplication
from jsonoverlay_manager import JSONOverlayManager
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
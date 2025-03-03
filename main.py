import sys
from PyQt6.QtWidgets import QApplication
from jsonoverlay_manager import JSONOverlayManager
from video_player import VideoPlayer
from PyQt6.QtGui import QPalette, QColor

def set_dark_mode(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

def main():
    app = QApplication(sys.argv)
    set_dark_mode(app)
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

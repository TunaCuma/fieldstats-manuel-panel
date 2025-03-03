import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from video_player import VideoPlayer
from jsonoverlay_manager import JSONOverlayManager

def set_dark_mode(app):
    """Apply dark mode styling to the application"""
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

def check_video_files():
    """Check if required video files exist and return their paths"""
    # Hardcoded video filenames
    transform_video = "topdown.webm"
    left_field_video = "field_left.mp4"
    right_field_video = "field_right.mp4"
    json_file = "turkmen.json"
    
    missing_files = []
    
    if not os.path.exists(transform_video):
        missing_files.append(transform_video)
    if not os.path.exists(left_field_video):
        missing_files.append(left_field_video)
    if not os.path.exists(right_field_video):
        missing_files.append(right_field_video)
    if not os.path.exists(json_file):
        missing_files.append(json_file)
    
    return {
        "transform": transform_video,
        "left": left_field_video,
        "right": right_field_video,
        "json": json_file,
        "missing": missing_files
    }

def main():
    app = QApplication(sys.argv)
    set_dark_mode(app)
    
    # Check for required files
    files = check_video_files()
    
    if files["missing"]:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Missing Files")
        msg.setText("The following required files are missing:")
        msg.setInformativeText("\n".join(files["missing"]))
        msg.setDetailedText("Please ensure all required video files and JSON data are in the application directory.")
        msg.exec()
        return 1
    
    # Initialize player and load videos
    player = VideoPlayer()
    player.load_videos(
        transform_path=files["transform"],
        left_path=files["left"],
        right_path=files["right"]
    )
    
    # Initialize overlay manager with JSON data
    overlay_manager = JSONOverlayManager(
        player,
        files["json"]
    )
    
    player.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())

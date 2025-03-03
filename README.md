# Football Analysis Video Player

A specialized video player application built with PyQt6 for analyzing football footage with YOLO detection overlays. This application synchronizes three video views (left field, right field, and top-down transformed view) and displays bounding box overlays from YOLO detection data.

## Features

- Three synchronized video views:
  - Left field camera view (top left)
  - Right field camera view (top right)
  - Transformed top-down view (bottom)
- Frame-accurate navigation with previous/next frame controls
- Interactive overlays that display object information when clicked
- Proper aspect ratio preservation for all video views
- Dark mode UI for better visibility of video content
- JSON-based overlay system for displaying YOLO detection results

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/TunaCuma/fieldstats-manuel-panel.git
   cd fieldstats-manuel-panel
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place your video files in the application directory:

   - `field_left.mp4` - Left camera view
   - `field_right.mp4` - Right camera view
   - `topdown.webm` - Transformed top-down view
   - `turkmen.json` - YOLO detection data file

2. Run the application:

   ```
   python main.py
   ```

3. Use the controls at the bottom to:

   - Play/pause the videos
   - Navigate frame by frame
   - Jump to specific frames
   - Adjust volume

4. Click on colored rectangles to see information about the detected objects

## JSON Format

The application expects a JSON file with the following structure:

```json
{
  "metadata": {
    "width": 752, // Width of the top-down view
    "height": 300, // Height of the top-down view
    "field_width": 1920, // Width of the field views
    "field_height": 1080 // Height of the field views
  },
  "frames": [
    {
      "fr": 0, // Frame number
      "obj": [
        {
          "bbox": [
            // Bounding box coordinates [x1, y1, x2, y2]
            1069.1, 654.9, 1094.5, 713.2
          ],
          "src": 0, // Source: 0 for left field, 1 for right field
          "t_c": [
            // Transformed center coordinates for top-down view
            216.8, 113.5
          ]
        }
        // More objects...
      ]
    }
    // More frames...
  ]
}
```

## Project Structure

- `main.py` - Application entry point
- `video_player.py` - Main video player class
- `jsonoverlay_manager.py` - Manages overlay rectangles
- `custom_rect_item.py` - Interactive rectangle class for overlays

## Future Improvements

- Project file support for saving and loading analysis sessions
- Additional overlay options (player tracking, heatmaps, etc.)
- Export capabilities for annotated video
- Timeline view for easier navigation
- Customizable overlay colors and styles

## License

This project is licensed under the MIT License - see the LICENSE file for details.

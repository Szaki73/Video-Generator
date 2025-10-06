# Video Generator Tool Documentation

This script generates a synchronized video from multiple camera feeds (JPEG images), accounting for frame delays and layout constraints. It overlays frame numbers, arranges camera views into a grid, and outputs a single .mp4 video.

## Usage

in the command line write:
`python video_generator.py -i <input_path> -o <output_path> -f <framerate> -c <camera_order...> -d <camera_delay...>`

## Required Arguments
Flag	                Description
-i, --input_path	    Path to folder containing .jpg images
-o, --output_path	    Destination folder for output video
-f, --framerate	Video   Framerate (integer between 0–120)
-c, --camera_order	    List of camera names (e.g. Dev0 Dev1 Dev2)
-d, --camera_delay	    List of frame delays per camera (e.g. 0 1 0)

## Function Reference

**input_handler()**: Parses and validates command-line arguments.

- Converts camera delays to integers
- Calls input_validation() for correctness
- Returns: `argparse.Namespace`

**input_validation(args)**: Ensures all input parameters are valid.

- Checks path existence
- Validates framerate range
- Ensures camera order and delay lengths match
- Exits with error message if invalid

**sort_images(input_path, camera_order, camera_delay)**: Organizes image files by camera and adjusted frame number.

- Filters .jpg files, and filter not existing or requiered cameras
- Applies delay offset to frame numbers
- Returns: camera_frames: `{camera: {frame_number: image_path}} frame_numbers: set[int]`

**get_video_height_and_video_width(camera_frames, height, width)**: Calculates final video canvas size and layout.

- Max 2 cameras per row
- Returns: `video_height, video_width, num_cameras, cams_per_row, num_rows`

**get_image_height_and_image_width(camera_frames, input_path)**: Reads a sample image to determine frame dimensions.

- Returns: `height, width`
- Exits if sample image is unreadable

**load_and_set_frame(...)**: Loads and annotates a frame for a specific camera.

- Parameters: cam, fn, args, camera_frames, height, width, black_frame, camera_order, camera_delay
- Returns: Annotated image or fallback black frame
- Features: adds semi-transparent overlay, displays corrected frame number

**main()**: Coordinates the full video generation process.

- Steps:
    - Parse input
    - Sort images
    - Calculate layout
    - Load frames in parallel
    - Assemble canvas grid
    - Write frames to video

- Extras:
    - Progress bar
    - Missing camera report


**__main__ block**: Measures runtime and handles unexpected errors.

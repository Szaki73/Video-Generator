# Video Generator
Useful tool to load pictures from a folder and create a video based on multiple cameras. The program fills missing frames with black ones for synchronization.

## Installation:
- You will need Python 3.13 or later.
- Clone this repository, run the following to clone everything: `git clone https://github.com/Szaki73/Video-Generator.git`
- Preferably use a python virtual environment, and install dependencies via pip\
  `pip install -r requirements.txt`

## Usage:

- After successfully installind all dependencies, you can run `python video_generator.py -i <input_path> -o <output_path> -f <framerate> -c <camera_order...>`
- Each image filename must follow the pattern: `DivX_..._fnY.jpg`, where **X** and **Y** are integers representing the camera ID and frame number. **DivX** can be anything but it must match the camera names in **camera_order**. The `...` is representing any other parameters that is in the image name, it is not important but the name attributes must be separated with `_`.
- Framerate is locked between 0 and 120.
- camera_order should be: `Div0 Div1 Div2...` if the image pattern is: `DivX_..._fnY.jpg.`
  Camera_order sets the camera images from top to bottom, left to right.
- Runnig this will load all images, from the **input_path**, add the frame number to the top left corner, create the video, and save it in the **output_path** as *output.mp4*.

## Notes:

- You should be able to run this the same way on Linux or on Windows.

- If you set more or less cameras in the order than there are cameras in the **input_path**, then the non existing cameras will be ignored and shown at the end. Not requested cameras will be ignored in the generation.
- If camera names in **camera_order** do not match the names in the **input_path** then those cameras will be ignored.







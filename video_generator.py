import argparse
import sys
import os
import cv2 as cv
import numpy as np
import math
from concurrent.futures import ThreadPoolExecutor
import time

def input_handler():
    parser = argparse.ArgumentParser(
        description="Video Generator Tool",
        usage="python video_generator.py -i <input_path> -o <output_path> -f <framerate> -c <camera_order...>"
    )

    parser.add_argument("-i", "--input_path", type=str, required=True, help="Input folder path")
    parser.add_argument("-o", "--output_path", type=str, required=True, help="Output folder path")
    parser.add_argument("-f", "--framerate", type=int, required=True, help="Framerate [0-120] (e.g. 30)")
    parser.add_argument("-c", "--camera_order", nargs="+", required=True, help="Camera order (e.g. Dev0 Dev1 Dev2...)")

    if len(sys.argv) < 9 or "-h" in sys.argv:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    input_validation(args)

    return args

def input_validation(args):
    if not os.path.exists(args.input_path):
        print(f"video_generator.py: Input path {args.input_path} does not exist.")
        sys.exit(1)

    if not os.path.exists(args.output_path):
        print(f"video_generator.py: Output path {args.output_path} does not exist.")
        sys.exit(1)
    if not isinstance(args.framerate, int):
        print(f"video_generator.py: Framerate must be an integer: {args.framerate}")
        sys.exit(1)
    if not (0 <= args.framerate <= 120):
        print(f"video_generator.py: Framerate must be between 0 and 120. You provided: {args.framerate}")
        sys.exit(1)
    print("All parameters are valid.")
    print(f"Input Path: {args.input_path}")
    print(f"Output Path: {args.output_path}")
    print(f"Framerate: {args.framerate}")
    print(f"Camera Order: {args.camera_order}\n")

def sort_images(input_path, camera_order):
    image_files = [f for f in os.listdir(input_path) if f.endswith(".jpg")]

    camera_frames = {}
    frame_numbers = set()

    for f in image_files:
        parts = f.split("_")
        cam = parts[0]
        if cam not in camera_order: continue
        fn = int(parts[-1][2:].split(".")[0])
        camera_frames.setdefault(cam, {})[fn] = os.path.join(input_path, f)
        frame_numbers.add(fn)
    if len(camera_frames) == 0:
        print("video_generator.py: No camera were found in the input folder from the Camera order.")
        sys.exit(1)
    return camera_frames, frame_numbers

def get_video_height_and_video_width(camera_frames, height, width):
        num_cameras = len(camera_frames)
        cams_per_row = min(2, num_cameras)
        num_rows = math.ceil(num_cameras / cams_per_row)

        video_width = width * min(cams_per_row, num_cameras)
        video_height = height * num_rows
        return video_height, video_width, num_cameras, cams_per_row, num_rows

def get_image_height_and_image_width(camera_frames, input_path):
    try:
        sample_file = next(iter(next(iter(camera_frames.values())).values()))
        sample_image = cv.imread(os.path.join(input_path, sample_file))
        if sample_image is None:
            raise ValueError("Sample image could not be read.")
        height, width, _ = sample_image.shape
        return height, width
    except Exception as e:
        print(f"video_generator.py: error reading sample image: {e}")
        sys.exit(1)


def load_and_set_frame(cam, fn, args, camera_frames, height, width, black_frame):
    try:
        img_file = camera_frames[cam].get(fn)
        img = cv.imread(img_file) if img_file else black_frame
        if img is None:
            img = black_frame

        overlay = img.copy()
        rect_x, rect_y = 5, 5
        rect_w, rect_h = 250, 50
        alpha = 0.6

        cv.rectangle(overlay, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 0, 0), -1)
        img = cv.addWeighted(overlay, alpha, img, 1 - alpha, 0)

        cv.putText(img, f"Frame: {fn}", (11, 41), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv.LINE_AA)
        cv.putText(img, f"Frame: {fn}", (10, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

        return img
    except Exception as e:
        print(f"video_generator.py: error loading frame {fn} for camera {cam}: {e}")
        return black_frame

def main():
    args = input_handler()
    output_file = os.path.join(args.output_path, "output.mp4")

    camera_frames, frame_numbers = sort_images(args.input_path, args.camera_order)

    height, width = get_image_height_and_image_width(camera_frames, args.input_path)

    black_frame =  np.zeros((height, width, 3), dtype=np.uint8)

    video_height, video_width, num_cameras, cams_per_row, num_rows = get_video_height_and_video_width(camera_frames, height, width)

    try:
        fourcc = cv.VideoWriter_fourcc(*"mp4v")
        video = cv.VideoWriter(output_file, fourcc, args.framerate, (video_width, video_height))
    except Exception as e:
        print(f"video_generator.py: error initializing video writer: {e}")
        sys.exit(1)
    
    for index, fn in enumerate(sorted(frame_numbers), start=1):
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(load_and_set_frame, cam, fn, args, camera_frames, height, width, black_frame)
                for cam in args.camera_order if cam in set(camera_frames.keys())
            ]
            all_images = []
            for f in futures:
                try:
                    result = f.result()
                    all_images.append(result)
                except Exception as e:
                    print(f"video_generator.py: error loading frame {fn} in thread: {e}")
                    break  # Skip this frame entirely
            else:
                # Only write frame if all threads succeeded
                canvas_height = video_height
                canvas_width = video_width
                canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

                for row_index in range(num_rows):
                    start = row_index * cams_per_row
                    end = start + cams_per_row
                    current_row = all_images[start:end]

                    vertical_offset = row_index * height

                    if len(current_row) == 1:
                        horizontal_offset = (canvas_width - width) // 2
                        canvas[vertical_offset:vertical_offset + height, horizontal_offset:horizontal_offset + width] = current_row[0]
                    else:
                        for col_index, img in enumerate(current_row):
                            horizontal_offset = col_index * width
                            canvas[vertical_offset:vertical_offset + height, horizontal_offset:horizontal_offset + width] = img

                video.write(canvas)
                percent_complete = (index / len(frame_numbers)) * 100
                print(f"Progress: {percent_complete:.2f}% ({index}/{len(frame_numbers)})", end="\r")
    video.release()

    print(f"Video created successfully at: {output_file}")
    missing_cameras = [cam for cam in args.camera_order if cam not in set(camera_frames.keys())]
    if missing_cameras:
        print(f"Cameras that were not found in the input folder: {missing_cameras}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except Exception as e:
        print(f"video_generator.py: unexpected error: {e}")
        sys.exit(1)
    print(f"Run time: {time.time() - start_time}")
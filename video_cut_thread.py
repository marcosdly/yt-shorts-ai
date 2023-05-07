from config import *
import os
import hashlib
import time
from local_logging import log
import moviepy.editor as editor
from io_utils import is_file, move_to_trash
import shutil

__all__ = ["watch_and_cut"]


def cut_video_if_valid(path: str):
    """
    Cuts a video into the maximum possible number of pieces
    where each piece have [duration] seconds.
    """
    # handle not being a file
    if not is_file(path):  # builtin string check
        log.error(f"Path {path} is not a file, skipping and moving to trash...")
        if os.path.exists(path):
            move_to_trash(path)
        return  # skip function execution if path is not file

    try:
        with editor.VideoFileClip(path) as video:
            if video.duration < 60:
                # handle being to small
                log.error(
                    "Provided video has 60 seconds or less! Please provide a longer one. Skipping and moving to trash...")
                move_to_trash(path)
                return

            durations = [10, 20, 30, 40, 50, 60]  # in seconds
            for clip_length in durations:
                possible_amount_of_clips = int(video.duration / clip_length)
                log.info(
                    f"Video {os.path.basename(video.filename)} with {video.duration} seconds will grant {possible_amount_of_clips} clips of {clip_length} each")
                start = 0
                end = clip_length
                for _ in range(possible_amount_of_clips):
                    clip = video.subclip(start, end)

                    # adjust clip range
                    start = end
                    end = end + clip_length

                    # sha256 of original video path
                    video_path_hash = hashlib.sha256(bytes(video.filename, "utf-8")).hexdigest()
                    # output_path = f"{OUPUT_FOLDER}/{temp_title}.mp4"
                    output_path = os.path.join(
                        OUTPUT_FOLDER,
                        CHILD_OUTPUT_FOLDER_BY_DURATION[clip_length],
                        f"TEMP-{video_path_hash}.mp4")

                    clip.write_videofile(output_path, codec="libx264", threads=THREADS)
                    log.info(f"Written clip {os.path.basename(output_path)} from {os.path.basename(video.filename)}")

                    with open(output_path, "rb") as in_drive_clip:
                        clip_content_hash = hashlib.sha256(in_drive_clip.read()).hexdigest()
                        # new_output_path = f"{OUPUT_FOLDER}/{clip_content_hash}.mp4"
                        new_output_path = os.path.join(
                            OUTPUT_FOLDER,
                            CHILD_OUTPUT_FOLDER_BY_DURATION[clip_length],
                            f"{clip_content_hash}.mp4")
                        os.rename(output_path, new_output_path)
                        log.info(f"Renamed clip {os.path.basename(output_path)} to {os.path.basename(new_output_path)}")
    except OSError:
        # handle not being a video
        log.error(f"Path {path} is not a video, skipping and moving to trash...")
        move_to_trash(path)
        return

    # Move videos that already have been cutted.
    # If execution gets to this point everything has gone well
    # and [path] is a valid video, with invalid videos/files/dirs being
    # moved to trash before this point.
    shutil.move(path, ALREADY_CUTTED_ORIGINAL_FOLDER)


def watch_and_cut():
    while True:
        with os.scandir(INPUT_FOLDER) as dir:
            for file_or_dir in dir:
                cut_video_if_valid(file_or_dir.path)
        time.sleep(120)  # in seconds

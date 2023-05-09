from config import *
import os
from os.path import basename, dirname, exists, join, isfile
import pathlib
import hashlib
import time
import moviepy.editor as editor
import shutil
from local_logging import log
from io_utils import move_to_trash, is_video
from db import create_video_doc_basic

__all__ = ["watch_and_cut"]

# TODO: divide function into smaller ones, as it is performing many actions of different natures
def cut_video_if_valid(path: str):
    """
    Cuts a video into the maximum possible number of pieces
    where each piece have [duration] seconds.
    """
    # handle not being a file
    if not isfile(path):  # builtin string check
        log.error(f"Path {path} is not a file, skipping and moving to trash...")
        if exists(path):
            move_to_trash(path)
        return  # skip function execution if path is not file

    if not is_video(path):
        log.error(f"Path {path} is not a video, skipping and moving to trash...")
        move_to_trash(path)
        return

    
    with editor.VideoFileClip(path) as video:
        # handle video being too small
        if video.duration < 60:
            log.error(
                "Provided video has 60 seconds or less! Please provide a longer one. Skipping and moving to trash...")
            move_to_trash(path)
            return
        
        # original video initial name
        video_initial_name = ""
        # original video final name (to be stored in db and become easier to find afterwards)
        video_final_name = ""
        # sha256 of original video initial path
        video_original_path_hash = ""
        # 17.532 seconds to hash the entire The Dark Knight (2008) movie on a i3 5005U
        # using sha256, so this is safe (To my standards, and for this application).
        video_content_hash = ""
        
        # Renaming initial video to the hash of its content for catalogation purposes.
        # Also, assigning and re-assigning pre-declared variables.
        if True: # introducing new scope to encapsulate variables
            parent_dir = dirname(path)
            original_extension = pathlib.Path(path).suffix
            # renaming all videos to the same name before hashing because file names can
            # influence the final hash
            pre_hash_path = join(parent_dir, "DUMMY-TEMP-HARD-CODED-TITLE.video")
            os.rename(src=path, dst=pre_hash_path)
            video_hash = hashlib.sha256(open(pre_hash_path, "rb").read()).hexdigest()
            post_hash_filename = f"{video_hash}{original_extension}"
            post_hash_path = join(parent_dir, post_hash_filename)
            os.rename(src=pre_hash_path, dst=post_hash_path)

            # assigning already initialized variables
            video_initial_name = basename(path)
            video_final_name = post_hash_filename
            video_original_path_hash = hashlib.sha256(bytes(path, "utf-8")).hexdigest()
            video_content_hash = video_hash
            path = post_hash_path # *re-assigning*

        # Creating clips and storing their info in the database

        durations = [10, 20, 30, 40, 50, 60]  # in seconds
        # durations = [10] # debug
        for clip_length in durations:
            possible_amount_of_clips = int(video.duration / clip_length)
            log.info(
                f"Video {basename(video.filename)} with {video.duration} seconds will grant {possible_amount_of_clips} clips of {clip_length} each")
            start = 0
            end = clip_length
            for _ in range(possible_amount_of_clips):
                clip = video.subclip(start, end)

                # adjust clip range
                start = end
                end = end + clip_length

                output_path = join(
                    OUTPUT_FOLDER,
                    CHILD_OUTPUT_FOLDER_BY_DURATION[clip_length],
                    f"TEMP-{video_original_path_hash}.mp4")

                clip.write_videofile(output_path, codec="libx264", threads=THREADS)
                log.info(f"Written clip {basename(output_path)} from {basename(video.filename)}")

                with open(output_path, "rb") as in_drive_clip:
                    clip_content_hash = hashlib.sha256(in_drive_clip.read()).hexdigest()
                    new_output_path = join(
                        OUTPUT_FOLDER,
                        CHILD_OUTPUT_FOLDER_BY_DURATION[clip_length],
                        f"{clip_content_hash}.mp4")
                    os.rename(output_path, new_output_path)
                    log.info(f"Renamed clip {basename(output_path)} to {basename(new_output_path)}")
                    
                    create_video_doc_basic(
                        basename = basename(new_output_path),
                        initial_name = video_initial_name,
                        content_hash = video_content_hash,
                        final_name = video_final_name,
                        duration = clip_length
                    )
    

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

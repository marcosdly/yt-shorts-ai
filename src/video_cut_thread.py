from config_wrapper import *
import os
from os.path import basename, dirname, exists, join, isfile
import pathlib
import hashlib
import time
import moviepy.editor as editor
import shutil
from local_logging import log
from json import load
from io_utils import move_to_trash, is_video
from db import create_video_doc_basic

__all__ = ["watch_and_cut"]

def cut_video_if_valid(path: str, info_json):
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
                        duration = clip_length,
                        media_name = info_json["media_name"],
                        media_year = info_json["year"]
                    )
    

    # Move videos that already have been cutted.
    # If execution gets to this point everything has gone well
    # and [path] is a valid video, with invalid videos/files/dirs being
    # moved to trash before this point.
    shutil.move(path, ALREADY_CUTTED_ORIGINAL_FOLDER)

def get_videos_recursively(dir_path: str) -> list[str]:
    if not isinstance(dir_path, str):
        raise TypeError("Provided path isn't a string, so it can't point to a directory.")
    if not isdir(dir_path):
        raise TypeError("Path doesn't point to a directory.")
    
    video_paths = []
    with os.scandir(dir_path) as inner_dir:
        for file in inner_dir:
            if file.is_file() and is_video(file.path):
                video_paths.append(file.path)
            if file.is_dir():
                video_paths.extend(get_videos_recursively(file.path))

    return video_paths

def move_to_series_dir_root(paths: list[str], series_dir: str) -> None:
    final_paths = []
    for i, path in enumerate(paths):
        new_path = join(series_dir, f"{i}{pathlib.Path(path).suffix}")
        shutil.move(src=path, dst=new_path)
        final_paths.append(new_path)
    return final_paths
        

def move_to_useless_folder(paths: list[str], useless_dir: str) -> None:
    if not isdir(useless_dir):
        os.mkdir(useless_dir)
    for path in paths:
        if is_video(path) or basename(path) == "info.json" or path == useless_dir:
            continue
        shutil.move(src=path, dst=useless_dir)

def watch_and_cut():
    while True:
        for media_type in ["movie", "series"]:
            # INPUT_FOLDER/movie or INPUT_FOLDER/series
            with os.scandir(join(INPUT_FOLDER, media_type)) as media_dir:
                # loop over media_type dir
                for video_dir in media_dir:
                    if not video_dir.is_dir():
                        continue
                    # if dir entry is a folder, open it
                    # INPUT_FOLDER/movie/scooby-doo-zombie-island
                    movie_series_dir = video_dir.path

                    # Using "with os.scandir" here causes a weird bug:
                    # the list of dir entries is wiped after some time.
                    # If you put a breakpoint after the if statement, the
                    # statement will run fine; put it before and let it 
                    # rest during debug and you can watch the list being wiped.
                    # with os.scandir(video_dir.path) as video_info_dir:
                    # Using the slower os.listdir instead.

                    def scanfolder() -> tuple[list[str], list[str]]:
                        entries = os.listdir(movie_series_dir)
                        return entries, [join(movie_series_dir, name) for name in entries]

                    dir_entries, dir_entries_paths = scanfolder()

                    # if folder doesn't have an info.json file, skip it
                    if not "info.json" in dir_entries:
                        log.error("No info file found on directory, skipping...")
                        continue

                    info = open(join(movie_series_dir, "info.json"), "rb")
                    info = load(info)
                    log.info(f"""Found {media_type}. Title: {info["media_name"]}; Year: {info["year"]}""")

                    if media_type == "movie":
                        # if folder has an info.json file and it is a movie, grab
                        # only the first video file inside it
                        videos = [x for x in dir_entries_paths if is_video(x)]
                        if len(videos) == 0:
                            log.error("No videos found inside a directory that contains a valid info file. Skipping...")
                            # TODO move valid folders with no videos to trash
                            continue
                        cut_video_if_valid(videos[0], info)
                    if media_type == "series":
                        # if folder has an info.json file and it is a series, loop over all
                        # its subdirectories searching for videos and put all theirs paths
                        # in a list
                        videos = get_videos_recursively(movie_series_dir)
                        # move all the videos to the same folder as the info.json file and
                        # rename them with their position in the generated list of paths
                        # (0.mkv, 1.mkv, 2.mkv, etc), which is arbitrary. Return
                        # the new paths.
                        videos = move_to_series_dir_root(videos, movie_series_dir)
                        # move all the folders left the 'useless' folder
                        useless_folder = join(movie_series_dir, "useless")
                        dir_entries, dir_entries_paths = scanfolder()
                        move_to_useless_folder(dir_entries_paths, useless_folder)
                        # for every video in the folder
                        for vid_path in videos:
                            cut_video_if_valid(vid_path, info)


        time.sleep(120)  # in seconds

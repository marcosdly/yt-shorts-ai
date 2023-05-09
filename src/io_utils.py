import os
import sys
import shutil
from moviepy.editor import VideoFileClip
from local_logging import log
from config import *


def is_dir(path: str) -> bool:
    # TODO: REPLACE BY NATIVE
    if not isinstance(path, str):
        return False
    try:
        dir = os.scandir(os.path.expanduser(path))
    except FileNotFoundError:
        return False
    finally:
        dir.close()
    return True


def is_dir_fatal(path: str) -> str:
    if not isinstance(path, str):
        log.error("Provided path is not a string.")
        sys.exit(1)
    try:
        with os.scandir(os.path.expanduser(path)):
            # entering here means it didn't raise
            return os.path.expanduser(path)
    except FileNotFoundError as err:
        log.error(f"{path} :: No such file or directory.", err)
        sys.exit(1)


def is_file(path: str) -> bool:
    # TODO: REPLACE BY NATIVE
    if not isinstance(path, str):
        return False
    try:
        os.stat(os.path.expanduser(path), follow_symlinks=True)
    except FileNotFoundError:
        return False
    return True


def is_file_fatal(path: str) -> str:
    if not isinstance(path, str):
        log.error("Provided path is not a string.")
        sys.exit(1)
    try:
        os.stat(os.path.expanduser(path), follow_symlinks=True)
    except FileNotFoundError as err:
        log.error(f"{path} :: No such file or directory", err)
        sys.exit(1)
    return os.path.expanduser(path)  # getting here means it exists


def move_to_trash(path: str):
    if not isinstance(path, str):
        raise TypeError("Provided path is not a string.")

    path = os.path.expanduser(path)

    if not os.path.exists(path):
        raise FileNotFoundError("Source file or directory doesn't exist. Can't move to trash.")

    shutil.move(path, TRASH_FOLDER)

def is_video(path: str) -> bool:
    if not isinstance(path, str):
        raise TypeError("Provided path is not a string.")
    
    if not os.path.isfile(path):
        raise TypeError("Provided path doesn't point to a file.")
    
    try:
        with VideoFileClip(path):
            return True
    except:
        return False
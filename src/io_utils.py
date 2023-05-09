from os.path import exists, expanduser, isdir, isfile
import sys
import shutil
from moviepy.editor import VideoFileClip
from local_logging import log
from config import *


def is_dir_fatal(path: str) -> str:
    if not isinstance(path, str):
        log.error("Provided path is not a string.")
        sys.exit(1)
    path = expanduser(path)
    if not isdir(path):
        log.error(f"{path} :: No such file or directory.", err)
        sys.exit(1)
    return path



def is_file_fatal(path: str) -> str:
    if not isinstance(path, str):
        log.error("Provided path is not a string.")
        sys.exit(1)
    path = expanduser(path)
    if not isfile(path):
        log.error(f"{path} :: No such file or directory", err)
        sys.exit(1)
    return path


def move_to_trash(path: str):
    if not isinstance(path, str):
        raise TypeError("Provided path is not a string.")

    path = expanduser(path)

    if not exists(path):
        raise FileNotFoundError("Source file or directory doesn't exist. Can't move to trash.")

    shutil.move(path, TRASH_FOLDER)

def is_video(path: str) -> bool:
    if not isinstance(path, str):
        raise TypeError("Provided path is not a string.")
    
    if not isfile(path):
        raise TypeError("Provided path doesn't point to a file.")
    
    try:
        with VideoFileClip(path):
            return True
    except:
        return False
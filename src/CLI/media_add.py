from datetime import datetime
from math import ceil
import shutil
from moviepy.editor import VideoFileClip
from os.path import isdir, join
from re import split
from os import scandir, mkdir, get_terminal_size
from json import dumps
from config_wrapper import INPUT_FOLDER

# TODO implement script to create new movie or series entry
# TODO erase not useful lines
# TODO implement this file properly for fuck sake

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def isvideo(path: str) -> bool:
    if not isinstance(path, str): return False
    try:
        with VideoFileClip(path): return True
    except: return False

def find_videos_recursively(dir_path: str) -> list[str]:
    if not isdir(dir_path): return []
    paths = []
    with scandir(dir_path) as entries:
        for file in entries:
            if isvideo(file.path): paths.append(file.path)
            if isdir(file.path): paths.extend(find_videos_recursively(file.path))
    return paths

def readchar(prompt: str, valid_answers: list[str]) -> str:
    if len([s for s in valid_answers if len(s) != 1]) > 0:
        # if there's any string with length different than 1
        raise ValueError("All the valid answers must be a single character string.")

    valid_answers = list(map(lambda s: s.lower(), valid_answers)) # normalize strings
    answer = ""
    print()
    while True:
        print(LINE_UP, end=LINE_CLEAR)
        answer = input(prompt).lower() # normalize input
        if not answer in valid_answers:
            continue
        break
    return answer

def readline(prompt: str) -> str:
    answer = ""
    print(); print() # dummy calls to prevent overcomplicated checks
    while True:
        print(LINE_UP, end=LINE_CLEAR); print(LINE_UP, end=LINE_CLEAR) # clear the prompts
        answer = input(prompt)
        yes_or_no = input(f"Is \"{answer}\" correct? (N/y) ")
        if yes_or_no.lower() != "y":
            continue
        else:
            # clear only the correctness check
            print(LINE_UP, end=LINE_CLEAR)
            break
    return answer

def readint(prompt: str, validation) -> int:
    if not callable(validation):
        raise ValueError("You must pass in a function.")
    elif not isinstance(validation(0), bool):
        raise ValueError("Validation function must return a boolean value.")

    answer = 0
    print()
    while True:
        print(LINE_UP, end=LINE_CLEAR)
        try:
            answer = int(input(prompt))
            if not validation(answer):
                raise ValueError("Answer is an integer, but not a correct one.")
            break
        except (ValueError, TypeError): continue
    return answer

def is_valid_path(path: str, media_type: str) -> bool:
    """Checks if the provided path points to a correct source of media. A video
    if the media type is a movie, or a directory with videos if the media type is series."""

    if not isinstance(path, str) and isinstance(media_type, str):
        return False
    elif not media_type in ["movie", "series"]:
        return False
    
    if media_type == "movie" and not isvideo(path):
        return False
    elif media_type == "series":
        if (not isdir(path)) or len(find_videos_recursively(path)) == 0:
            return False
        
    return True

def readpath(prompt: str, media_type: str) -> str:
    # developer responsability
    if not isinstance(prompt, str) and isinstance(media_type, str):
        raise ValueError("Prompt and media type must be both strings.")
    if not media_type in ["movie", "series"]:
        raise ValueError("Incorrect media type.")
    
    # user responsability
    path = ""; lines_to_delete =1
    print()
    while True:
        for _ in range(lines_to_delete):
            print(LINE_UP, end=LINE_CLEAR)
        path = input(prompt)
        # TODO implement this line_to_delete system in all functions
        lines_to_delete = ceil(len(prompt+path) / get_terminal_size().columns)
        if not is_valid_path(path, media_type):
            continue
        break
    return path
        

def media_add(relevant_argv) -> None: 
    path = None
    try:
        path = relevant_argv[0]
    except IndexError:
        # if path isn't provided, ask for it later
        print("Couldn't find a path in the list of arguments.")
        print("You be asked it later alongside the type of the media this path points to.")
        print("If invalid, the program will exit.")
        print("INFO: For movies, the path must point to a video file.")
        print("INFO: For series, the path must point to a folder tree that contains video files.")
        print() # empty line to separate text

    preset_media_type = None
    if path != None:
        # if path is provided as an argument, check to see if its valid
        # if not, print an error message and exit
        if is_valid_path(path, "movie"): preset_media_type = "movie"
        elif is_valid_path(path, "series"): preset_media_type = "series"
        else:
            print("The provided path can't be neither a movie nor a series. Make sure to double check.")
            print("INFO: For movies, the path must point to a video file.")
            print("INFO: For series, the path must point to a folder tree that contains video files.")
            exit(1)

        # here media must me presetted
        print(f"Provided path is only valid for {preset_media_type}.")    
        print(f"WARNING: Using \"{preset_media_type}\" as media type.")
        print() # empty line to separate text

    media_name = readline("What's the name of the media? ")
    max_year = datetime.now().year + 1
    media_year = readint(f"What's the year of launch of this media (1800 < x <= {max_year})? ",
                         lambda n: n > 1800 and n <= max_year)

    media_type = ""
    if preset_media_type == None:
        media_type = readchar("Is your media a [m]ovie or a [s]eries? ", ["m", "s"])
        match media_type:
            case "m": media_type = "movie"
            case "s": media_type = "series"
        path = readpath(f"Provide a path to a {media_type}: ", media_type)
    else:
        media_type = preset_media_type

    media_dir_name = "-".join(split("[ ,.':()\[\]{}]", media_name.lower()))
    media_dir_path = join(INPUT_FOLDER, media_type, media_dir_name)
    info_json_string = dumps({"media_name": media_name, "year": media_year}, indent=2) + "\n"

    if not isdir(media_dir_path): mkdir(media_dir_path)
    with open(join(media_dir_path, "info.json"), "wt") as info_file:
        info_file.write(info_json_string)
    shutil.move(src=path, dst=media_dir_path)

    print("Media successfully added!")
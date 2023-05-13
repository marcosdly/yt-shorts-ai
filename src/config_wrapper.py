from json import load
from os.path import expanduser, isdir, join, dirname

# implementing it here too to avoid circular dependency issues
def is_dir_fatal(path: str) -> str:
    if not isinstance(path, str):
        raise ValueError("PATH IS NOT STRING")

    path = expanduser(path)

    if not isdir(path):
        raise ValueError(f"{path} IS NOT A DIRECTORY OR DOESN'T EXIST")

    return path

def is_int_fatal(i: int) -> int:
    if not isinstance(i, int):
        raise ValueError(f"{i} IS NOT AN INTEGER")

    return i

def child_folders_by_duration(original_dict: dict[str, str]) -> dict[int, str]:
    new_dict = {}
    if not isinstance(original_dict, dict):
        raise ValueError("PROVIDED ARGUMENT IS NOT A DICTIONARY")
    
    try:
        for key, value in original_dict.items():
            if not isinstance(key, str): raise ValueError()
            new_dict[int(key)] = value
        return new_dict
    except ValueError:
        # throw it again but with a better message
        raise ValueError("One or more keys are not string representations of integers. Could not convert the key to integer.")

config_json_path = join(dirname(__file__), "..", "config", "config.json")
config = load(open(config_json_path, "rb")) # can throw

# Relevant directories
INPUT_FOLDER                      = is_dir_fatal(config["INPUT_FOLDER"])
OUTPUT_FOLDER                     = is_dir_fatal(config["OUTPUT_FOLDER"])
REJECTED_FOLDER                   = is_dir_fatal(config["REJECTED_FOLDER"])
APPROVED_FOLDER                   = is_dir_fatal(config["APPROVED_FOLDER"])
ALREADY_POSTED_FOLDER             = is_dir_fatal(config["ALREADY_POSTED_FOLDER"])
TRASH_FOLDER                      = is_dir_fatal(config["TRASH_FOLDER"])
TEMP_FOLDER                       = is_dir_fatal(config["TEMP_FOLDER"])
LOGS_FOLDER                       = is_dir_fatal(config["LOGS_FOLDER"])
ALREADY_CUTTED_ORIGINAL_FOLDER    = is_dir_fatal(config["ALREADY_CUTTED_ORIGINAL_FOLDER"])
CHILD_OUTPUT_FOLDER_BY_DURATION = \
    child_folders_by_duration(config["CHILD_OUTPUT_FOLDER_BY_DURATION"])

# CPU threads to use while ouputting video
THREADS = is_int_fatal(config["THREADS"])
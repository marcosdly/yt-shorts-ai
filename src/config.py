import sys
from os.path import exists, expanduser, isdir

# implementing it here too to avoid circular dependency issues
def is_dir_fatal(path: str) -> str:
    if not isinstance(path, str):
        print("PATH IS NOT STRING")
        sys.exit(1)
    path = expanduser(path)
    if not isdir(path):
        print(f"{path} IS NOT A DIRECTORY OR DOESN'T EXIST")
        sys.exit(1)
    return path

# Relevant directories
INPUT_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.uncutted-videos-input")
OUTPUT_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.cutted-videos-pre-validation")
REJECTED_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.rejected-videos")
APPROVED_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.approved-not-posted-videos")
ALREADY_POSTED_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.approved-already-posted-videos")
TRASH_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.invalid-files-and-dirs-trash")
TEMP_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.tmp")
ALREADY_CUTTED_ORIGINAL_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.already-cutted-original-videos")
CHILD_OUTPUT_FOLDER_BY_DURATION = {
    10: "10s",
    20: "20s",
    30: "30s",
    40: "40s",
    50: "50s",
    60: "60s"
}

LOGS_FOLDER = is_dir_fatal("~/yt-shorts-ai.d/.yt-shorts.log.d")

# CPU threads to use while ouputting video
THREADS = 4

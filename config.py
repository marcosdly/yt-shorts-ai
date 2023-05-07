import sys, os

# implementing it here too to avoid circular dependency issues
def is_dir_fatal(path: str) -> str:
    if not isinstance(path, str):
        print("PATH IS NOT STRING")
        sys.exit(1)

    path = os.path.expanduser(path)

    if not os.path.exists(path):
        print(f"NO SUCH FILE OR DIRECTORY {path}")
        sys.exit(1)

    try:   
        with os.scandir(path):
            return path
    except:
        print(f"{path} IS NOT A DIRECTORY")
        sys.exit(1)

# Relevant directories
INPUT_FOLDER = is_dir_fatal("~/.uncutted-videos-input")
OUTPUT_FOLDER = is_dir_fatal("~/.cutted-videos-pre-validation")
REJECTED_FOLDER = is_dir_fatal("~/.rejected-videos")
APPROVED_FOLDER = is_dir_fatal("~/.approved-not-posted-videos")
ALREADY_POSTED_FOLDER = is_dir_fatal("~/.approved-already-posted-videos")
TRASH_FOLDER = is_dir_fatal("~/.invalid-files-and-dirs-trash")
CHILD_OUTPUT_FOLDER_BY_DURATION = {
    10: "10s",
    20: "20s",
    30: "30s",
    40: "40s",
    50: "50s",
    60: "60s"
}

LOGS_FOLDER = is_dir_fatal("~/.yt-shorts.log.d")

# CPU threads to use while ouputting video
THREADS = 4

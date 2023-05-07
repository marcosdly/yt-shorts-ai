from io_utils import is_dir_fatal

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

import threading
from video_cut_thread import watch_and_cut


def main() -> None:
    video_cutting_thread = threading.Thread(target=watch_and_cut)
    video_cutting_thread.start()  # run forever, as it needs to watch a folder


if __name__ == "__main__":
    main()

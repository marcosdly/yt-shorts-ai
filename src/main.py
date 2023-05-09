import threading
from video_cut_thread import watch_and_cut
from ai import config_openai


def main() -> None:
    config_openai()
    video_cutting_thread = threading.Thread(target=watch_and_cut, name="Video_Cutting_Thread")
    video_cutting_thread.start()  # run forever, as it needs to watch a folder


if __name__ == "__main__":
    main()

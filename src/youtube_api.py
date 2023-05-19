from time import sleep
from selenium_youtube import Youtube
from selenium_chrome import Chrome
from io_utils import is_video

# TODO commit kstopit import timoutable
# from kstopit

def login() -> Youtube:
    return Youtube(browser=Chrome())

def youtube_url_by_id(id: str) -> str:
    return f"https://youtu.be/{id}"

def post_video_youtube(youtube: Youtube, video_path: str, title: str, tags: list[str]) -> str | None:
    if not is_video(video_path):
        raise ValueError("Provided path is not a video.")

    for _ in range(10):
        ok, video_id = youtube.upload(video_path=video_path, title=title,
                                       description=title+" #shorts", tags=tags)
        if ok:
            return youtube_url_by_id(video_id)
        else:
            sleep(60)
            continue
    return None
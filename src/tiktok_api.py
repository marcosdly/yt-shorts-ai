from tiktokapipy.api import TikTokAPI
from tiktok_uploader.upload import upload_video
from db import VideoDoc
from collections import namedtuple
from json import load
from os.path import join, dirname
from io_utils import is_video

def login() -> tuple[str, str]:
    # TODO create function that return the config folder path; update calls
    login_info = namedtuple("LoginInfo", ["session_id", "username"])
    config_path = join(dirname(__file__), "..", "config", "tiktok_login.json")
    config = load(open(config_path, "rb"))
    return login_info(config["session_id"], config["username"])

def last_video_url(tiktok: tuple[str, str]) -> str:
    url = "https://www.tiktok.com/@{}/video/{}"
    with TikTokAPI() as api:
        for video in api.user(tiktok.username).videos:
            url = url.format(tiktok.username, video.id)
            break # only first video
        return url

def post_video_tiktok(tiktok: tuple[str, str], video_path: str, document: VideoDoc) -> str:
    # TODO post video to tiktok
    # TODO get last video's link
    if not is_video(video_path):
        raise ValueError("Provided path doesn't point to a video.")

    upload_video(filename=video_path, description=document.title, sessionid=tiktok.session_id)

    return last_video_url(tiktok)

if __name__ == "__main__":
    from tiktokapipy.api import TikTokAPI
    with TikTokAPI() as api:
        # api = TikTokApi()
        user = api.user("therock")
        # videos = user.videos(count=1)
        # videos = TikTokApi.user(username="therock").videos(count=1)
        for video in user.videos:
            # print("BASIC INFO", video.info())
            # print("FULL INFO", video.info_full())
            # print("AS DICT", video.as_dict)
            print(video.author, video.id, video.stats)
            break

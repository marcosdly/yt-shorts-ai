from pathlib import Path
from instagrapi import Client
from db import VideoDoc
from os.path import dirname, join
from json import load
from config_wrapper import TEMP_FOLDER

CREDENTIALS = load(open(join(dirname(__file__), "..", "config", "instagram_login.json"), "rb"))
SETTINGS_PATH = join(TEMP_FOLDER, "instagram-auth.json")

def login() -> Client:
    cl = Client()
    try:
        cl.load_settings(SETTINGS_PATH)
    except FileNotFoundError:
        cl.login(CREDENTIALS["username"], CREDENTIALS["password"], verification_code=CREDENTIALS["2FA"])
        cl.dump_settings(SETTINGS_PATH)
    return cl

def post_video_instagram(client: Client, video_path: Path, document: VideoDoc) -> str:
    media = client.clip_upload(video_path, document.title)
    url = f"https://www.instagram.com/p/{media.code}"
    return url
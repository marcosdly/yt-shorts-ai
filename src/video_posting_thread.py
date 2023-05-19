from pathlib import Path
from shutil import move
from db import VideoDoc
from datetime import datetime
from time import sleep
from os.path import join, basename, dirname
# from youtube_api import login as yt_login, post_video_youtube, VideoData
from youtube_api import login as yt_login, post_video_youtube
from instagram_api import login as insta_login, post_video_instagram
from tiktok_api import login as tiktok_login, post_video_tiktok
from io_utils import is_video
from config_wrapper import *

# TODO put credential files in their own directory

def move_to_already_posted(video_path: str, duration: int) -> str:
    if not isinstance(video_path, str) and isinstance(duration, int):
        raise ValueError("Invalid argument type.")
    if not is_video(video_path):
        raise ValueError("Path doesn't point to a video")

    new_path = join(ALREADY_POSTED_FOLDER,
                    CHILD_OUTPUT_FOLDER_BY_DURATION[duration],
                    basename(video_path))
    
    move(src=video_path, dst=new_path)
    
    return new_path

def get_video_path(doc: VideoDoc) -> str:
    return join(APPROVED_FOLDER, CHILD_OUTPUT_FOLDER_BY_DURATION[doc.duration],
                doc.basename)

def watch_db_and_post_video() -> None:
    can_post_youtube = True # prevent youtube api overload and ban (I hope)
    # login
    youtube = yt_login()
    instagram = insta_login()
    tiktok = tiktok_login()
    while True:
        # wait a minute before checking for time
        sleep(60)
        hour = datetime.now().hour
        # hour_now = 10 # debug

        # post every 10AM and 5PM on youtube
        if can_post_youtube and (hour == 10 or hour == 17):
            doc = VideoDoc.objects(youtube__posted=False,
                                   rejected=False).first()
            if not doc: continue
            
            video_path = get_video_path(doc)
            tags = [s.replace("#", "") for s in doc.title.split(" ") if s.startswith("#")]

            # video_data = VideoData(video_path, doc.title, tags)
            
            # TODO store video url and the upload-success status in the database
            url = post_video_youtube(youtube, video_path, doc.title, tags)

            if url == None:
                can_post_youtube = False
                continue

            doc.youtube.posted = True
            doc.youtube.url = url
            doc.save()
                
        # post every 8AM and 3PM on tiktok
        if hour == 8 or hour == 15:
            doc = VideoDoc.objects(tiktok__posted=False,
                                   rejected=False).first()
            if not doc: continue
            
            video_path = get_video_path(doc)
            
            # TODO implement api overload system from youtube here too

            url = post_video_tiktok(tiktok, video_path, doc)

            doc.tiktok.posted = True
            doc.tiktok.url = url
            doc.save()

        # post every 11AM and 6PM on instagram
        if hour == 11 or hour == 18:
            doc = VideoDoc.objects(instagram__posted=False,
                                   rejected=False).first()
            if not doc: continue
            
            video_path = Path(get_video_path(doc))
            
            url = post_video_instagram(instagram, video_path, doc)

            doc.instagram.posted = True
            doc.instagram.url = url
            doc.save()

        posted_everywhere_doc = VideoDoc.objects(youtube__posted=True, tiktok__posted=True,
                                                 instagram__posted=True).first()
        if posted_everywhere_doc: # if found any
            video_path = get_video_path(posted_everywhere_doc)
            move_to_already_posted(video_path, posted_everywhere_doc.duration)
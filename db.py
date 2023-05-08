import json, os
from mongoengine import *

__all__ = ["Video"]

config_file_path = os.path.abspath(f"{os.path.dirname(__file__)}/config/database.json")
config = json.load(open(config_file_path, "rb"))

connect(
    db=config["db"],
    host=config["host"],
    port=config["port"],
    username=config["user"],
    password=config["password"]
)


class VideoDoc(Document):
    # required
    original_video_initial_name = StringField(required=True)
    original_video_content_hash = StringField(required=True)
    original_video_final_name = StringField(required=True)
    basename = StringField(required=True,primary_key=True)
    duration = IntField(required=True)

    # Setting default="" or null=True (either or both) doesn't create their
    # respective fields on saving. Also, didn't find a way to query for null fields,
    # so this behaviour is acceptable as you can query for non existing fields, which,
    # in this case, was the purpose of null anyway.
    transcription = StringField()

    # To prevent unwanted posting.
    # Check for ("transcription" field exists) == False and "rejected" == True
    # to see videos with pending evaluation.
    rejected = BooleanField(default=True)
    
    content_description = StringField()
    title = StringField()
    posted = BooleanField(default=False)
    youtube_url = StringField()
    meta = {"collection": "videos"}

    
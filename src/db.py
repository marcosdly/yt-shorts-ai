import json, os
from mongoengine import *

__all__ = ["Video"]

config_file_path = os.path.abspath(f"{os.path.dirname(__file__)}/../config/database.json")
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
    media_name = StringField(required=True)
    media_year = StringField(required=True)
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

def create_video_doc_basic(
        initial_name: str, content_hash: str,
        final_name: str, duration: int, 
        media_name: str, media_year: int,
        basename: str = None, id: str = None) -> None:
    """Stores a document entry for a video with ONLY the required fields. Other fields beside
    the required ones are not touched by this function. The 'id' and 'basename' arguments are
    synonymous; specify what sounds more descriptive."""

    # if none of these exist (id and basename are synonymous)
    # note that none of the required fields are booleans, which allows the use of logical operators
    if not ((id or basename)
            and initial_name
            and content_hash
            and final_name
            and duration
            and media_name
            and media_year):
        raise TypeError("All arguments are required, except id and basename, which are synonymous.")

    temp_doc = VideoDoc()
    temp_doc.original_video_initial_name   = initial_name
    temp_doc.original_video_content_hash   = content_hash
    temp_doc.original_video_final_name     = final_name
    temp_doc.basename                      = basename or id
    temp_doc.duration                      = duration
    temp_doc.media_name                    = media_name
    temp_doc.media_year                    = media_year
    temp_doc.save()
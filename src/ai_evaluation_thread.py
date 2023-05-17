from os import listdir
from config_wrapper import *
from os.path import join, basename, dirname
from shutil import move
from time import sleep
from hashlib import sha256
from moviepy.editor import VideoFileClip
import openai
from openai.error import RateLimitError
import prompts as prompts
from re import search
from json import loads
from db import VideoDoc
from io_utils import is_video
from local_logging import log
from edit_video import edit_video

__all__ = ["watch_db_and_evaluate_video_AI"]

def move_to_rejected_folder(path: str, duration: int) -> str:
    """Returns final path of file after moving it."""
    if not isinstance(path, str):
        raise TypeError("Provided path is not a string.")
    if not is_video(path):
        raise TypeError("Provided path doesn't represent a video.")
    final_path = join( # points to a dir; no problems
        REJECTED_FOLDER,
        CHILD_OUTPUT_FOLDER_BY_DURATION[duration])
    move(src=path, dst=final_path)
    return final_path

def move_to_approved_folder(path: str, duration: int) -> str:
    """Returns final path of file after moving it."""
    if not isinstance(path, str):
        raise TypeError("Provided path is not a string.")
    if not is_video(path):
        raise TypeError("Provided path doesn't represent a video.")
    final_path = join( # points to a dir; no problems
        APPROVED_FOLDER,
        CHILD_OUTPUT_FOLDER_BY_DURATION[duration],
        basename(path))
    move(src=path, dst=final_path)
    return final_path

def get_transcription(audio_file_bytes: bytes, media_name: str, media_year: int) -> str:
    """Returns an audio's transcription. If the model is overloaded,
    waits some seconds before trying again. Tries until gets it."""
    seconds, count = (10, 0)
    while True:
        try:
            return openai.Audio.transcribe(model="whisper-1", file=audio_file_bytes,
                                           prompt=prompts.gen_transcription_prompt(media_name, media_year))["text"]
        except RateLimitError:
            if count > 0 and count % 2 == 0 and seconds < 60:
                # every 2 tries and if time is less than a minute
                seconds += 10
            count += 1
            sleep(seconds)

def get_completion(messages: list[dict[str, str]]):
    """Returns an chat completion for the given message history.
    If the model is overloaded, waits some seconds before trying again.
    Tries until gets it."""
    model = "gpt-3.5-turbo"
    seconds, count = (20, 0)
    while True:
        try:
            return openai.ChatCompletion.create(model=model, messages=messages)
        except RateLimitError:
            if count > 0 and count % 2 == 0 and seconds < 60:
                # every 2 tries and if time is less than a minute
                seconds += 20
            count += 1
            sleep(seconds)


def evaluate_with_ai(video_path: str, document: VideoDoc) -> None:
    """This function: validates the content of a video and generate its title; mutates the database document
    related to that video and saves it; moves video to rejected or approved folders according to its fate."""
    temp_audio_file_name = "{}{}".format(sha256(bytes("yt-shorts-ai", "utf-8")).hexdigest(), ".mp3")
    temp_audio_file_path = join(TEMP_FOLDER, temp_audio_file_name)
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(temp_audio_file_path)
        audio_file = open(temp_audio_file_path, "rb")
        document.transcription = get_transcription(audio_file, document.media_name, document.media_year)

        # ai stuff
        messages = [{
            "role": "user", 
            "content": prompts.gen_validation_prompt(
                document.transcription, document.media_name,
                document.media_year, document.duration            
            )}]
        completion = get_completion(messages)
        text_answer = completion.choices[0].message["content"]

        def reject(motive: str) -> None:
            if motive == "bad_transcription":
                log.info(f"Video {document.basename} ({document.duration} seconds) didn't pass the test. See next logs for more information.")
                log.info(fr"""Transcription: "{document.transcription}" """)
                log.info(fr"""Answer: "{text_answer}" """)
            elif motive == "no_json_response":
                log.info(f"Video {document.basename} ({document.duration} seconds) passed the test. But ai model didn't answered with valid json.")
            else:
                raise ValueError("Invalid motive for rejecting a video.")
            document.rejected = True
            document.posted = False
            document.save()
            move_to_rejected_folder(video_path, document.duration)

        # ai thinks it didn't comply to the criteria
        if not text_answer.startswith("Yes"):
            reject(motive="bad_transcription")
            return
        
        log.info(f"Video {document.basename} passed the validation.")
        # include response
        messages.append(completion.choices[0].message)
        # include next prompt
        messages.append({"role": "user", "content": prompts.justify_your_answer_prompt})
        completion = get_completion(messages)

        # include response (description of the content of the transcipted audio)
        messages.append(completion.choices[0].message)
        document.content_description = completion.choices[0].message["content"]
        
        # add final prompt
        messages.append({"role": "user", "content": prompts.write_title_json_prompt})


        json_data_answer = ""
        json_data = {}
        attempts = 1
        while True:
            if attempts > 2:
                reject(motive="no_json_response")
                return
            try:
                completion = get_completion(messages)
                json_data_answer = completion.choices[0].message["content"]
                json_data = loads(search(prompts.json_title_data_regex, json_data_answer).group(0))
                break
            except AttributeError:
                attempts += 1
                continue

        # include final response, the one with the important data
        messages.append(completion.choices[0].message)
        
        # hashtags (they dont have the '#' at first)
        json_data["hashtags"] = [f"#{s}" for s in json_data["hashtags"]]
        document.title = " ".join([json_data["title"], *json_data["hashtags"]])

        document.rejected = False
        document.save()
        log.info("Database entry successfully written.")
        video_path = move_to_approved_folder(video_path, document.duration)
        log.info("Video files successfully moved to approved videos folder.")
        log.info("Rendering new version of video...")
        # with VideoFileClip(video_path) as video:
        #     new_video = edit_video(video)
        #     temp_path = join(dirname(video_path), f"RENDERING-{basename(video_path)}")
        #     new_video.write_videofile(temp_path, codec="libx264", threads=THREADS)
        #     move(src=temp_path, dst=video_path)
        # log.info("New video rendered. Ready to be uploaded.")
        return


def watch_db_and_evaluate_video_AI() -> None:
    while True:
        # querying for videos not yet validated
        # they must be inside the "not yet validated" specific folder
        for doc in VideoDoc.objects(transcription__exists=False, rejected=True):
            video_path = join(OUTPUT_FOLDER,
                              CHILD_OUTPUT_FOLDER_BY_DURATION[doc.duration],
                              doc.basename)
            evaluate_with_ai(video_path=video_path, document=doc)
            # wait to limit requested data limit to reset (1 min)
            print("Video successfully processed with ai, waiting 1 minute until trying another.")
            sleep(60)

        # wait some time to prevent system or database freezes due to too many queries
        pre_db_check_sleep = 60
        print(f"No database entries found, waiting {pre_db_check_sleep} seconds...")
        sleep(pre_db_check_sleep)
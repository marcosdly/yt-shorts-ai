from io import BufferedReader
from pathlib import Path
from random import choice
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
import moviepy.video.fx.all as vfx
from skimage.filters import gaussian
import whisper
from subtitles_fx import SUBTITLE_FX, COLORS


__all__ = ["edit_video"]

# stolen: https://gist.github.com/Integralist/4ca9ff94ea82b0e407f540540f1d8c6c
# and slightly modified
def calculate_aspect(width: int, height: int) -> tuple[str, bool]:
    temp = 0
    isphone = False

    def gcd(a, b):
        """The GCD (greatest common divisor) is the highest number that evenly divides both width and height."""
        return a if b == 0 else gcd(b, a % b)

    if width == height:
        return "1:1"

    if width < height:
        isphone = True
        temp = width
        width = height
        height = temp

    divisor = gcd(width, height)

    x = int(width / divisor) if not temp else int(height / divisor)
    y = int(height / divisor) if not temp else int(width / divisor)

    return f"{x}:{y}", isphone

def rule_of_three(a, b, c) -> int | float:
    """Proportion relation. B is equivalent to C, just like A is equivalent to X (return value)."""
    x = (b*c)/a
    return x

def local_transcription(audio_path: Path, prompt: str) -> dict[str, str | list]:
    model = whisper.load_model("small")
    transcription = model.transcribe(audio=str(audio_path), temperature=0.0, initial_prompt=prompt)
    return transcription

def create_subs_clips(segments: list[dict[str, str | float]], duration: int,
                      frame_size: tuple[int, int]) -> list[TextClip]:
    fx_func = choice(SUBTITLE_FX)
    text_color = choice(COLORS)
    upper_case = choice([True, False])
    subtitles: list[TextClip] = []
    for segment in segments:
        clip: TextClip = fx_func(segment["text"], segment["start"], segment["end"],
                                 text_color, duration, frame_size, upper_case)
        subtitles.append(clip)
    return subtitles
        
def edit_video(video: VideoFileClip, audio_path: Path, prompt: str) -> CompositeVideoClip:
    final_size = width, height = (1080, 1920) # phone-like 16:9 (width, heigth)
    # final_size = width, height = (480, 854) # debug
    principal_video = None
    aspect_ratio, isphone = calculate_aspect(video.w, video.h)

    if isphone:
        # resize video in way that it always fit in the final video area
        if video.w > width:
            principal_video = vfx.resize(video, height=height)
        if video.h > height:
            principal_video = vfx.resize(video, width=width)

        final_video_area_px = width * height
        video_area_px = video.w * video.h
        # percentage of how much the smaller video (initial) is filling the
        # bigger one (final) based on an area of square pixels (px^2)
        # 1 >= x > 0 (type(x) == float)
        filling_percen = rule_of_three(video_area_px, final_video_area_px, 1)

        # if the video fills the frame too much, might as well make it the size of the frame
        if filling_percen >= .95:
            principal_video = vfx.resize(principal_video, width=width, height=height)
        elif filling_percen >= .85:
            # If it doesn't fill the frame too much, but some borders are touching the frame,
            # make it smaller so it can have borders when centered.
            principal_video = vfx.resize(principal_video, .95) # 95% of the initial size
            
        principal_video.set_position(("center", "center"))
    elif aspect_ratio != "4:3":
        # Normalizing video size to make it easier to crop.
        principal_video = vfx.resize(video, height=1080) # resize to 1080p
        # 4:3 full hd is 1440x1080
        principal_video = vfx.crop(principal_video, width=1440, height=1080) # 4:3 full hd
        principal_video = vfx.resize(principal_video, width=width)
        principal_video.set_position(("center", "top"))
    else:
        principal_video = vfx.resize(video, width=width)
        principal_video.set_position(("center", "top"))

    # bluring frames of the background video
    blury_video = vfx.resize(video, height=height)
    blury_video.set_position(("center", "center")) # needs to come before resizing
    # cropping the unseen parts to make it less demanding CPU-wise (i guess)
    # if isphone:
    #     # horizontally, half of the pixels that are untouched by the main video
    #     x_half = (width - principal_video.w) / 2
    #     y_half = (height - principal_video.h) / 2 # same but vertically
    #     # coordinates in pixels
    #     left, right = (x_half, width - x_half)
    #     top, bottom = (y_half, height - y_half)

    #     blury_video = vfx.crop(blury_video, x1=left, y1=top, x2=right, y2=bottom)
    # elif aspect_ratio != "4:3":
    #     # crop to visible frame's size
    #     blury_video = vfx.crop(blury_video, width=width, height=height)
    #     visible_pixels_below_main_video = height - principal_video.h
    #     # remove only pixels above y1
    #     blury_video = vfx.crop(blury_video, y1=visible_pixels_below_main_video)

    # see: https://zulko.github.io/moviepy/examples/quick_recipes.html?highlight=blur#blurring-all-frames-of-a-video
    blury_video = blury_video.fl_image(
        lambda image: gaussian(image.astype(float), sigma=30)) # apply blur

    transcription = local_transcription(audio_path, prompt)
    subtitles = create_subs_clips(transcription["segments"], video.duration, final_size)

    # first one will be the background
    clips = [blury_video, principal_video, *[c.set_position(("center", "center")) for c in subtitles]]

    final_video = CompositeVideoClip(size=final_size, # phone-like 16:9
                                            # use_bgclip=True,  # first clip is the background
                                            clips=clips)
    return final_video

if __name__ == "__main__":
    from db import VideoDoc
    from config_wrapper import APPROVED_FOLDER, CHILD_OUTPUT_FOLDER_BY_DURATION, TEMP_FOLDER
    from os.path import join
    import prompts
    doc = VideoDoc.objects(rejected=False).first()
    video_path = join(APPROVED_FOLDER,
                      CHILD_OUTPUT_FOLDER_BY_DURATION[doc.duration], doc.basename)
    prompt = prompts.gen_transcription_prompt(doc.media_name, doc.media_year)
    temp_audio_path = join(TEMP_FOLDER, "debug-video-editing.mp3")
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(temp_audio_path)
        new_video = edit_video(video, Path(temp_audio_path), prompt)
        new_video.write_videofile(join(TEMP_FOLDER, "subtitles.mp4"),
                                codec="libx264", threads=4)

import re
from moviepy.editor import TextClip

__all__ = ["SUBTITLE_FX"]

COLORS: list[bytes] = [b"aqua", b"tomato", b"lavender", b"lime", b"fuchsia", b"yellow"]
COLOR_BLACK: bytes = b"black"
UNWANTED_CHARS: str = "[.]"

class TextFXProps:
    def __init__(self, font: str, size: tuple[int, int], txt_color: str,
                 stroke_width: int, stroke_color: str, letter_spacing: int) -> None:
        # TODO document the whole program
        if not font in TextClip.list("font"):
            raise ValueError("Specified font is not installed or is not permitted.")
        permited_colors = TextClip.list("color")
        if not (txt_color in permited_colors) and (stroke_color in permited_colors):
            raise ValueError("One or more of the specified colors are not valid.")

        self.font             = font
        self.size             = size
        self.txt_color        = txt_color
        self.stroke_width     = stroke_width
        self.stroke_color     = stroke_color
        self.letter_spacing   = letter_spacing

def one(text: str, start: float, end: float, txt_color: bytes,
                       duration: int, frame_size: tuple[int, int], upper: bool) -> TextClip:
    
    width, height = frame_size
    font_frame_size = (width*.8, height*.2)
    
    props = TextFXProps(font="Rubik-One-Regular", size=font_frame_size, txt_color=txt_color,
                        stroke_width=4, stroke_color=COLOR_BLACK, letter_spacing=2)
    
    # removing unwanted characters
    text = re.sub(UNWANTED_CHARS, "", text)

    # change case
    if upper: text = text.upper()
    else: text = text.lower()
    
    clip = TextClip(txt=text, font=props.font, size=props.size,
                    color=props.txt_color, stroke_color=props.stroke_color,
                    stroke_width=props.stroke_width, kerning=props.letter_spacing,
                    method="caption", align="center")
    
    clip = clip.set_duration(duration)
    clip = clip.set_start(start, change_end=False)
    clip = clip.set_end(end)
    clip.set_position(("center", "center"))

    return clip


SUBTITLE_FX: list[callable] = [one]
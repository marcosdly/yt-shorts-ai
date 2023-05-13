__all__ = [
    "justify_your_answer_prompt", "write_title_json_prompt", 
    "json_title_data_regex", "gen_validation_prompt", "gen_transcription_prompt"]

# waiting testing and tuning
# validation_prompt = \
# """
# Answer with yes or no: Does the following text either present and concludes an idea, says something funny, teaches something, presents a conversation that teaches something about one of people involved, presents a funny conversation, presents a conversation where the subject is either law, ethics, merit, or disparity between good and bad, describes something that could've happened, describes an object, describes an ideia, describes a concept, presents an irony as a significant part of it, presents a conversation where an irony is a big part of it, presents a conversation where one or more people challenge another, or presents an incomplete conversation where the missing part can represent a pause or moment of silent of one of the people involved denoting that the latter is going through sad, angry, or joyful thoughts?

# {}
# """

trancription_prompt = \
"""This audio is from the movie "{}" form the year {}. Try your best to make sure the final transcription is correctly punctuated."""

# If you get too specific in one of the criteria, the ai model will think of all the
# previous ones as equaly specific, so even if the text match one of them, it will say "No."
# because the criteria matched didn't represent an important enough part of the text.
# Here one of such criteria that poisoned the entire prompt: "... , or presents a 
# conversation where the subject is either law, ethics, merit, or disparity between 
# good and bad".
# Other (better) chat ai models, may overcome this, just like chatgpt does, but they
# cost more, and thats a killer con for me right now. 
validation_prompt = \
"""The text starting on the next paragraph on was extracted from a {} clip of the movie "{}" from the year {}. Tell me with Yes or No if it presents one or more of these characteristics: presents and concludes an idea, says something funny, teaches something, presents a conversation that teaches something about one of people involved, presents a funny conversation, describes something that could've happened, describes an object, describes an ideia, describes a concept, or presents a funny irony.

{}"""

justify_your_answer_prompt = \
"""Tell me why that text complied with the criteria that I presented."""

# Although I tell the AI to give only the code, it still, sometimes, can
# answer with more, unrelated, text. To solve this, detect the json code
# with regex instead of parsing the whole string.
write_title_json_prompt = \
"""Based on what you just told me, write a title with 20 characters at maximum and hashtags for a video . The hashtags must: contain only lower case characters, be a single word each, and make use of only the must known words among the average person. Pick an integer number between and including 2 and 4, then write an amount of hashtags equal to the number you picked.

Answer me in JSON code, but make it fit on one line by minifying it, then answer me with only this line, nothing more. The title must be a string, and the hashtags an array of strings."""

# Regex to find the json code provided by the ai model (a minified json string).
# {"title": "something", "hashtags": ["some", "thing", "yeah", "iknow"]}
# Check respective prompt.
json_title_data_regex = """\{"title": ?".+", ?"hashtags": ?\[".+"(, ?".+"){1,3}\]\}"""

def gen_validation_prompt(transcription: str, media_name: str, media_year: int, duration: int) -> str:
    if not isinstance(transcription, str) \
        and isinstance(media_name, str)   \
        and isinstance(media_year, int)   \
        and isinstance(duration, int):
        raise TypeError("One of the provided arguments is of incorrect type.")
    
    duration_str = "1 minute" if duration == 60 else f"{duration} seconds"

    return validation_prompt.format(
        duration_str, media_name, media_year, transcription
    )

def gen_transcription_prompt(media_name: str, media_year: int) -> str:
    if not isinstance(media_name, str) and isinstance(media_year, int):
        raise TypeError("Provided media information is of incorrect type.")
    
    return trancription_prompt.format(media_name, media_year)
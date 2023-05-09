import openai
from os.path import dirname, abspath, join
from json import load

def config_openai() -> None:
    config_path = abspath(join(dirname(__file__), "..", "config", "openai.json"))
    config = load(open(config_path, "rb"))

    openai.organization = config["organization"]
    openai.api_key = config["apiKey"]
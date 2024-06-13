from starlette.config import Config

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

OPENAI_API_KEY = config("OPENAI_API_KEY" , cast=str) 
from starlette.config import Config

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

OPENAI_API_KEY = config("OPENAI_API_KEY" , cast=str) 

DATA_BASE_URL = config("DATA_BASE_URL" , cast=str)
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config/secrets.env")

def get_secret(key: str) -> str:
    return os.getenv(key)

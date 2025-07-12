import jwt
import time
import httpx
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config/secrets.env")

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def generate_jwt():
    with open(PRIVATE_KEY_PATH, "r") as key_file:
        private_key = key_file.read()

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": GITHUB_APP_ID
    }

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt

async def get_installation_token(installation_id):
    jwt_token = generate_jwt()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers)
        resp.raise_for_status()
        return resp.json()["token"]

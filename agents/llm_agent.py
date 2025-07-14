import os
import httpx
import asyncio
import json
import time
import logging
from collections import defaultdict
from dotenv import load_dotenv

# Load secrets
load_dotenv("config/secrets.env")

# Config from env
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", 60))
OLLAMA_RETRY_DELAY = int(os.getenv("OLLAMA_RETRY_DELAY", 3))
MAX_ATTEMPTS = int(os.getenv("OLLAMA_MAX_ATTEMPTS", 5))

# Setup logs
LOG_DIR = os.getenv("LOG_FOLDER", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "llm_agent.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Prompt to trigger retry on invalid output
REPAIR_PROMPT = """
The JSON you returned could not be parsed.
Please reformat your output to **only** return a valid JSON array of violations, conforming strictly to the schema below:

[
  {
    "filename": "<string>",
    "line": <integer>,           // Line number in source file
    "issue": "<short description, ≤150 characters>",
    "recommendation": "<fix suggestion, ≤150 characters>",
    "severity": <integer 1–10>   // 10 = critical
  },
  ...
]

Do NOT include:
- Any prose or commentary
- Markdown formatting (no backticks, code blocks, headings)
- Extra keys or explanations

If there are no violations, return: `[]` (an empty array)

You must re-analyze the file from scratch and return **only** the JSON array.
Be strict and structured.
"""

async def query_ollama_async(prompt: str) -> str | None:
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{OLLAMA_URL.rstrip('/')}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip() or None
            else:
                return None
        except Exception as e:
            return None


async def get_llm_response_async(prompt: str, filename: str = "unknown") -> str:
    attempt = 1
    full_prompt = prompt
    failure_reasons = defaultdict(int)

    print(f"Starting review for {filename}")
    logging.info(f"Starting LLM review for {filename}")

    while attempt <= MAX_ATTEMPTS:
        print(f"{filename} attempt {attempt}")
        logging.info(f"{filename} attempt {attempt} with model {OLLAMA_MODEL}")

        result = await query_ollama_async(full_prompt)

        if result:
            try:
                parsed = json.loads(result)
                if isinstance(parsed, list):
                    print(f"{filename} - valid JSON received at attempt {attempt}")
                    logging.info(f"{filename} valid JSON received at attempt {attempt}")
                    if attempt > 1:
                        for reason, count in failure_reasons.items():
                            logging.info(f"{filename} had {count} earlier failure(s) due to: {reason}")
                    return result
                else:
                    reason = "Non-list JSON structure"
                    failure_reasons[reason] += 1
                    logging.warning(f"{filename} response not a list")
            except json.JSONDecodeError as e:
                reason = f"JSONDecodeError: {str(e).splitlines()[0]}"
                failure_reasons[reason] += 1
                logging.warning(f"{filename} JSON decode error: {reason}")
                full_prompt = prompt + "\n" + REPAIR_PROMPT
        else:
            reason = "No response or HTTP error"
            failure_reasons[reason] += 1
            logging.warning(f"{filename} no response from Ollama")

        print(f"Retrying {filename} in {OLLAMA_RETRY_DELAY} seconds...")
        await asyncio.sleep(OLLAMA_RETRY_DELAY)
        attempt += 1

    print(f"{filename} failed after {MAX_ATTEMPTS} attempts")
    logging.critical(f"{filename} all {MAX_ATTEMPTS} attempts failed")
    for reason, count in failure_reasons.items():
        logging.critical(f"{filename} {count} failure(s): {reason}")

    return json.dumps([{
        "filename": filename,
        "line": 0,
        "issue": "LLM failed to return valid JSON after retries",
        "recommendation": "Check model output, prompt size, or formatting",
        "severity": 10
    }])

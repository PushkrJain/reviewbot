import os
import json
import re
import subprocess
import cohere
from config.secrets import get_secret

# API Keys
COHERE_API_KEY = get_secret("COHERE_API_KEY")
cohere_client = cohere.Client(COHERE_API_KEY)

# Supported extensions
EXTENSION_LANG_MAP = {
    ".java": "java",
    ".py": "python",
    ".js": "javascript",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".ts": "typescript"
}

SYSTEM_PROMPT = """
You are a senior software engineer at a top-tier product company like Google or NVIDIA. 
Your job is to perform a strict and thorough code review on the provided source code. 

Identify *any* issues that could arise in professional, large-scale codebases, including but not limited to:

- Poor naming conventions or unclear method/variable names
- Unused or dead code
- Poor structure, logic, or unclear flow
- Missing documentation or comments where needed
- Redundant or repeated logic
- Misuse of language-specific constructs (e.g., Pythonic/Java idioms)
- Security, performance, and maintainability risks
- Violations of best practices — even if not explicitly listed

Use your experience and judgment to flag potential problems like a human would.

📦 Return only a **strict JSON array** like this (NO explanation outside JSON):

[
  {
    "filename": "FileName.ext",
    "line": 12,
    "issue": "Method name 'doStuff' is vague and doesn’t reflect the functionality.",
    "recommendation": "Rename method to 'processInputData'.",
    "severity": 6
  }
]

Severity must be a number from 1 (low) to 10 (high).
Do NOT add comments, headings, explanations, or markdown — only return the JSON.
"""


def detect_language_from_filename(filename: str) -> str:
    for ext, lang in EXTENSION_LANG_MAP.items():
        if filename.endswith(ext):
            return lang
    return "unknown"

def call_ollama(prompt: str) -> str:
    try:
        print("Using Ollama LLM for violation detection...")
        result = subprocess.run(
            [
                "curl", "-s", "http://localhost:11434/api/generate",
                "-d", json.dumps({
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                })
            ],
            capture_output=True,
            text=True
        )
        raw = json.loads(result.stdout)
        return raw.get("response", "")
    except Exception as e:
        print("Ollama failed:", e)
        return None

def call_cohere(prompt: str) -> str:
    try:
        print("Falling back to Cohere...")
        response = cohere_client.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.3
        )
        return response.text.strip()
    except Exception as e:
        print("Cohere failed:", e)
        return ""

def get_violations_from_llm(code: str, filename: str) -> list:
    language = detect_language_from_filename(filename)

    full_prompt = f"""
{SYSTEM_PROMPT}

Filename: {filename}

```{language}
{code}
"""

    raw_response = call_ollama(full_prompt)

    if not raw_response:
        raw_response = call_cohere(full_prompt)
    # print("🔍 Raw LLM Response:\n", raw_response)
    return parse_response(raw_response)

def parse_response(raw_response: str) -> list:
    import json, re
    try:
        # Try parsing directly first
        if isinstance(raw_response, list):
            data = raw_response
        elif raw_response.strip().startswith('['):
            data = json.loads(raw_response.strip())
        else:
            match = re.search(r'\[\s*{.*?}\s*.*?\]', raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                print("No valid JSON array found in response.")
                return []

        # Sort by line number and normalize fields
        sorted_data = sorted(data, key=lambda x: x.get("line", 0))
        for v in sorted_data:
            v.setdefault("filename", "UnknownFile")
            v.setdefault("line", 0)
            v.setdefault("issue", v.get("description", ""))
            v.setdefault("recommendation", "No recommendation provided.")
            v.setdefault("severity", 5)

        return sorted_data

    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
        return []


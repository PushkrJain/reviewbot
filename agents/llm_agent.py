import os
import cohere
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# Load secrets
load_dotenv("config/secrets.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")  # default port

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
cohere_client = cohere.Client(COHERE_API_KEY)

# 🔹 Primary: Ollama (Local)
def query_ollama(prompt):
    try:
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        response = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print("❌ Ollama Error:", response.text)
            return None
    except Exception as e:
        print("❌ Ollama Exception:", e)
        return None

# 🔸 Secondary: Cohere
def query_cohere(prompt):
    try:
        response = cohere_client.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.3
        )
        return response.text.strip()
    except Exception as e:
        print("⚠️ Cohere failed:", e)
        return None

# 🔻 Tertiary: OpenAI
def query_openai(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ OpenAI failed:", e)
        return None

# 🚀 Entry Point
def get_llm_response(prompt):
    print("🔹 Trying Ollama (local llama3)...")
    result = query_ollama(prompt)
    if result:
        return result

    print("🔸 Falling back to Cohere...")
    result = query_cohere(prompt)
    if result:
        return result

    print("🔻 Final fallback to OpenAI...")
    result = query_openai(prompt)
    return result or "❌ All LLMs failed. Please check connectivity or quota."

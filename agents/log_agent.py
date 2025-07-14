import os
import json
from datetime import datetime

LOG_FILE = "logs/ollama_log.json"
os.makedirs("logs", exist_ok=True)

def load_logs():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_logs(log_data):
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)

def log_attempt(prompt, status, error=None):
    logs = load_logs()
    prompt_key = prompt.strip()[:80]  # Avoid log bloat

    if prompt_key not in logs:
        logs[prompt_key] = {
            "attempts": [],
            "fail_counts": {},
            "success_count": 0
        }

    timestamp = datetime.utcnow().isoformat()
    entry = {"timestamp": timestamp, "status": status}

    if status == "failure" and error:
        error = str(error)
        logs[prompt_key]["fail_counts"][error] = logs[prompt_key]["fail_counts"].get(error, 0) + 1
        entry["error"] = error

    if status == "success":
        logs[prompt_key]["success_count"] += 1

    logs[prompt_key]["attempts"].append(entry)
    save_logs(logs)

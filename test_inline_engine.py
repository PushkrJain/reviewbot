import os
import time
import asyncio
from agents.rule_engine_agent import get_violations_from_llm, format_review_report
from dotenv import load_dotenv

load_dotenv("config/secrets.env")

TEST_FOLDER = os.getenv("TEST_FOLDER", "tests")
REPORTS_FOLDER = os.path.join(TEST_FOLDER, "reports")

EXTENSION_LANG_MAP = {
    ext.strip(): lang.strip()
    for ext, lang in (item.split(":") for item in os.getenv("EXTENSION_LANG_MAP", ".java:java,.py:python").split(","))
}


def detect_language(filename: str) -> str:
    for ext, lang in EXTENSION_LANG_MAP.items():
        if filename.endswith(ext):
            return lang
    return "unknown"


async def review_file(file_path: str):
    fname = os.path.basename(file_path)

    if not os.path.isfile(file_path) or fname.startswith(".") or fname == "test_inline_engine.py":
        return None

    language = detect_language(fname)
    if language == "unknown":
        return f"Skipping unsupported file: {fname}"

    with open(file_path, "r") as f:
        code = f.read()

    start = time.time()
    review = await get_violations_from_llm(code, filename=fname)
    formatted = format_review_report(review)
    duration = time.time() - start

    print(f"\nCode Review Report for {fname}")
    print(f"Completed in {duration:.2f} seconds\n")
    print(formatted)

    safe_name = file_path.replace("/", "_").replace("\\", "_")
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    report_path = os.path.join(REPORTS_FOLDER, f"{safe_name}_review.md")
    with open(report_path, "w") as f:
        f.write(formatted)

    return f"✅ {fname} reviewed in {duration:.2f} seconds"


async def run_inline_review_on_tests():
    print("Running AutoReviewBot Inline Review...\n")

    start_all = time.time()
    all_files = []

    for dirpath, _, filenames in os.walk(TEST_FOLDER):
        for fname in filenames:
            full_path = os.path.join(dirpath, fname)
            if os.path.isfile(full_path):
                all_files.append(full_path)

    review_tasks = [review_file(file_path) for file_path in all_files]
    results = await asyncio.gather(*review_tasks)

    reviewed = sum(1 for r in results if r and r.startswith("✅"))
    total_time = time.time() - start_all

    print(f"\nReview completed for {reviewed} file(s).")
    print(f"Total time taken: {total_time:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(run_inline_review_on_tests())

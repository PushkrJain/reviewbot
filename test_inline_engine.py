# test_inline_engine.py

import os
from agents.rule_engine_agent import get_violations_from_llm
from agents.inline_comment_agent import annotate_file_with_comments

TEST_FOLDER = "tests"
ANNOTATED_FOLDER = os.path.join(TEST_FOLDER, "annotated")

def detect_language(filename):
    if filename.endswith(".java"):
        return "java"
    elif filename.endswith(".py"):
        return "python"
    else:
        return "unknown"

def run_inline_review_on_tests():
    print("Running AutoReviewBot Inline Review on Test Files...")

    for fname in os.listdir(TEST_FOLDER):
        file_path = os.path.join(TEST_FOLDER, fname)

        if not os.path.isfile(file_path):
            continue
        if fname.startswith(".") or fname == "test_inline_agent.py":
            continue

        # Detect language from extension
        language = detect_language(fname)
        if language == "unknown":
            print(f"Skipping unsupported file: {fname}")
            continue

        # Read code
        with open(file_path, "r") as f:
            code = f.read()

        # Get violations
        violations = get_violations_from_llm(code, filename=fname)
        if not violations:
            print(f"No violations found in {fname}")
            continue

        # Print Report
        print(f"\n Code Review Report for {fname}")
        for idx, v in enumerate(violations, 1):
            print(f"Issue {idx}:")
            print(f"File     : {v['filename']}")
            print(f"Line     : {v['line']}")
            print(f"Issue    : {v['issue']}")
            print(f"Fix      : {v['recommendation']}")
            print(f"Severity : {v['severity']}")
            print("-" * 50)

        # Generate annotated file
        annotate_file_with_comments(file_path, violations, output_dir=ANNOTATED_FOLDER)

if __name__ == "__main__":
    run_inline_review_on_tests()

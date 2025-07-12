# tests/test_rule_engine.py

import sys
import os
from agents.rule_engine_agent import get_violations_from_llm

SUPPORTED_EXTENSIONS = {".java", ".py"}  # Extend this list as needed

def run_file_test(path):
    with open(path, "r") as f:
        code = f.read()
    filename = os.path.basename(path)
    return get_violations_from_llm(code, filename)

def collect_code_files(folder="tests"):
    all_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1] in SUPPORTED_EXTENSIONS:
                all_files.append(os.path.join(root, file))
    return all_files

def print_report(violations):
    print("\n📋 AutoReviewBot - Code Review Report\n")
    for idx, v in enumerate(violations, 1):
        print(f"Issue {idx}:")
        print(f"  📄 File     : {v['filename']}")
        print(f"  🔢 Line     : {v['line']}")
        print(f"  ⚠️  Issue    : {v['issue']}")
        print(f"  🛠️  Fix      : {v['recommendation']}")
        print(f"  🚨 Severity : {v['severity']}")
        print("-" * 50)

if __name__ == "__main__":
    violations = []

    for path in collect_code_files("tests"):
        print(f"🔍 Analyzing {path} ...")
        violations.extend(run_file_test(path))

    print_report(violations)

import os

def insert_inline_comments(code: str, violations: list, filename: str) -> str:
    """
    Inserts inline suggestions directly above the affected lines of code.
    Each comment includes the issue description and a fix recommendation.
    """
    code_lines = code.splitlines()
    annotated_lines = []
    
    # Create a map from line number to all violations at that line
    violation_map = {}
    for v in violations:
        line = v.get("line", 0)
        if line not in violation_map:
            violation_map[line] = []
        violation_map[line].append(v)

    # Use comment syntax based on file type
    comment_prefix = "# " if filename.endswith(".py") else "// "

    for i, line in enumerate(code_lines, start=1):
        if i in violation_map:
            for v in violation_map[i]:
                issue = v.get('issue', 'No issue description provided.').strip()
                fix = v.get('recommendation', 'Consider refactoring.').strip()
                severity = v.get('severity', 5)
                
                annotated_lines.append(f"{comment_prefix} 🚩 Recommendation (Severity {severity}): {issue}")
                annotated_lines.append(f"{comment_prefix} 💡 {fix}")
        annotated_lines.append(line)

    return "\n".join(annotated_lines)


def annotate_file_with_comments(file_path: str, violations: list, output_dir: str = "tests/annotated") -> str:
    """
    Annotates a code file with inline comments and saves the result to output_dir.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(file_path, 'r') as f:
        code = f.read()

    filename = os.path.basename(file_path)
    annotated_code = insert_inline_comments(code, violations, filename)
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w') as f:
        f.write(annotated_code)

    print(f"✅ Annotated file saved to: {output_path}")
    return output_path

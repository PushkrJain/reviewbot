import os

def insert_inline_comments(code: str, violations: list, filename: str) -> str:
    """
    Inserts inline suggestions above the affected lines.
    """
    code_lines = code.splitlines()
    annotated_lines = []
    line_offset = 0
    
    # Group violations by line number
    violation_map = {v['line']: [] for v in violations}
    for v in violations:
        violation_map[v['line']].append(v)

    comment_prefix = "# " if filename.endswith(".py") else "// "
    
    for i, line in enumerate(code_lines, 1):
        # Inject comments before the current line if any violations exist
        if i in violation_map:
            for v in violation_map[i]:
                fix = v.get('recommendation', 'Consider refactoring.')
                severity = v.get('severity', 5)
                annotated_lines.append(f"{comment_prefix} Recommendation (Severity {severity}): {v['issue']}")
                annotated_lines.append(f"{comment_prefix} {fix}")
        annotated_lines.append(line)
    
    return "\n".join(annotated_lines)

def annotate_file_with_comments(file_path: str, violations: list, output_dir: str = "tests/annotated") -> str:
    """
    Reads a file, adds inline comments for violations, writes to output_dir.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(file_path, 'r') as f:
        code = f.read()
    
    filename = os.path.basename(file_path)
    commented_code = insert_inline_comments(code, violations,filename)
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w') as f:
        f.write(commented_code)

    print(f"Annotated file saved to: {output_path}")
    return output_path

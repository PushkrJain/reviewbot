#  Recommendation (Severity 8): File name 'tests/sample.py' suggests this is a test file, but it contains non-test code. Consider renaming or moving.
#  
# tests/sample.py

#  Recommendation (Severity 4): Unused variable 'y'.
#  Remove or use the variable.
def DoStuff():
    x = 5
#  Recommendation (Severity 6): Unreachable code. The function always returns without executing this logic.
#  Remove dead code.
    y = 10
    # unnecessary logic
    return
#  Recommendation (Severity 5): Unused function 'unused'.
#  Remove or refactor to use the function.

def unused():
    pass
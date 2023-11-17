def prepare_prompt(issue):
    return f"""
    Task: Review the identified issue in the provided Java class and provide the corrected Java class code.
    Focus only on the class code; do not include any comments or explanations.

    Issue Details:
    - Rule: {issue['rule']}
    - Component: {issue['component']}
    - Location: Check around Line {issue['line']} or the related area in the file.
    - Message: {issue['message']}
    - Effort: {issue['effort']}
    - Issue Type: {issue['type']}

    Return: Only the corrected Java class code.
    """

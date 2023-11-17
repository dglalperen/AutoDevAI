def prepare_prompt(issue):
    return f"""
    Task: Correct the identified issue in the provided Java class
        and return the corrected class in its entirety.

    Issue Details:
    - Rule: {issue['rule']}
    - Component: {issue['component']}
    - Location: Line {issue['line']} (Start offset: {issue['textRange']['startOffset']}, End offset: {issue['textRange']['endOffset']})
    - Message: {issue['message']}
    - Effort: {issue['effort']}
    - Issue Type: {issue['type']}

    Please return the corrected Java class.
    """
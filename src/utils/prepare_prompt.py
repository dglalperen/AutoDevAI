def prepare_prompt(issue_group_key, example_issue):
    parts = issue_group_key.split(':', 1)

    # Handling cases where 'line' key might not be present
    line_info = f"Around Line {example_issue['line']}" if 'line' in example_issue else "Check the file in general"

    prompt = f"""
    System message: You are a Java programming master. Generate the corrected Java code based on the specified rule and present it in JSON format.

    Task: Correct the identified issue in the provided Java class
        and return the corrected class in its entirety.

    Issue Details:
    - Rule: {example_issue['rule']}
    - Component: {example_issue['component']}
    - Location: {line_info} and generally the file {example_issue['component']}
    - Message: {example_issue['message']}
    - Issue Type: {example_issue['type']}

    Return: The corrected Java class code formatted as a JSON string. The structure should be:
    {{
        "result": "<corrected Java class code here>"
    }}

    """
    print(f"DEBUG: Prompt: {prompt}")
    return prompt

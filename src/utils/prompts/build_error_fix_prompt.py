def build_error_fix_prompt(error_message):

    prompt = f"""
    System message: You are a Java programming expert. Correct the issue in the Java code that caused the build error and provide the corrected code.

    Build Error Details:
    - Error Message: {error_message}

    Task: Analyze the error and provide the corrected Java code to fix this build error. Ensure the solution addresses the specific issue mentioned in the error message and relates to the file at the given path.

    Return: The corrected Java class code formatted as a JSON string. The structure should be:
    {{
        "result": "<corrected Java class code here>"
    }}

    Note: The solution should be directly applicable to fix the error and allow the build to succeed.
    """
    
    print(f"DEBUG: Prompt: {prompt}")
    return prompt
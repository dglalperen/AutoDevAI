from utils.prompts.prepare_prompt import get_file_content

def feedback_loop_prompt(previous_response, issue_group_key, example_issue, rule_details, attempt_number):
    # Extract necessary information from the provided context
    rule_key = issue_group_key.split(':', 1)[0]
    rule_explanation_brief = rule_details.get('rule', {}).get('mdDesc', "No detailed explanation available.")
    original_java_class = get_file_content(example_issue['component'])

    prompt = f"""
        Objective: Evaluate the correctness of the provided refactoring and decide whether a reattempt is necessary.

        Context:
        - Attempt Number: {attempt_number}
        - Issue Summary:
            - Message: '{example_issue["message"]}'
            - Rule Key: '{rule_key}'
            - Detailed Explanation: '{rule_explanation_brief}'
            - Affected File: '{example_issue["component"]}'

        Previous Attempt Output:
        {"-" * 30}
        {previous_response}
        {"-" * 30}

        Instructions:
        1. Analyze the previous attempt output and the original Java class code.
        2. Determine whether the output correctly addresses the SonarQube issue described in the context.
        3. If the output is correct and meets the requirements (properly refactored Java code encapsulated in a JSON object with the key 'updated_java_class'), respond with 'Output is correct'.
        4. If the output is incorrect or incomplete, respond with 'Output is incorrect'.

        Decision:
        - [YOUR RESPONSE HERE]
    """.strip()

    return prompt

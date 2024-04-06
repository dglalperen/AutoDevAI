import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai_api(prompt_text):
    response = openai.Completion.create(
        model="gpt-4-1106-preview",
        prompt=prompt_text,
        max_tokens=150,
        temperature=0.5,
        response_format="json"
    )
    return response

def generate_fix_for_issue(issue_description, java_class_content):
    prompt = f"""
    [Your detailed prompt asking for a fix based on the issue and including the Java class content]
    Make sure to specify that you expect a JSON response containing the updated class.
    """
    response = call_openai_api(prompt)
    print(json.dumps(response, indent=2))  # For debugging

    # Extract the updated class from the JSON response
    updated_class = response['choices'][0]['message']
    return updated_class

if(__name__ == "__main__"):
    issue_description = "This is the actual issue description."
    java_class_content = "public class MyClass {\n    // Class content here\n}"
    updated_class = generate_fix_for_issue(issue_description, java_class_content)
    print(updated_class)
          
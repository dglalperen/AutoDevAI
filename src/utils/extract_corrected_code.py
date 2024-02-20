import json
from pydantic import BaseModel
import re

def unescape_java_code(code):
    """Unescape Java code string extracted from JSON."""
    # Replace escaped newlines and escaped backslashes
    return code.encode().decode('unicode_escape')

def extract_corrected_code_json(response):
    # Improved regex to capture more complex JSON structures
    json_match = re.search(r"```json\s*\n?(\{[\s\S]*?\})\s*```", response)
    if json_match:
        json_string = json_match.group(1)
        try:
            parsed_json = json.loads(json_string)
            corrected_code = parsed_json.get('result', '')
            if corrected_code:
                # Unescape Java code if extracted from JSON
                return unescape_java_code(corrected_code)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # Fall through to try extracting as plain Java code block

    # Try to extract the Java code block if JSON extraction fails
    java_code_match = re.search(r"```java\s*\n([\s\S]*?)\n\s*```", response)
    if java_code_match:
        return java_code_match.group(1)

    # Log if no corrected code was found
    print("No corrected code found in the response.")
    return ''

def extract_corrected_code(parsed_response):
    if parsed_response.result:
        return parsed_response.result

    print("No corrected code found in the response.")
    return ''

def extract_json_from_response(response):
    json_start = response.find('```json') + len('```json')
    json_end = response.find('```', json_start)
    json_part = response[json_start:json_end].strip()

    return json_part

# Mock Pydantic model simulating the actual JavaClassModel
class MockJavaClassModel(BaseModel):
    result: str

# Updated function to work with Pydantic model instance
def extract_corrected_code_from_model(parsed_response: MockJavaClassModel):
    if parsed_response.result:
        return parsed_response.result
    print("No corrected code found in the response.")
    return ''

# Test the updated function
if __name__ == "__main__":
    # Creating a mock instance of the model with sample corrected code
    mock_response = MockJavaClassModel(result="public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}")

    # Extracting corrected code using the updated function
    corrected_code = extract_corrected_code_from_model(mock_response)

    # Print the extracted code
    print(corrected_code)

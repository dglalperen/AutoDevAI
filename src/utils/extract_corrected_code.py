import json
import re

def unescape_java_code(code):
    """Unescape Java code string extracted from JSON."""
    # Replace escaped newlines and escaped backslashes
    return code.encode().decode('unicode_escape')

def extract_corrected_code(response):
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

if __name__ == "__main__":
    response = """
    The rule java:S2699 is a SonarQube rule that requires at least one assertion in each test case.

    ```json
    {
        "result": "package com.CarRentalAgency;\\n\\nimport org.junit.jupiter.api.Test;\\nimport org.springframework.boot.test.context.SpringBootTest;\\nimport static org.junit.jupiter.api.Assertions.assertTrue;\\n\\n@SpringBootTest\\nclass CarRentalAgencyApplicationTests {\\n\\n\\t@Test\\n\\tvoid contextLoads() {\\n\\t\\tassertTrue(true);\\n\\t}\\n\\n}\\n"
    }
    ```
    """
    java_code = extract_corrected_code(response)
    print(java_code)

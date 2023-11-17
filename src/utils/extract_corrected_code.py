import json
import re

def extract_corrected_code(response):
    # Adjusting the regex pattern to account for varying whitespace/newline characters
    json_match = re.search(r"```json\s*\n?(\{.*?\})\n?\s*```", response, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
        try:
            parsed_json = json.loads(json_string)
            corrected_code = parsed_json.get('result', '')
            return corrected_code
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print("No JSON string found in the response.")
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

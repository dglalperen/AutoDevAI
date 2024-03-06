import json
import re

def extract_correctly_updated(response: str) -> bool:
    """
    Extracts the boolean value for "correctly_updated_class" from the given response.

    :param response: The response string from the model, which should include a JSON object.
    :return: A boolean value extracted from the response or None if not found or invalid.
    """
    try:
        response = response.strip()

        try:
            parsed_json = json.loads(response)
            correctly_updated = parsed_json.get('correctly_updated_class')
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if json_match:
                json_string = json_match.group(0).strip()
                parsed_json = json.loads(json_string)
                correctly_updated = parsed_json.get('correctly_updated_class')
            else:
                return None

        if isinstance(correctly_updated, bool):
            return correctly_updated
        else:
            print("Extracted value is not a boolean.")
            return None

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return None

def test_extract_correctly_updated():
    # Test cases
    cases = [
        ('{"correctly_updated_class": true}', True),
        ('{"correctly_updated_class": false}', False),
        ('Some text before {"correctly_updated_class": true} some text after', True),
        ('Incorrect key {"another_key": true}', None),
        ('No boolean value {"correctly_updated_class": "true"}', None),
        ('Invalid JSON {correctly_updated_class: true}', None),
    ]
    
    # Testing loop
    for input_str, expected in cases:
        result = extract_correctly_updated(input_str)
        assert result == expected, f"Failed on '{input_str}': expected {expected}, got {result}"
    
    print("All tests passed!")

def extract_updated_java_class(response):
    """
    Extracts the updated Java class from the OpenAI model's JSON output.

    Parameters:
    - response (str): The raw string output from the OpenAI model.

    Returns:
    - str: The extracted Java class code, or an empty string if not found.
    """
    try:
        # Find the JSON snippet within the response using a regular expression
        json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            
            # Parse the JSON string into a Python dictionary
            parsed_json = json.loads(json_string)

            # Extract the Java class code without relying on a specific key
            # Assuming there's only one piece of Java class code in the JSON
            for value in parsed_json.values():
                if isinstance(value, str) and value.strip().startswith("package "):
                    # Assuming the class code starts with "package"
                    return value.encode().decode('unicode_escape')

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    # If no updated Java class is found or an error occurs, return an empty string
    return ''

if __name__ == "__main__":
    test_extract_correctly_updated()

    simulated_response = """```json
    {"updated_java_class": "public class HelloWorld {\\\\n    public static void main(String[] args) {\\\\n        System.out.println(\\\\\\"Hello, World!\\\\\\");\\\\n    }\\\\n}"}
    ```"""
    
    expected_class = 'public class HelloWorld {\\n    public static void main(String[] args) {\\n        System.out.println("Hello, World!");\\n    }\\n}'

    extracted_class = extract_updated_java_class(simulated_response)
    
    assert extracted_class == expected_class, f"extract_updated_java_class failed: expected {expected_class}, got {extracted_class}"
    print("extract_updated_java_class test passed!")

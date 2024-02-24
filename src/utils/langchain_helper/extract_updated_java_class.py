import json
import re

def extract_updated_java_class(response):
    """
    Extracts the updated Java class from the OpenAI model's JSON output.

    Parameters:
    - response (str): The raw string output from the OpenAI model.

    Returns:
    - str: The extracted and unescaped Java class code, or an empty string if not found.
    """
    try:
        # Find the JSON snippet within the response using a regular expression
        json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            
            # Parse the JSON string into a Python dictionary
            parsed_json = json.loads(json_string)
            
            # Extract the 'updated_java_class' field containing the Java code
            updated_java_class = parsed_json.get('updated_java_class', '')
            if updated_java_class:
                # Unescape Java code to interpret escape sequences like \n, \t, etc.
                return updated_java_class.encode().decode('unicode_escape')

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    # If no updated Java class is found or an error occurs, return an empty string
    return ''

# Example usage
if __name__ == "__main__":
    # Simulated response from the OpenAI model
    simulated_response = """Some introductory text...
    ```json
    {"updated_java_class": "public class HelloWorld {\\n    public static void main(String[] args) {\\n        System.out.println(\\\"Hello, World!\\\");\\n    }\\n}"}
    ```
    Some concluding text..."""

    # Extract the updated Java class from the response
    updated_java_class = extract_updated_java_class(simulated_response)

    # Print the extracted Java class code
    print(updated_java_class)

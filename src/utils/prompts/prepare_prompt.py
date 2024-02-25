import requests
import re
import os

from utils.print_utils.colored_print import print_red, print_yellow

def fetch_rule_details(rule_key):
    try:
        response = requests.get(f"http://localhost:3000/rules?key={rule_key}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch rule details: {response.status_code}")
    except Exception as e:
        print(f"Error fetching rule details: {e}")
    return None

def get_file_content(component_key):
    project_name, file_path = component_key.split(':', 1)

    # Dynamically find the script's current directory
    current_script_dir = os.path.dirname(os.path.realpath(__file__))

    base_dir = os.path.abspath(os.path.join(current_script_dir, os.pardir, os.pardir, os.pardir, 'Repos', project_name))

    full_path = os.path.join(base_dir, file_path)

    try:
        with open(full_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return str(e)


def setup_prompt(issue_group_key, example_issue, rule_details):
    # Split the issue group key to extract the rule key
    rule_key = issue_group_key.split(':', 1)[0]

    # Rule explanation from Markdown description or a default message
    rule_explanation_md = rule_details.get('rule', {}).get('mdDesc', "No additional rule details available.")

    # Simplify rule explanation to its key parts
    rule_explanation_brief = extract_relevant_parts(rule_explanation_md)
    original_java_class = get_file_content(example_issue['component'])

    # Determine the specific line or general file area for the update
    line_info = f"Around Line {example_issue['line']}" if 'line' in example_issue else "Check the file in general"
    
    prompt = f"""
        Objective: Refactor the provided Java class to address a specific SonarQube issue, ensuring adherence to best practices and maintaining the integrity of the original functionality.

        Issue Summary:
        - Message: '{example_issue["message"]}'
        - Rule Key: '{rule_key}'
        - Detailed Explanation: '{rule_explanation_brief}'
        - Affected File: '{example_issue["component"]}'

        Java Class to Refactor:
        {"-" * 30}
        {original_java_class}
        {"-" * 30}

        Instructions:
        1. Review the issue summary and the provided Java class code.
        2. Make the necessary changes to the Java class to resolve the SonarQube issue.
        3. **Crucially**, return the refactored Java class code formatted as a JSON object with the key 'updated_java_class'. The entire class code must be included without any omissions or abbreviations.

        Positive Example:
        - Issue: Define a constant instead of duplicating this literal 'example' multiple times.
        - Original Class Snippet: 
            public void exampleMethod() {{
                System.out.println("example");  // Noncompliant
                System.out.println("example");  // Noncompliant
            }}

        Example of Expected Output:
        {{
        "updated_java_class": "public class ExampleClass {{\\n    private static final String EXAMPLE_CONSTANT = \\"example\\";\\n    public void exampleMethod() {{\\n        System.out.println(EXAMPLE_CONSTANT);\\n        System.out.println(EXAMPLE_CONSTANT);\\n    }}\\n}}"
        }}

        Negative Examples to Avoid:
        1. Omitting Original Elements: Ensure that all original elements, including necessary imports and class-level annotations, are retained in the updated class.
        2. Avoiding Shortenings: Do not shorten methods or variables, e.g., 'exMethod' instead of 'exampleMethod', as this can alter the intended functionality or readability of the class.

        Important: The response must consist solely of the updated Java class code in the specified JSON format. Any deviation from these instructions, including missing the JSON structure or omitting parts of the class, will result in an unsuccessful task completion.
""".strip()
    
    return prompt

def extract_relevant_parts(md_description):
    # Updated patterns for the start of sections
    patterns = {
        'why_issue': re.compile(r"<h2>Why is this an issue\?</h2>", re.IGNORECASE),
        'exceptions': re.compile(r"<h3>Exceptions</h3>", re.IGNORECASE),
        'how_to_fix_it': re.compile(r"<h2>How to fix it</h2>", re.IGNORECASE),
        'code_examples': re.compile(r"<h3>Code examples</h3>", re.IGNORECASE)
    }

    # Initialize variables to hold extracted text
    extracted_texts = {key: "" for key in patterns}

    # Split the Markdown content into lines for processing
    lines = md_description.split('\n')

    # Variable to track the current section being extracted
    current_section = None

    # Iterate through each line in the Markdown description
    for line in lines:
        # Check if current line is the start of a new section
        for section, pattern in patterns.items():
            if pattern.match(line):
                current_section = section
                break

        # Append the line to the appropriate section text if that section is being extracted
        if current_section:
            extracted_texts[current_section] += line + '\n'

    # Removing HTML tags from each extracted section
    for section in extracted_texts:
        extracted_texts[section] = remove_html_tags(extracted_texts[section])

    # Combine the extracted sections into a single string without HTML tags
    extracted_text = "\n".join(extracted_texts.values())

    return extracted_text

def remove_html_tags(text):
    """ Remove html tags from a string """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def test_get_file_content():
    component_key = "expense-tracker-api:src/main/java/com/pairlearning/expensetracker/resources/CategoryResource.java"
    file_content = get_file_content(component_key)
    print(file_content)
    
if __name__ == "__main__":
    # Fetch rule details
    #rule_details = fetch_rule_details("java:S1192")

    # Prepare the prompt using the 'prepare_prompt2' function
    # prompt = setup_prompt("java:S1192:src/main/java/com/rentalcar/agency/CarRentalAgency.java", {
    #     "key": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java:java:S1192",
    #     "rule": "java:S1192",
    #     "severity": "MAJOR",
    #     "component": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java",
    #     "line": 13,
    #     "message": "String literals should not be duplicated",
    #     "type": "CODE_SMELL"
    #     }, rule_details)
    # Print the prepared prompt
    #print(prompt)

    # For testing purposes, you might want to simulate an AI response here
    # Example AI response (modify as needed for your tests)
    #simulated_ai_response = "format_code_as_json(java_code=\"public class HelloWorld {\\n    public static void main(String[] args) {\\n        System.out.println(\\\"Hello World!\\\");\\n    }\\n}\")"

    # Handle the AI response
    #formatted_output = handle_ai_response(simulated_ai_response)

    # Print the formatted output to check if it is correct
    #print(formatted_output)
    test_get_file_content()

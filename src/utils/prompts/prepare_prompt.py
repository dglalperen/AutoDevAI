import requests
import re
import os
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


def print_yellow(text):
    print("\x1b[33m{}\x1b[0m".format(text))


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
    project_name, file_path = component_key.split(":", 1)

    # Dynamically find the script's current directory
    current_script_dir = os.path.dirname(os.path.realpath(__file__))

    base_dir = os.path.abspath(
        os.path.join(
            current_script_dir, os.pardir, os.pardir, os.pardir, "Repos", project_name
        )
    )

    full_path = os.path.join(base_dir, file_path)

    try:
        with open(full_path, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return str(e)


def setup_format_instructions():
    response_schemas = [
        ResponseSchema(
            name="updated_java_class",
            description="The updated Java class code, encapsulated in a JSON object.",
        )
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    format_instructions = output_parser.get_format_instructions()

    return format_instructions


def extract_java_class_name(path):
    """
    Extracts the Java class name from a full path or partial path string.

    Parameters:
    - path (str): The full or partial path to the Java class file.

    Returns:
    - str: The extracted Java class name.
    """
    # Split the path by "/" to get segments, then take the last segment
    last_segment = path.split("/")[-1]
    # Remove the ".java" extension and return the class name
    class_name = last_segment.replace(".java", "")
    return class_name


def setup_prompt(issue_group_key, example_issue, rule_details):
    # Extract the rule key and simplify the rule explanation
    rule_key = issue_group_key.split(":")[1]
    rule_explanation_brief = extract_relevant_parts(
        rule_details.get("rule", {}).get(
            "mdDesc", "No detailed rule explanation available."
        )
    )

    original_java_class = get_file_content(example_issue["component"])

    # Construct the prompt with clear instructions for the model
    prompt = f"""
    As a Java expert, you're reviewing a Java class that violates certain
    coding principles according to SonarQube analysis.
    Below is the Java class with identified issues. 

    Correct the specific issue described
    and return the entire Java class as is,
    with the necessary modifications made directly in the code.
    The expectation is for the modified class to be fully functional
    and adhere to best coding practices, addressing the SonarQube issue highlighted.

    This is the current state of the Java class "{extract_java_class_name(example_issue["component"])}"
    and the sonarqube issue:
    "{original_java_class}"
    
    The sonarqube issue is as follows:
    "{example_issue["message"]}"

    Return the corrected Java class in the following JSON format:
    ```json
    {{
        "updated_java_class": "/* The updated Java class code */"
    }}
    ```

    Ensure the entire class is returned with the issue corrected, without using placeholders like 'rest of the class code remains unchanged'. The class should be directly usable without further modifications.
    """

    print_yellow("DEBUG: Prompt:")
    print_yellow(prompt)
    return prompt


def extract_relevant_parts(md_description):
    # Updated patterns for the start of sections
    patterns = {
        "why_issue": re.compile(r"<h2>Why is this an issue\?</h2>", re.IGNORECASE),
        "exceptions": re.compile(r"<h3>Exceptions</h3>", re.IGNORECASE),
        "how_to_fix_it": re.compile(r"<h2>How to fix it</h2>", re.IGNORECASE),
        "code_examples": re.compile(r"<h3>Code examples</h3>", re.IGNORECASE),
    }

    # Initialize variables to hold extracted text
    extracted_texts = {key: "" for key in patterns}

    # Split the Markdown content into lines for processing
    lines = md_description.split("\n")

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
            extracted_texts[current_section] += line + "\n"

    # Removing HTML tags from each extracted section
    for section in extracted_texts:
        extracted_texts[section] = remove_html_tags(extracted_texts[section])

    # Combine the extracted sections into a single string without HTML tags
    extracted_text = "\n".join(extracted_texts.values())

    return extracted_text


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def test_get_file_content():
    component_key = "expense-tracker-api:src/main/java/com/pairlearning/expensetracker/resources/CategoryResource.java"
    file_content = get_file_content(component_key)
    print(file_content)


if __name__ == "__main__":
    # Fetch rule details
    rule_details = fetch_rule_details("java:S1192")

    # Prepare the prompt using the 'prepare_prompt2' function
    prompt = setup_prompt(
        "java:S1192:src/main/java/com/rentalcar/agency/CarRentalAgency.java",
        {
            "key": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java:java:S1192",
            "rule": "java:S1192",
            "severity": "MAJOR",
            "component": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java",
            "line": 13,
            "message": "String literals should not be duplicated",
            "type": "CODE_SMELL",
        },
        rule_details,
    )
    # Print the prepared prompt
    print(prompt)

    # For testing purposes, you might want to simulate an AI response here
    # Example AI response (modify as needed for your tests)
    # simulated_ai_response = "format_code_as_json(java_code=\"public class HelloWorld {\\n    public static void main(String[] args) {\\n        System.out.println(\\\"Hello World!\\\");\\n    }\\n}\")"

    # Handle the AI response
    # formatted_output = handle_ai_response(simulated_ai_response)

    # Print the formatted output to check if it is correct
    # print(formatted_output)

    # test_get_file_content()

    # setup_format_instructions()

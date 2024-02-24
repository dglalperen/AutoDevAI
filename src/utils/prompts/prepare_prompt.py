import requests
import re
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

class JavaClassModel(BaseModel):
    result: str = Field(description="The fully updated Java class without any shortenings or explanatory comments.")
    
def setup_json_output_parser():
    """
    Set up the output parser for the QA retriever.
    """
    jsonOutputParser = JsonOutputParser(pydantic_object=JavaClassModel)
    format_instructions = jsonOutputParser.get_format_instructions()
    
    return format_instructions
 
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

def setup_prompt(issue_group_key, example_issue, rule_details):
    # Split the issue group key to extract the rule key
    rule_key = issue_group_key.split(':', 1)[0]

    # Setup for JSON output parsing instructions
    format_instructions = setup_json_output_parser()

    # Rule explanation from Markdown description or a default message
    rule_explanation_md = rule_details.get('rule', {}).get('mdDesc', "No additional rule details available.")

    # Simplify rule explanation to its key parts
    rule_explanation_brief = extract_relevant_parts(rule_explanation_md)

    # Determine the specific line or general file area for the update
    line_info = f"Around Line {example_issue['line']}" if 'line' in example_issue else "Check the file in general"

    # Construct the task prompt with structured information
    prompt_test = f"""
    **Task**: Update a Java class to address the specified SonarQube rule violation. Provide the complete updated class. Avoid partial code or explanatory comments.

    **Issue Details**:
    - **Rule**: {example_issue['rule']} (Severity: {rule_details['rule']['severity']})
    - **Brief Explanation**: {rule_explanation_brief}
    - **Target File/Component**: {example_issue['component']}
    - **Location in File**: {line_info}
    - **Issue Description**: {example_issue['message']}
    - **Issue Type**: {example_issue['type']}

    **Formatting Instructions**:
    ```{format_instructions}```

    Ensure adherence to the task as described to avoid incorrect outcomes.
    """

    return prompt_test


# def setup_prompt(issue_group_key, example_issue, rule_details):
#     parts = issue_group_key.split(':', 1)
#     rule_key = parts[0]
#     format_instructions = setup_json_output_parser()

#     # Use Markdown description directly
#     rule_explanation_md = rule_details['rule']['mdDesc'] if rule_details else "No additional rule details available."

#     # Extract key parts of the rule explanation
#     rule_explanation_brief = extract_relevant_parts(rule_explanation_md)

#     line_info = f"Around Line {example_issue['line']}" if 'line' in example_issue else "Check the file in general"
    
#     prompt_test = f"""
#     System message: You are tasked with updating a Java class based on the sonar issue being violated.
#     Provide the updated class in full, without any shortenings or explanatory comments.
    
#     Issue Summary:
#     - Rule: {example_issue['rule']} | Severity: {rule_details['rule']['severity']}
#     - Rule Explanation Briefly: {rule_explanation_brief}
#     - File/Component to be updated: {example_issue['component']}
#     - Specific Location of File to be updated: {line_info}
#     - Description: {example_issue['message']}
#     - Type: {example_issue['type']}
    
#     Format instructions for result:
    
#     ```{format_instructions}```
    
#     Do the Task exactly how it is described or you will get a wrong answer.
#     """

#     return prompt_test

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
    
if __name__ == "__main__":
    # Fetch rule details
    rule_details = fetch_rule_details("java:S1192")

    # Prepare the prompt using the 'prepare_prompt2' function
    prompt = setup_prompt("java:S1192:src/main/java/com/rentalcar/agency/CarRentalAgency.java", {
        "key": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java:java:S1192",
        "rule": "java:S1192",
        "severity": "MAJOR",
        "component": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java",
        "line": 13,
        "message": "String literals should not be duplicated",
        "type": "CODE_SMELL"
        }, rule_details)
    # Print the prepared prompt
    #print(prompt)

    # For testing purposes, you might want to simulate an AI response here
    # Example AI response (modify as needed for your tests)
    simulated_ai_response = "format_code_as_json(java_code=\"public class HelloWorld {\\n    public static void main(String[] args) {\\n        System.out.println(\\\"Hello World!\\\");\\n    }\\n}\")"

    # Handle the AI response
    #formatted_output = handle_ai_response(simulated_ai_response)

    # Print the formatted output to check if it is correct
    #print(formatted_output)



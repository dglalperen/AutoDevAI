import requests
import re

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


def prepare_prompt(issue_group_key, example_issue, rule_details):
    parts = issue_group_key.split(':', 1)
    rule_key = parts[0]

    # Use Markdown description directly
    rule_explanation_md = rule_details['rule']['mdDesc'] if rule_details else "No additional rule details available."

    # Extract key parts of the rule explanation
    rule_explanation_brief = extract_relevant_parts(rule_explanation_md)

    line_info = f"Around Line {example_issue['line']}" if 'line' in example_issue else "Check the file in general"

    prompt = f"""
    System message: You are a Java programming master. Use the rule details provided to identify and correct the specific issue in the Java code. Return the corrected code in JSON format.

    Task: Correct the identified issue in the provided Java class
        and return the corrected class in its entirety.

    Issue Details:
    - Rule: {example_issue['rule']} - Severity: {rule_details['rule']['severity']}
    - Impact: {rule_details['rule']['impacts'][0]['softwareQuality']}
    - Explanation: {rule_explanation_brief}
    - Component: {example_issue['component']}
    - Location: {line_info} and generally the file {example_issue['component']}
    - Message: {example_issue['message']}
    - Issue Type: {example_issue['type']}

    Return: The corrected Java class code formatted as a JSON string. The structure should be:
    {{
        "result": "<insert corrected Java class code here>"
    }}

    Note: Ensure the entire Java class code is encapsulated within the JSON structure, using proper JSON string escaping where necessary.
    """

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

if __name__ == "__main__":
    rule_details = fetch_rule_details("java:S1192")
    print(prepare_prompt("java:S1192:src/main/java/com/rentalcar/agency/CarRentalAgency.java", {
        "key": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java:java:S1192",
        "rule": "java:S1192",
        "severity": "MAJOR",
        "component": "dglalperen_Rental-Car-Agency:src/main/java/com/rentalcar/agency/CarRentalAgency.java",
        "line": 13,
        "message": "String literals should not be duplicated",
        "type": "CODE_SMELL"
    }, rule_details))
    



import json
import os
import datetime
from utils.print_utils.colored_print import print_blue

def apply_fix_and_log(issue, fixed_code, repo_path, log_path):
    issue_details = f"Rule: {issue['rule']} - Message: {issue['message']} - Component: {issue['component']}"
    print_blue(f"\nHandling Issue: {issue_details}\n")
    
    if not fixed_code.strip():
        print(f"No valid fix provided for {issue['key']}. Skipping...")
        return

    file_path = os.path.join(repo_path, issue['component'].split(':')[1])
    print(60*"-")
    print_blue(f"Expected file path: {file_path}")
    print(60*"-")

    with open(file_path, 'w') as file:
        file.write(fixed_code)

    log_entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'issue_key': issue['key'],
        'rule': issue['rule'],
        'message': issue['message'],
        'component': issue['component'],
        'fixed_code_summary': fixed_code[:100] + '...' if len(fixed_code) > 100 else fixed_code,
        'file_path': file_path
        }

    with open(log_path, 'a') as log_file:
        json.dump(log_entry, log_file)
        log_file.write('\n')

    print(f"Applied fix for {issue['key']} and logged the resolution.")

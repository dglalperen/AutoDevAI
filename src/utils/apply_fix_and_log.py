import json
import os
import datetime

def apply_fix_and_log(issue, fixed_code, repo_path, log_path):
    """
    Applies the fixed code to the respective file and logs the resolution.

    :param issue: The original issue data.
    :param fixed_code: The corrected code for the file.
    :param repo_path: Path to the local repository.
    :param log_path: Path to store the resolution logs.
    """
    
    print(60*"-")
    print("DEBUG Prompt Response:", fixed_code)
    print(60*"-")
    print("DEBUG Repo Path:", repo_path)
    print(60*"-")
    print("DEBUG Log Path:", log_path)
    # Do not apply changes if fixed_code is empty
    if not fixed_code.strip():
        print(f"No valid fix provided for {issue['key']}. Skipping...")
        return

    # Construct the file path from the issue component and repo path
    file_path = os.path.join(repo_path, issue['component'].split(':')[1])

    # Write the fixed code to the file
    with open(file_path, 'w') as file:
        file.write(fixed_code)

    # Log the resolution
    resolution = {
        'issue_key': issue['key'],
        'original_issue': issue,
        'fixed_code': fixed_code,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(log_path, 'a') as log_file:
        json.dump(resolution, log_file)
        log_file.write('\n')

    print(f"Applied fix for {issue['key']} and logged the resolution.")
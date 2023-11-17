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
    # Construct the file path from the issue component and repo path
    file_path = os.path.join(repo_path, issue['component'].split(':')[1])

    # Backup original file (optional)
    # os.rename(file_path, file_path + ".backup")

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

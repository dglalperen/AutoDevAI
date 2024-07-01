import json
import os
import datetime
from utils.print_utils.colored_print import print_blue


def apply_fix_and_log(
    issue,
    original_code,
    ai_generated_fix,
    correctly_updated,
    retries,
    cloned_repo_path,
    log_path,
):
    issue_details = f"Rule: {issue['rule']} - Message: {issue['message']} - Component: {issue['component']}"
    # print_blue(f"\nHandling Issue: {issue_details}\n")

    if not ai_generated_fix.strip():
        print(f"No valid fix provided for {issue['key']}. Skipping...")
        return

    file_path = os.path.join(cloned_repo_path, issue["component"].split(":")[1])

    with open(file_path, "w") as file:
        file.write(ai_generated_fix)

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "issue_key": issue["key"],
        "rule": issue["rule"],
        "message": issue["message"],
        "component": issue["component"],
        "original_code": original_code,
        "ai_generated_fix": ai_generated_fix,
        "evaluation_result": correctly_updated,
        "error_message": None,  # Placeholder for potential errors
        "retries": retries,
        "file_path": file_path,
    }

    with open(log_path, "a") as log_file:
        json.dump(log_entry, log_file)
        log_file.write("\n")

    print(f"Applied fix for {issue['key']} and logged the resolution.")

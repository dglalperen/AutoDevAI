import json
import os


def load_processed_issues(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {}
    with open(file_path, "r") as file:
        return json.load(file)


def save_processed_issue(file_path, issue_key, status):
    processed_issues = load_processed_issues(file_path)
    processed_issues[issue_key] = status
    with open(file_path, "w") as file:
        json.dump(processed_issues, file, indent=4)

import os
from utils.build_error_fix_prompt import build_error_fix_prompt
from utils.build_maven import run_maven_build
from utils.clone_repo import clone_repo
from utils.console_interaction import fork_and_clone_repository, introduce_program, get_repository, ask_to_fork_and_clone, is_valid_github_url
from utils.prepare_prompt import prepare_prompt
from utils.setup_qa_retriever import setup_qa_retriever
from utils.sonar_backend import get_projects, get_filtered_issues
from utils.apply_fix_and_log import apply_fix_and_log
from utils.processed_issues_operations import load_processed_issues
from utils.extract_corrected_code import extract_corrected_code
import json

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEBUG_GITHUB_URL = "https://github.com/dglalperen/Rental-Car-Agency.git"

def main():
    introduce_program()
    
    repo_choice = get_repository()
    cloned_repo_path = None

    if is_valid_github_url(repo_choice):
        fork_and_clone = ask_to_fork_and_clone()
        if fork_and_clone:
            print(f"Forking and cloning {repo_choice}...")
            cloned_repo_path = fork_and_clone_repository(repo_choice)
        else:
            print(f"Cloning {repo_choice} without forking...")
            cloned_repo_path = clone_repo(repo_choice)
    else:
        cloned_repo_path = repo_choice
        print(f"Using local repository at {cloned_repo_path}")

    print("Repository operation successful.")
    #! DONT KNOW IF WE CAN DO THAT AUTOMATICALLY
    print("Initiating SonarQube scan...")
    # Implement SonarQube scan and fetch results
    # issues = perform_sonarqube_scan(cloned_repo_path)
    #!

    # Get Projects from sonar backend
    organization = "dglalperen"
    projects = get_projects(organization)
    
    # Print Projects and let the user choose
    print("Projects:")
    for idx, project in enumerate(projects):
        print(f"{idx}. Project: {project['name']}")

    project_idx = int(input("Please enter the project index you'd like to auto-develop: "))
    project_key = projects[project_idx]['key']

    # Get Issues from sonar backend
    #project_key = "dglalperen_Rental-Car-Agency"
    # Get Issues from Sonar backend
    issues = get_filtered_issues(project_key)
    
    # Group issues by rule and file component
    grouped_issues = {}
    for issue in issues:
        component = issue['component'].split(':', 1)[1]
        issue_group_key = f"{issue['rule']}:{component}"
        if issue_group_key not in grouped_issues:
            grouped_issues[issue_group_key] = []
        grouped_issues[issue_group_key].append(issue)

    # Initialize QA retrieval chain
    qa = setup_qa_retriever(cloned_repo_path, model='gpt-4')
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, 'issue_resolutions.log')
    processed_issues_file = os.path.join(script_dir, 'processed_issues.json')
    processed_issues = load_processed_issues(processed_issues_file)
    
    for group_key, issues_in_group in grouped_issues.items():
        if group_key in processed_issues:
            print(f"Group {group_key} has already been processed. Skipping...")
            continue

        first_issue = issues_in_group[0]
        prompt_text = prepare_prompt(group_key, first_issue)
        response = qa(prompt_text)
        print("DEBUG: Response:", response)
        
        # Apply fixes and build the project
        for attempt in range(3):
            print(f"Attempt {attempt + 1} to fix and build...")
            for issue in issues_in_group:
                apply_fix_and_log(issue, extract_corrected_code(response["answer"]), cloned_repo_path, log_path)

            # Check if the build is successful
            build_result, error_message = run_maven_build(cloned_repo_path)
            if build_result:
                print("Build successful.")
                break
            else:
                print("Build failed. Attempting to fix...")
                error_fix_prompt = build_error_fix_prompt(error_message)
                response = qa(error_fix_prompt)  # Get a fix for the build error
                if not response['answer']:
                    print("Unable to resolve build error.")
                    break

            processed_issues[group_key] = True

        with open(processed_issues_file, 'w') as file:
            json.dump(processed_issues, file)

if __name__ == "__main__":
    main()
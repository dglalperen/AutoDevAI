import os
from utils.build_error_fix_prompt import build_error_fix_prompt
from utils.build_maven import run_maven_build_docker
from utils.clone_repo import clone_repo
from utils.console_interaction import fork_and_clone_repository, introduce_program, get_repository, ask_to_fork_and_clone, is_valid_github_url
from utils.prepare_prompt import fetch_rule_details, prepare_prompt_with_function_call
from utils.setup_qa_retriever import setup_qa_retriever
from utils.sonar_backend import get_projects, get_filtered_issues
from utils.apply_fix_and_log import apply_fix_and_log
from utils.processed_issues_operations import load_processed_issues
from utils.extract_corrected_code import extract_corrected_code
from utils.sonarqube.sonar_scan import create_sonar_project_file_if_not_exists, run_sonarqube_scan_docker
import json

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SONARCLOUD_TOKEN = os.getenv("SONARCLOUD_TOKEN")
SONARQUBE_URL = os.getenv("SONARQUBE_URL")
DEBUG_GITHUB_URL = "https://github.com/dglalperen/Rental-Car-Agency.git"
ORGANIZATION = "dglalperen"

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

    # 0 Build the project
    print("Compiling the project...")
    build_result, error_message = run_maven_build_docker(cloned_repo_path)
    if not build_result:
        print("Failed to compile the project.")
        print("Error:", error_message)
        return
    
    project_name = os.path.basename(cloned_repo_path)
    create_sonar_project_file_if_not_exists(cloned_repo_path, project_name)

    # 1 First Scan
    print("Initiating SonarQube scan...")
    run_sonarqube_scan_docker(cloned_repo_path, SONARCLOUD_TOKEN, ORGANIZATION, project_name)

    # 2 Get Projects from sonar backend
    projects = get_projects(ORGANIZATION)
    
    # 3 Select a project from sonar backend
    print("Projects:")
    for idx, project in enumerate(projects):
        print(f"{idx}. Project: {project['name']}")

    project_idx = int(input("Please enter the project index you'd like to auto-develop: "))
    project_key = projects[project_idx]['key']

    # 4 Get issues for the selected project
    issues = get_filtered_issues(project_key)
    
    # 5 Group issues by rule and component
    grouped_issues = {}
    for issue in issues:
        component = issue['component'].split(':', 1)[1]
        issue_group_key = f"{issue['rule']}:{component}"
        if issue_group_key not in grouped_issues:
            grouped_issues[issue_group_key] = []
        grouped_issues[issue_group_key].append(issue)

    # 6 For each group, get a fix from OpenAI
    qa = setup_qa_retriever(cloned_repo_path, model='gpt-4')
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, 'issue_resolutions.log')
    processed_issues_file = os.path.join(script_dir, 'processed_issues.json')
    
    # 7 Load previously processed issues to avoid reprocessing
    processed_issues = load_processed_issues(processed_issues_file)
    
    # 8 For each group, get a fix from OpenAI
    for group_key, issues_in_group in grouped_issues.items():
        
        # Skip if the group has already been processed
        if group_key in processed_issues:
            print(f"Group {group_key} has already been processed. Skipping...")
            continue

        # 9 Fetch rule details for the first issue in the group to prepare the prompt
        first_issue = issues_in_group[0]
        rule_details = fetch_rule_details(first_issue['rule'])
        prompt_text = prepare_prompt_with_function_call(group_key, first_issue,rule_details)
        
        # 10 Get a fix from OpenAI
        response = qa(prompt_text)
        print("DEBUG: Response:", response)
        
        # 11 Apply the fix and log the changes
        for attempt in range(3):
            print(f"Attempt {attempt + 1} to fix and build...")
            
            # 12 Apply the fix and log the changes
            for issue in issues_in_group:
                apply_fix_and_log(issue, extract_corrected_code(response["answer"]), cloned_repo_path, log_path)

            # 13 Build the project again to see if the fix worked
            build_result, error_message = run_maven_build_docker(cloned_repo_path)
            if build_result:
                print("Build successful.")
                break # Break out of the attempt loop
            else:
                print("Build failed. Attempting to fix...")
                
                # 14 If the build failed, get a fix for the build error
                error_fix_prompt = build_error_fix_prompt(error_message)
                response = qa(error_fix_prompt)
                if not response['answer']:
                    print("Unable to resolve build error.")
                    break # Exit the loop if unable to resolve the build error

            # 15 Log the group as processed
            processed_issues[group_key] = True

        # 16 Save the processed issues
        with open(processed_issues_file, 'w') as file:
            json.dump(processed_issues, file)

if __name__ == "__main__":
    main()
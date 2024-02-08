import os
import json
from utils.build_error_fix_prompt import build_error_fix_prompt
from utils.build_maven import run_maven_build_docker
from utils.clone_repo import clone_repo
from utils.console_interaction import (fork_and_clone_repository, get_number_of_generations, introduce_program,
                                       get_repository, ask_to_fork_and_clone, is_valid_github_url)
from utils.prepare_prompt import fetch_rule_details, prepare_prompt_with_function_call
from utils.setup_qa_retriever import setup_qa_retriever
from utils.sonar_backend import get_filtered_issues
from utils.apply_fix_and_log import apply_fix_and_log
from utils.processed_issues_operations import load_processed_issues, save_processed_issue
from utils.extract_corrected_code import extract_corrected_code
from utils.sonarqube.sonar_scan import create_sonar_project_file_if_not_exists, run_sonarqube_scan_docker

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
    generations = get_number_of_generations()

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
    
    for generation in range(1, generations + 1):
        print(f"\n--- Starting Generation {generation} ---")
        # Build the project
        print("Compiling the project...")
        build_result, error_message = run_maven_build_docker(cloned_repo_path)
        if not build_result:
            print("Failed to compile the project.")
            print("Error:", error_message)
            return
        
        print("Build successful.")
        
        project_name = os.path.basename(cloned_repo_path)
        create_sonar_project_file_if_not_exists(cloned_repo_path, project_name)

        # First Scan
        print("Initiating SonarQube scan...")
        run_sonarqube_scan_docker(cloned_repo_path, SONARCLOUD_TOKEN, ORGANIZATION, project_name)

        # Automatically select the SonarQube project
        project_key = f"{project_name}"
        print(f"Automatically selected SonarQube project: {project_name}")

        # Get issues for the selected project
        issues = get_filtered_issues(project_key)
        
        if not issues:
            print(f"No issues found for project: {project_name}. The project meets the quality standards.")
            print("No further development required based on the current quality checks.")
            break
        
        # Group issues by rule and component
        grouped_issues = {}
        for issue in issues:
            component = issue['component'].split(':', 1)[1]
            issue_group_key = f"{issue['rule']}:{component}"
            if issue_group_key not in grouped_issues:
                grouped_issues[issue_group_key] = []
            grouped_issues[issue_group_key].append(issue)

        # For each group, get a fix from OpenAI
        qa = setup_qa_retriever(cloned_repo_path, model='gpt-4-0125-preview')
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, 'issue_resolutions.log')
        processed_issues_file = os.path.join(script_dir, 'processed_issues.json')
        
        # Load previously processed issues to avoid reprocessing
        processed_issues = load_processed_issues(processed_issues_file)
        
        for group_key, issues_in_group in grouped_issues.items():
            
            if group_key in processed_issues:
                print(f"Group {group_key} has already been processed. Skipping...")
                continue

            first_issue = issues_in_group[0]
            rule_details = fetch_rule_details(first_issue['rule'])
            prompt_text = prepare_prompt_with_function_call(group_key, first_issue, rule_details)
            
            response = qa(prompt_text)
            print(60*"-")
            print("DEBUG OPENAI Response:", response['answer'])
            print(60*"-")
            
            for attempt in range(3):
                print(f"Attempt {attempt + 1} to fix and build...")
                
                for issue in issues_in_group:
                    fixed_code = extract_corrected_code(response["answer"])
                    apply_fix_and_log(issue, fixed_code, cloned_repo_path, log_path)
                    save_processed_issue(processed_issues_file, group_key)

                build_result, error_message = run_maven_build_docker(cloned_repo_path)
                if build_result:
                    print("Build successful.")
                    break
                else:
                    print("Build failed. Attempting to fix...")
                    
                    error_fix_prompt = build_error_fix_prompt(error_message)
                    response = qa(error_fix_prompt)
                    if not response['answer']:
                        print("Unable to resolve build error.")
                        break

                processed_issues[group_key] = True

            with open(processed_issues_file, 'w') as file:
                json.dump(processed_issues, file)
        
        if build_result:
            print(f"Generation {generation} completed successfully. Moving to the next generation.")
        else:
            print(f"Generation {generation} could not be completed successfully. Retrying...")
    
    print("\nAll generations processed. The project development cycle is complete.")

if __name__ == "__main__":
    main()

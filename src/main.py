import os
from utils.console_interaction import introduce_program, get_repository, ask_to_fork_and_clone
from utils.load_java_documents_from_repo import load_java_documents_from_repo
from utils.prepare_prompt import prepare_prompt
from utils.setup_qa_retriever import setup_qa_retriever
from utils.sonar_backend import get_projects, get_filtered_issues
from datetime import datetime
import json
from utils.apply_fix_and_log import apply_fix_and_log

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def main():
    introduce_program()
    
    repo_url = get_repository()
    cloned_repo_path = None

    if ask_to_fork_and_clone():
        print(f"Forking and cloning {repo_url}...")
        # Implement fork and clone functionality
        # cloned_repo_path = fork_and_clone_repo(repo_url)
    
    else:
        print("Proceeding without forking.")

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
    for idx, project in projects:
        print(f"{idx}. Project: {project['components']['name']}")
    project_idx = input("Please enter the project index you'd like to auto-develop: ")
    project_key = projects[project_idx]['components']['key']

    # Get Issues from sonar backend
    #project_key = "dglalperen_Rental-Car-Agency"
    issues = get_filtered_issues(project_key)

    # Initialize QA retrieval chain
    qa = setup_qa_retriever(cloned_repo_path, model='gpt-4')
    
    # Define log path
    log_path = os.path.join(cloned_repo_path, "issue_resolutions.log")
    
    # Process each issue with the language model
    for issue in issues:
        # Prepare prompt with issue details
        prompt_text = prepare_prompt(issue)
        
        # Get response from the language model
        response = qa(prompt_text)
        print(f"Issue Resolution for {issue['key']}: {response['answer']}")
        
        # Apply fix and log the resolution
        apply_fix_and_log(issue, response['answer'], cloned_repo_path, log_path)


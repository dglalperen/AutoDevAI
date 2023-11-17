import os
from utils.clone_repo import clone_repo
from utils.console_interaction import fork_and_clone_repository, introduce_program, get_repository, ask_to_fork_and_clone, is_valid_github_url
from utils.load_java_documents_from_repo import load_java_documents_from_repo
from utils.prepare_prompt import prepare_prompt
from utils.setup_qa_retriever import setup_qa_retriever
from utils.sonar_backend import get_projects, get_filtered_issues
from utils.apply_fix_and_log import apply_fix_and_log
from utils.processed_issues_operations import load_processed_issues, save_processed_issue

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
    issues = get_filtered_issues(project_key)

    # Initialize QA retrieval chain
    qa = setup_qa_retriever(cloned_repo_path, model='gpt-4')
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, 'issue_resolutions.log')
    processed_issues_file = os.path.join(script_dir, 'processed_issues.json')
    processed_issues = load_processed_issues(processed_issues_file)
    
    # Process each issue with the language model
    for issue in issues:
        if issue['key'] in load_processed_issues(processed_issues_file):
            print(f"Issue {issue['key']} has already been processed. Skipping...")
            continue
        # Prepare prompt with issue details
        prompt_text = prepare_prompt(issue)
        
        # Get response from the language model
        response = qa(prompt_text)
        print(f"Issue Resolution for {issue['key']}: {response['answer']}")
        
        # Apply fix and log the resolution
        apply_fix_and_log(issue, response['answer'], cloned_repo_path, log_path)
        
        # Save the issue key to the processed issues list
        save_processed_issue(processed_issues_file, issue['key'])

if __name__ == "__main__":
    main()
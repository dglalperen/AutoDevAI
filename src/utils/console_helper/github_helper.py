from github import Github
import os
import dotenv
from pathlib import Path
import re
import subprocess
from utils.print_utils.colored_print import print_blue, print_green, print_red, print_yellow

def clone_repo(repo_url):
    # Get the name of the repository from the URL
    repo_name = repo_url.split("/")[-1].split(".")[0]
    
    # Get the path to the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate up two directories to the project root
    project_root = os.path.join(script_dir, '..', '..')
    
    # Create the path to the Repos folder within your project's root directory
    repos_path = os.path.join(project_root, 'Repos')
    
    # Ensure the Repos folder exists
    os.makedirs(repos_path, exist_ok=True)
    
    # Create the path to the repository folder
    repo_path = os.path.join(repos_path, repo_name)
    
    # Clone the repository into the repository folder
    subprocess.run(["git", "clone", repo_url, repo_path])

    # Return the path where the repository is cloned
    return repo_path

def is_valid_github_url(url):
    regex = r'https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+(\.git)?'
    return re.match(regex, url) is not None

def fork_and_clone_repository(repo_url):
    dotenv.load_dotenv()
    GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
    # Authenticate with GitHub
    g = Github(GITHUB_API_KEY)
    try:
        repo_name = get_repo_name_from_url(repo_url)
        user = g.get_user()
        repo = g.get_repo(repo_name)
        forked_repo = user.create_fork(repo)
        clone_repo(forked_repo.clone_url)
        return forked_repo.clone_url
    except Exception as e:
        print_red(f"Error occurred during forking and cloning: {e}")
        return None
    
def get_repo_name_from_url(url):
    return url.split('/')[-2] + '/' + url.split('/')[-1].replace('.git', '')

def commit_changes(repo_path, message):
    """
    Commit changes to the local repository.

    :param repo_path: Path to the local repository.
    :param message: Commit message.
    """
    # Navigate to the repository directory
    os.chdir(repo_path)
    
    # Configure Git to bypass the need for user identity in this script context
    os.system("git config user.name 'dglalperen'")
    os.system("git config user.email 'alperen.dagli43@gmail.com'")
    
    # Add all changes to staging
    os.system("git add .")
    
    # Commit the changes
    commit_status = os.system(f"git commit -m '{message}'")
    
    # Check if commit was successful
    if commit_status == 0:
        print_green("Changes committed successfully.")
    else:
        print_yellow("No changes to commit or commit failed.")

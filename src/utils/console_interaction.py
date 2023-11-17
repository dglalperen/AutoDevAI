from clone_repo import clone_repo
from github import Github
import os
import dotenv
import re

def introduce_program():
    print("\nWelcome to AutoDevAI!")
    print("This program autonomously improves and evolves Java software repositories.")
    print("Let's get started.\n")

def get_repository():
    while True:
        repo_url = input("Enter the GitHub URL of the Java repository you'd like to auto-develop: ").strip()
        if is_valid_github_url(repo_url):
            return repo_url
        else:
            print("Invalid URL. Please enter a valid GitHub repository URL.\n")

def ask_to_fork_and_clone():
    while True:
        choice = input("Would you like to fork and clone this repository locally? (yes/no): ").strip().lower()
        if choice in ['yes', 'no']:
            return choice == "yes"
        else:
            print("Invalid input. Please answer 'yes' or 'no'.\n")

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
        return forked_repo.clone_url  # Return the path where the repo is cloned
    except Exception as e:
        print(f"Error occurred during forking and cloning: {e}")
        return None

def is_valid_github_url(url):
    regex = r'https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+(\.git)?'
    return re.match(regex, url) is not None

def get_repo_name_from_url(url):
    return url.split('/')[-2] + '/' + url.split('/')[-1].replace('.git', '')


from utils.clone_repo import clone_repo
from github import Github
import os
import dotenv
import re
from pathlib import Path

def list_repositories_in_folder(folder_path):
    """List directories in the given folder path."""
    return [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]


def introduce_program():
    print("\nWelcome to AutoDevAI!")
    print("This program autonomously improves and evolves Java software repositories.")
    print("Let's get started.\n")

def get_repository():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    repos_path = os.path.join(project_root, 'Repos')

    available_repos = list_repositories_in_folder(repos_path)

    if available_repos:
        print("\nAvailable local repositories:")
        for idx, repo in enumerate(available_repos):
            print(f"{idx}. {repo}")

        choice = input("\nEnter the index of the repository to use, or enter a new GitHub URL: ").strip()

        if choice.isdigit() and int(choice) in range(len(available_repos)):
            selected_repo = available_repos[int(choice)]
            return os.path.join(repos_path, selected_repo)
        elif is_valid_github_url(choice):
            return choice
        else:
            print("Invalid input. Please enter a valid index or GitHub URL.\n")
            return get_repository()
    else:
        return input("\nEnter the GitHub URL of the Java repository you'd like to auto-develop: ").strip()


def ask_to_fork_and_clone():
    while True:
        choice = input("Would you like to (1) fork and clone this repository or (2) just clone it locally? Enter 1 or 2: ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print("Invalid input. Please enter 1 or 2.")


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
        print(f"Error occurred during forking and cloning: {e}")
        return None

def is_valid_github_url(url):
    regex = r'https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+(\.git)?'
    return re.match(regex, url) is not None

def get_repo_name_from_url(url):
    return url.split('/')[-2] + '/' + url.split('/')[-1].replace('.git', '')


import os
from pathlib import Path
from utils.console_helper.github_helper import is_valid_github_url
from utils.print_utils.colored_print import print_blue,print_green,print_red

def introduce_program():
    print_green("\nWelcome to AutoDevAI!")
    print_green("This program autonomously improves and evolves Java software repositories.")
    print_green("Let's get started.\n")

def ask_select_or_enter_repository():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    repos_path = os.path.join(project_root, 'Repos')

    available_repos = list_repositories_in_folder(repos_path)

    if available_repos:
        print_blue("\nAvailable local repositories:")
        for idx, repo in enumerate(available_repos):
            print(f"{idx}. {repo}")

        choice = input("\nEnter the index of the repository to use, or enter a new GitHub URL: ").strip()

        if choice.isdigit() and int(choice) in range(len(available_repos)):
            selected_repo = available_repos[int(choice)]
            return os.path.join(repos_path, selected_repo)
        elif is_valid_github_url(choice):
            return choice
        else:
            print_red("Invalid input. Please enter a valid index or GitHub URL.\n")
            return ask_select_or_enter_repository()
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
            print_red("Invalid input. Please enter 1 or 2.")


def ask_number_of_generations():
    """
    Ask the user for the number of generations they want to run the program.
    """
    while True:
        try:
            generations = int(input("Enter the number of generations to run: ").strip())
            if generations > 0:
                return generations
            else:
                print_blue("Please enter a positive integer.")
        except ValueError:
            print_red("Invalid input. Please enter an integer.")
            
def list_repositories_in_folder(folder_path):
    """List directories in the given folder path."""
    return [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
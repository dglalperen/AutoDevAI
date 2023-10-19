import os
from utils.console_interaction import introduce_program, get_repository, ask_to_fork_and_clone

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



def main():
    introduce_program()
    
    repo_url = get_repository()
    
    if ask_to_fork_and_clone():
        print(f"Forking and cloning {repo_url}...")
        # TODO: Implement fork and clone functionality
    else:
        print("Proceeding without forking.")
    
    print("Initiating SonarQube scan...")
    # TODO: Implement SonarQube scan and fetch results

if __name__ == "__main__":
    main()

def introduce_program():
    print("Welcome to AutoDevAI!")
    print("This program aims to autonomously improve and evolve Java software repositories.")
    print("Let's get started.")

def get_repository():
    repo_url = input("Please enter the GitHub URL of the Java repository you'd like to auto-develop: ")
    # TODO: Validate the URL and check that it's a Java repository
    return repo_url

def ask_to_fork_and_clone():
    choice = input("Would you like to fork and clone this repository locally? (yes/no): ")
    return choice.lower() == "yes"

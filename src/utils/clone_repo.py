import dotenv
import os
import subprocess



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

# Cloning manually
if __name__ == "__main__":
    dotenv.load_dotenv()

    GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
    repo_url = "https://github.com/dglalperen/Rental-Car-Agency.git"
    clone_repo(repo_url)

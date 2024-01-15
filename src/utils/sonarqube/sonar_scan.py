import subprocess
import os

def run_sonarqube_scan(repo_path):
    original_dir = os.getcwd()
    os.chdir(repo_path)
    try:
        subprocess.run(["sonar-scanner"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"SonarQube scan failed: {e}")
    finally:
        os.chdir(original_dir)


def main():
    # Assuming that the cloned repository path is obtained from some user input or other logic
    cloned_repo_path = ""  # Placeholder: Replace with logic to obtain the actual repo path

    # Verify that the path is not empty
    if not cloned_repo_path:
        print("Error: Cloned repository path is empty.")
        return

    print(f"Initiating SonarQube scan on repository at {cloned_repo_path}...")
    run_sonarqube_scan(cloned_repo_path)

if __name__ == "__main__":
    main()

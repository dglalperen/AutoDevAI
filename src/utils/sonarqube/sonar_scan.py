import subprocess
import os

def run_sonarqube_scan(repo_path):
    original_dir = os.getcwd()
    os.chdir(repo_path)
    try:
        #subprocess.run(["sonar-scanner"], check=True)
        # temporarely using direct path
        subprocess.run(["C:\\Users\\Alpi\\Desktop\\HRW\\Master\\sonar-scanner-cli-5.0.1.3006-windows\\sonar-scanner-5.0.1.3006-windows\\bin\\sonar-scanner.bat"], check=True)
        print("SonarQube scan completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"SonarQube scan failed: {e}")
    finally:
        os.chdir(original_dir)

def create_sonar_project_file_if_not_exists(repo_path, repo_name):
    sonar_file_path = os.path.join(repo_path, 'sonar-project.properties')
    if not os.path.exists(sonar_file_path):
        with open(sonar_file_path, 'w') as file:
            file.write(f"sonar.projectKey={repo_name}\n")
            file.write(f"sonar.projectName={repo_name}\n")
            file.write("sonar.projectVersion=1.0\n")
            file.write("sonar.sources=src/main/java\n")
            file.write("sonar.java.binaries=target/classes\n")
            file.write("sonar.exclusions=**/test/**\n")
            file.write("sonar.login=sqa_040e2900a14c49c16814ea473cd40ca29f1b48bb")
            file.write("sonar.organization=dglalperen")
        print(f"Created sonar-project.properties in {repo_path}")

def test_create_sonar_project_file_if_not_exists():
    repo_path = "../../../Repos/Rental-Car-Agency"
    repo_name = "rental-car-agency"
    create_sonar_project_file_if_not_exists(repo_path, repo_name)


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
    test_create_sonar_project_file_if_not_exists()

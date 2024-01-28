import subprocess
import os
        
def run_sonarqube_scan_docker(repo_path, sonarcloud_token, organization, project_key):
    try:
        subprocess.run(
            ["docker", "run", "--rm",
             "-v", f"{os.path.abspath(repo_path)}:/usr/src",
             "sonarsource/sonar-scanner-cli",
             "-Dsonar.projectKey=" + project_key,
             "-Dsonar.organization=" + organization,
             "-Dsonar.sources=.",
             "-Dsonar.host.url=https://sonarcloud.io",
             "-Dsonar.login=" + sonarcloud_token],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("SonarCloud scan completed successfully.")
    except subprocess.CalledProcessError as e:
        print("SonarCloud scan failed.")

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

if __name__ == "__main__":
    mac_dir = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/Rental-Car-Agency"
    windows_dir = "/Users/adagli/Desktop/Coding/Uni/Projekt-2/AutoDevAI/Repos/Rental-Car-Agency"
    run_sonarqube_scan_docker(windows_dir)
    #test_create_sonar_project_file_if_not_exists()

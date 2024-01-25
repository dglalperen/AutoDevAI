import subprocess
import re
import os
# mvn clean install -DskipTests

# docker run --rm -v /Users/dglalperen/Desktop/Uni/Project-2/Repos/Rental-Car-Agency:/app maven-build-17 mvn clean install -DskipTests

def run_maven_build_docker(project_path):
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", 
             f"{project_path}:/app",
             "maven-build-17", "mvn", "clean", "install", "-DskipTests"],
            check=True, capture_output=True, text=True
        )
        print("Build Output:\n", result.stdout)
        return True, None
    except subprocess.CalledProcessError as e:
        print("Build failed. Output:\n", e.stdout)
        print("Build failed. Error Output:\n", e.stderr)
        return False, e.stderr


def run_maven_build(project_path):
    try:
        result = subprocess.run(['mvn', 'clean', 'install', '-DskipTests'], cwd=project_path, check=True, capture_output=True)
        print("Build Output:\n", result.stdout.decode())
        return True, None
    except subprocess.CalledProcessError as e:
        #print("Build Error Output:\n", e.output.decode())
        #print("Build Error Stderr:\n", e.stderr.decode())
        #error_message = extract_detailed_error_message(e.output.decode())
        error_message = e.output.decode()
        #print("Detailed Maven Error:\n", error_message)
        return False, error_message

def extract_detailed_error_message(stderr):
    # Pattern to identify the start of the actual error message
    error_pattern = re.compile(r"\[ERROR\](.*?)\[INFO\]", re.DOTALL)

    # Search for the pattern in stderr
    match = error_pattern.search(stderr)
    if match:
        # Extracting only the error message part
        error_message = match.group(1).strip()
        # Removing additional [ERROR] tags from within the message
        error_message_clean = re.sub(r"\[ERROR\]", "", error_message).strip()
        return error_message_clean
    else:
        return "Detailed error message not found. Check the Maven build logs."


def is_maven_project(path):
    """ Check if a given path contains a Maven project (pom.xml file) """
    return os.path.isfile(os.path.join(path, 'pom.xml'))

def list_maven_projects(repos_dir):
    """ List all Maven projects in the specified directory """
    maven_projects = []
    for repo_name in os.listdir(repos_dir):
        repo_path = os.path.join(repos_dir, repo_name)
        if os.path.isdir(repo_path) and is_maven_project(repo_path):
            maven_projects.append(repo_path)
    return maven_projects

def main():
    repos_dir = "/Users/dglalperen/Desktop/Uni/Project-2/Repos"  # Provide the absolute path
    maven_projects = list_maven_projects(repos_dir)

    # Display Maven projects and let the user choose
    print("Available Maven Projects:")
    for idx, project in enumerate(maven_projects):
        print(f"{idx}: {project}")

    selected_index = int(input("Enter the number of the project to build: "))
    if 0 <= selected_index < len(maven_projects):
        selected_project = maven_projects[selected_index]
        print(f"Building Maven project in {selected_project}...")
        success, error_message = run_maven_build_docker(selected_project)  # Or run_maven_build_docker
        if success:
            print(f"Build was successful for {selected_project}.")
        else:
            print(f"Build failed for {selected_project}. Error: {error_message}")
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()

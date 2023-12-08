import subprocess
import re

#mvn clean install -DskipTests

def run_maven_build(project_path):
    try:
        # Run the Maven build command with skipping tests
        result = subprocess.run(['mvn', 'clean', 'install', '-DskipTests'], cwd=project_path, check=True, text=True, capture_output=True)
        
        # Output the result
        print("Build Output:\n", result.stdout)
        return True, None
    except subprocess.CalledProcessError as e:
        # Extract and return the detailed error message from stderr
        error_message = extract_detailed_error_message(e.stderr)
        print("Detailed Maven Error:\n", error_message)
        return False, error_message

def extract_detailed_error_message(stderr):
    # Pattern to identify the start of the actual error message
    error_pattern = re.compile(r"\[ERROR\].*?\[INFO\]", re.DOTALL)
    
    # Search for the pattern in stderr
    match = error_pattern.search(stderr)
    if match:
        return match.group().strip()
    else:
        return "Detailed error message not found. Check the Maven build logs."


if __name__ == "__main__":
    project_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/Rental-Car-Agency"
    success, error_message = run_maven_build(project_path)
    if success:
        print("Build was successful.")
    else:
        print("Build failed. Error:", error_message)

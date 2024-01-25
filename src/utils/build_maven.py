import subprocess
import re

# mvn clean install -DskipTests

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


if __name__ == "__main__":
    #project_path = "/Users/dglalperen/Desktop/Uni/Project-2/Repos/Rental-Car-Agency"
    project_path = "/Users\Alpi\Desktop\HRW\Master\Projekt-2\AutoDevAI\Repos\Online-Banking-System"
    success, error_message = run_maven_build(project_path)
    if success:
        print("Build was successful.")
    else:
        print("Build failed. Error:", error_message)

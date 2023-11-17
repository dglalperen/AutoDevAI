import subprocess

def run_maven_build(project_path):
    try:
        # Run the Maven build command in the specified project directory
        result = subprocess.run(['mvn', 'clean', 'install'], cwd=project_path, check=True, text=True, capture_output=True)

        # Output the result
        print("Build Output:\n", result.stdout)
        return True, ""
    except subprocess.CalledProcessError as e:
        # Output error details if the build fails
        print("Build failed with the following error:\n", e.stderr)
        return False, e.stderr

if __name__ == "__main__":
    project_path = "path/to/your/project"  # Replace with the actual project path
    success, error_message = run_maven_build(project_path)
    if success:
        print("Build was successful.")
    else:
        print("Build failed. Error:", error_message)

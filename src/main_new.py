import os
import json
from utils.console_helper.console_interaction import (
    ask_select_or_enter_repository,
    ask_to_fork_and_clone,
    introduce_program,
    print_summary,
)
from utils.console_helper.github_helper import (
    clone_repo,
    fork_and_clone_repository,
    is_valid_github_url,
)
from utils.langchain_helper.apply_fix_and_log import apply_fix_and_log
from utils.langchain_helper.extract_updated_java_class import (
    extract_correctly_updated,
    extract_updated_java_class,
)
from utils.langchain_helper.openai_conversation_handler import OpenAIConversationHandler
from utils.langchain_helper.processed_issues_operations import (
    load_processed_issues,
    save_processed_issue,
)
from utils.maven_sonar.docker_sonar_scan import (
    create_sonar_project_file_if_not_exists,
    run_sonarqube_scan_docker,
)
from utils.maven_sonar.sonar_backend_helper import get_filtered_issues
from utils.maven_sonar.docker_maven_builder import run_maven_build_docker
from utils.prompts.evaluate_prompt import setup_evaluation_prompt
from utils.prompts.prepare_prompt import (
    fetch_rule_details,
    get_file_content,
    setup_prompt,
)
from utils.print_utils.colored_print import (
    print_blue,
    print_green,
    print_red,
    print_yellow,
)

# Load API keys and tokens from environment
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SONARCLOUD_TOKEN = os.getenv("SONARCLOUD_TOKEN")
DEBUG_GITHUB_URL = "https://github.com/dglalperen/Rental-Car-Agency.git"
ORGANIZATION = "dglalperen"


def is_content_complete(java_class_content):
    placeholders = [
        "Rest of the class remains unchanged...",
        "Rest of the methods remains unchanged...",
        "remains unchanged",
    ]
    return not any(placeholder in java_class_content for placeholder in placeholders)


def get_java_class_content(issue, cloned_repo_path, force_original=False):
    component_path = issue["component"]
    if ":" in component_path:
        component_path = component_path.split(":")[1]
    original_path = os.path.join(cloned_repo_path, component_path.replace("/", os.sep))
    cache_dir = os.path.abspath(os.path.join(cloned_repo_path, ".cache"))
    os.makedirs(cache_dir, exist_ok=True)
    cache_file_name = component_path.replace("/", "_").replace(".java", "_cached.java")
    cache_path = os.path.join(cache_dir, cache_file_name)

    if force_original or not os.path.exists(cache_path):
        with open(original_path, "r") as file:
            content = file.read()
        with open(cache_path, "w") as file:
            file.write(content)
    else:
        with open(cache_path, "r") as file:
            content = file.read()

    if is_content_complete(content):
        return content
    else:
        if os.path.exists(original_path):
            with open(original_path, "r") as file:
                return file.read()
        else:
            raise FileNotFoundError(
                f"Cannot find the original Java file at: {original_path}"
            )


def handle_issues(
    issues,
    generation,
    project_name,
    cloned_repo_path,
    openai_conversation_handler,
    processed_issues_file,
):
    total_issues = len(issues)
    print_blue(f"Handling {total_issues} issues in generation {generation}.")
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../ResultLogs/issue_resolutions_high_complexity.log",
    )

    for index, issue in enumerate(issues, 1):
        print_blue(f"Processing issue {index} of {total_issues}: Rule {issue['rule']}")
        if evaluate_and_fix_issue(
            issue,
            project_name,
            cloned_repo_path,
            openai_conversation_handler,
            log_path,
        ):
            save_processed_issue(processed_issues_file, issue["key"], "processed")
        else:
            print_red(
                f"Failed to process issue {issue['key']} with rule {issue['rule']}."
            )


def evaluate_and_fix_issue(
    issue,
    project_name,
    cloned_repo_path,
    openai_conversation_handler,
    log_path,
    max_retries=2,
    interactive=False,
):
    print_blue(f"Evaluating issue {issue['key']} with rule {issue['rule']}")
    original_java_class = get_java_class_content(
        issue, cloned_repo_path, force_original=True
    )
    rule_details = fetch_rule_details(issue["rule"])
    attempts = 0
    correctly_updated = False

    while attempts <= max_retries:
        print_blue(
            f"Attempt {attempts + 1} for issue {issue['key']} with rule {issue['rule']}"
        )
        prompt_text = setup_prompt(issue["rule"], issue, rule_details)
        response_text = openai_conversation_handler.ask_question(prompt_text)
        updated_java_class = extract_updated_java_class(response_text)
        evaluation_prompt = setup_evaluation_prompt(
            original_java_class, updated_java_class, issue["message"]
        )
        evaluation_response = openai_conversation_handler.ask_question(
            evaluation_prompt
        )
        correctly_updated = extract_correctly_updated(evaluation_response)

        if correctly_updated:
            print_green(
                f"Correct fix applied for {issue['rule']} on {issue['component']}."
            )
            apply_fix_and_log(
                issue,
                original_java_class,
                updated_java_class,
                correctly_updated,
                attempts,
                cloned_repo_path,
                log_path,
            )
            return True
        else:
            print_red(f"Fix for {issue['rule']} on {issue['component']} was incorrect.")
            attempts += 1
            print_yellow("Retrying...")
            if interactive and attempts > max_retries:
                print_red(
                    f"Maximum retries reached for {issue['rule']} on {issue['component']}."
                )
                return False
    return correctly_updated


def main():
    introduce_program()
    repo_choice = ask_select_or_enter_repository()
    cloned_repo_path = None

    if is_valid_github_url(repo_choice):
        fork_and_clone = ask_to_fork_and_clone()
        if fork_and_clone:
            print_blue(f"Forking and cloning {repo_choice}...")
            cloned_repo_path = fork_and_clone_repository(repo_choice)
        else:
            print_blue(f"Cloning {repo_choice} without forking...")
            cloned_repo_path = clone_repo(repo_choice)
    else:
        cloned_repo_path = repo_choice
        print_blue(f"Using local repository at {cloned_repo_path}")

    print_green("Repository operation successful.")
    gpt4o = "gpt-4o"
    openai_conversation_handler = OpenAIConversationHandler(
        api_key=OPENAI_API_KEY, model=gpt4o
    )
    script_dir = os.path.dirname(os.path.abspath(__file__))
    processed_issues_file = os.path.join(
        script_dir, "../ResultLogs/processed_issues.json"
    )
    project_name = os.path.basename(cloned_repo_path)

    generation = 1
    total_issues_processed = 0

    # Ask user to select complexity level(s)
    print_blue("Select complexity level(s) to work on:")
    print_blue("1. Low complexity")
    print_blue("2. High complexity")
    print_blue("3. Both")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        complexities = ["low"]
    elif choice == "2":
        complexities = ["high"]
    elif choice == "3":
        complexities = ["low", "high"]
    else:
        print_red("Invalid choice. Exiting.")
        return

    for complexity in complexities:
        while True:
            print_blue(
                f"\n--- Starting Generation {generation} (Complexity: {complexity}) ---"
            )
            build_result, error_message = run_maven_build_docker(cloned_repo_path)
            if not build_result:
                print_red("Failed to compile the project.")
                print_red(f"Error: {error_message}")
                return  # Exit if the build fails

            print_green("Build successful.")
            create_sonar_project_file_if_not_exists(cloned_repo_path, project_name)
            print_blue("Initiating SonarQube scan...")
            run_sonarqube_scan_docker(
                cloned_repo_path, SONARCLOUD_TOKEN, ORGANIZATION, project_name
            )
            issues = get_filtered_issues(project_name, complexity)

            if not issues:
                print_yellow(
                    f"No {complexity} complexity issues found for {project_name}."
                )
                break  # Move to the next complexity if no issues are found

            handle_issues(
                issues,
                generation,
                project_name,
                cloned_repo_path,
                openai_conversation_handler,
                processed_issues_file,
            )
            processed_issues = load_processed_issues(processed_issues_file)
            total_issues_processed += len(issues)

            all_issues_resolved = all(
                status == "processed" for status in processed_issues.values()
            )

            if all_issues_resolved:
                print_green("All issues have been resolved. Ending the process.")
                break

            generation += 1

    print_blue("Performing final SonarQube scan to verify the overall project state...")
    run_sonarqube_scan_docker(
        cloned_repo_path, SONARCLOUD_TOKEN, ORGANIZATION, project_name
    )
    print_green("Final SonarQube scan completed.")

    print_summary(load_processed_issues(processed_issues_file), total_issues_processed)


if __name__ == "__main__":
    main()

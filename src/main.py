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


def is_content_complete(java_class_content):
    placeholders = [
        "Rest of the class remains unchanged...",
        "Rest of the methods remains unchanged...",
        "remains unchanged",
    ]
    return not any(placeholder in java_class_content for placeholder in placeholders)


def get_java_class_content(issue, cloned_repo_path, force_original=False):
    cache_dir = os.path.join(cloned_repo_path, ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(
        cache_dir, issue["component"].replace("/", "_").replace(".java", "_cached.java")
    )
    original_path = os.path.join(cloned_repo_path, issue["component"])

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
        with open(original_path, "r") as file:
            return file.read()


def evaluate_and_fix_issue(
    issue,
    project_name,
    cloned_repo_path,
    openai_conversation_handler,
    log_path,
    max_retries=2,
):
    original_java_class = get_java_class_content(
        issue, cloned_repo_path, force_original=True
    )
    rule_details = fetch_rule_details(issue["rule"])
    attempts = 0

    while attempts <= max_retries:
        prompt_text = setup_prompt(issue["rule"], issue, rule_details)
        response_text = openai_conversation_handler.ask_question(prompt_text)
        updated_java_class = extract_updated_java_class(response_text)
        evaluation_prompt = setup_evaluation_prompt(
            original_java_class, updated_java_class, issue["message"]
        )

        # Evaluate the updated class
        evaluation_response = openai_conversation_handler.ask_question(
            evaluation_prompt
        )
        correctly_updated = extract_correctly_updated(evaluation_response)

        if correctly_updated:
            print_green(
                f"Correct fix applied for {issue['rule']} on {issue['component']}."
            )
            apply_fix_and_log(issue, updated_java_class, cloned_repo_path, log_path)
            break
        else:
            print_red(f"Fix for {issue['rule']} on {issue['component']} was incorrect.")
            attempts += 1
            if attempts > max_retries:
                print_red(
                    f"Maximum retries reached for {issue['rule']} on {issue['component']}."
                )
                break

            print_yellow("Retrying...")
            # Force to use original file on retries
            original_java_class = get_java_class_content(
                issue, cloned_repo_path, force_original=True
            )


def handle_issues(
    issues, generation, project_name, cloned_repo_path, openai_conversation_handler
):
    total_issues = len(issues)
    print_blue(f"Handling {total_issues} issues in generation {generation}.")
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../ResultLogs/issue_resolutions.log",
    )

    for index, issue in enumerate(issues, 1):
        print_blue(f"Processing issue {index} of {total_issues}: Rule {issue['rule']}")
        if generation == 2:
            evaluate_and_fix_issue(
                issue, project_name, cloned_repo_path, openai_conversation_handler
            )
        else:
            original_java_class = get_file_content(issue["component"])
            prompt_text = setup_prompt(
                issue["rule"], issue, fetch_rule_details(issue["rule"])
            )
            response_text = openai_conversation_handler.ask_question(prompt_text)
            updated_java_class = extract_updated_java_class(response_text)
            apply_fix_and_log(issue, updated_java_class, cloned_repo_path, log_path)


# Load API keys and tokens from environment
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SONARCLOUD_TOKEN = os.getenv("SONARCLOUD_TOKEN")
DEBUG_GITHUB_URL = "https://github.com/dglalperen/Rental-Car-Agency.git"
ORGANIZATION = "dglalperen"


def main():
    introduce_program()
    repo_choice = ask_select_or_enter_repository()
    cloned_repo_path = None

    if is_valid_github_url(repo_choice):
        fork_and_clone = ask_to_fork_and_clone()
        if fork_and_clone:
            print_blue(f"Forking and cloning {repo_choice}...")
            cloned_repo_path = fork_and_clone_repository(repo_choice, GITHUB_API_KEY)
        else:
            print_blue(f"Cloning {repo_choice} without forking...")
            cloned_repo_path = clone_repo(repo_choice, GITHUB_API_KEY)
    else:
        cloned_repo_path = repo_choice
        print_blue(f"Using local repository at {cloned_repo_path}")

    print_green("Repository operation successful.")
    openai_conversation_handler = OpenAIConversationHandler(api_key=OPENAI_API_KEY)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    processed_issues_file = os.path.join(
        script_dir, "../ResultLogs/processed_issues.json"
    )
    project_name = os.path.basename(cloned_repo_path)

    generation = 1
    total_issues_processed = 0
    while True:
        print_blue(f"\n--- Starting Generation {generation} ---")
        complexity = "low" if generation == 1 else "high"
        build_result, error_message = run_maven_build_docker(cloned_repo_path)
        if not build_result:
            print_red("Failed to compile the project.")
            print_red(f"Error: {error_message}")
            break

        print_green("Build successful.")
        create_sonar_project_file_if_not_exists(cloned_repo_path, project_name)
        print_blue("Initiating SonarQube scan...")
        run_sonarqube_scan_docker(
            cloned_repo_path, SONARCLOUD_TOKEN, ORGANIZATION, project_name
        )
        issues = get_filtered_issues(project_name, complexity)

        if not issues:
            print_yellow(
                f"No {complexity} complexity issues found for {project_name}. Ending the cycle."
            )
            break

        handle_issues(
            issues,
            generation,
            project_name,
            cloned_repo_path,
            openai_conversation_handler,
        )
        processed_issues = load_processed_issues(processed_issues_file)
        total_issues_processed += len(issues)  # Update the total issues processed

        all_issues_resolved = all(
            status == "processed" for status in processed_issues.values()
        )

        if all_issues_resolved:
            print_green("All issues have been resolved. Ending the process.")
            break

        generation += 1  # Increment to move to the next generation

    print_summary(load_processed_issues(processed_issues_file), total_issues_processed)


if __name__ == "__main__":
    main()

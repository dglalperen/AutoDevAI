import os
import json
from utils.console_helper.console_interaction import (
    ask_number_of_generations,
    ask_select_or_enter_repository,
    ask_to_fork_and_clone,
    introduce_program,
)
from utils.console_helper.github_helper import (
    clone_repo,
    fork_and_clone_repository,
    is_valid_github_url,
)
from utils.langchain_helper.apply_fix_and_log import apply_fix_and_log
from utils.langchain_helper.extract_updated_java_class import (
    extract_updated_java_class,
    extract_correctly_updated,
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

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SONARCLOUD_TOKEN = os.getenv("SONARCLOUD_TOKEN")
DEBUG_GITHUB_URL = "https://github.com/dglalperen/Rental-Car-Agency.git"
ORGANIZATION = "dglalperen"


def main():
    introduce_program()

    repo_choice = ask_select_or_enter_repository()
    cloned_repo_path = None
    generations = ask_number_of_generations()

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

    openai_conversation_handler = OpenAIConversationHandler(api_key=OPENAI_API_KEY)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    processed_issues_file = os.path.join(
        script_dir, "../ResultLogs/processed_issues.json"
    )

    for generation in range(1, generations + 1):
        print_blue(f"\n--- Starting Generation {generation} ---")
        build_result, error_message = run_maven_build_docker(cloned_repo_path)
        if not build_result:
            print_red("Failed to compile the project.")
            print_red("Error:", error_message)
            return

        print_green("Build successful.")
        project_name = os.path.basename(cloned_repo_path)
        create_sonar_project_file_if_not_exists(cloned_repo_path, project_name)
        print_blue("Initiating SonarQube scan...")
        run_sonarqube_scan_docker(
            cloned_repo_path, SONARCLOUD_TOKEN, ORGANIZATION, project_name
        )

        issues = get_filtered_issues(os.path.basename(cloned_repo_path))

        if not issues:
            print_yellow(f"No issues found for project: {project_name}.")
            continue

        grouped_issues = {}
        processed_issues = load_processed_issues(processed_issues_file)
        for issue in issues:
            component = issue["component"].split(":", 1)[1]
            issue_group_key = f"{issue['rule']}:{component}"
            if (
                issue_group_key not in processed_issues
                or processed_issues[issue_group_key] == "unprocessed"
            ):
                if issue_group_key not in grouped_issues:
                    grouped_issues[issue_group_key] = []
                grouped_issues[issue_group_key].append(issue)

        log_path = os.path.join(script_dir, "../ResultLogs/issue_resolutions.log")

        for group_key, issues_in_group in grouped_issues.items():
            first_issue = issues_in_group[0]
            rule_details = fetch_rule_details(first_issue["rule"])
            original_java_class = get_file_content(first_issue["component"])
            prompt_text = setup_prompt(group_key, first_issue, rule_details)
            response_text = openai_conversation_handler.ask_question(prompt_text)

            updated_java_class = extract_updated_java_class(response_text)

            if updated_java_class:
                print_green(
                    f"The updated class for {group_key} has been correctly updated."
                )
                for issue in issues_in_group:
                    apply_fix_and_log(
                        issue, updated_java_class, cloned_repo_path, log_path
                    )
                save_processed_issue(processed_issues_file, group_key, "processed")
            else:
                print_red(f"Attempt for {group_key} was unsuccessful.")
                save_processed_issue(processed_issues_file, group_key, "unprocessed")

        if build_result:
            print_green(f"Generation {generation} completed successfully.")
        else:
            print_yellow(
                f"Generation {generation} could not be completed successfully."
            )

    print_blue(
        "\nAll generations processed. The project development cycle is complete."
    )


if __name__ == "__main__":
    main()

import requests

sonar_rules = [
    "java:S2259",
    "javabugs:S6466",
    "java:S3655",
    "java:S138",
    "java:S1541",
    "java:S1820",
    "java:S1192",
    "java:S1143",
    "java:S2142",
    "java:S1774",
    "java:S2057",
    "java:S106",
    "java:S1068",
    "java:S2390",
    "java:S2095",
    "java:S4925",
    "java:S2699",
    "java:S3776",
    "java:S1448",
    "java:S107",
    "java:S3516",
    "java:S3973",
    "java:S2692",
    "java:S2638",
    "java:S2447",
    "java:S131",
    "java:S4970",
    "java:S2252",
]


def get_projects(organization):
    """
    Get projects for a given organization.
    """
    response = requests.get(
        f"http://localhost:3000/projects?organization={organization}"
    )
    if response.status_code == 200:
        return response.json().get("components", [])
    else:
        return None


def get_issues(project_key):
    """
    Get issues for a given project key.
    """
    response = requests.get(f"http://localhost:4000/issues?projects={project_key}")
    if response.status_code == 200:
        return response.json().get("issues", [])
    else:
        return None


def filter_issues(issues):
    """
    Filter issues based on predefined sonar rules.
    """
    return [issue for issue in issues if issue.get("rule") in sonar_rules]


def get_issues_by_complexity(issues, complexity="low"):
    complexity_map = {
        "low": ["java:S1192", "java:S106", "java:S2447", "java:S2259", "java:S3655"],
        "high": ["java:S3776", "java:S1541", "java:S138"],
    }
    return [
        issue for issue in issues if issue.get("rule") in complexity_map[complexity]
    ]


def get_filtered_issues(project_key, complexity="low"):
    """
    Get filtered issues for a given project key based on complexity.
    """
    issues = get_issues(project_key)
    print(f"Total Issues for {project_key}: {len(issues)}")
    for issue in issues:
        print(issue)
    if issues:
        return get_issues_by_complexity(issues, complexity)
    else:
        print(f"No issues found for {project_key}.")
        return []


def get_issues_by_complexity(issues, complexity="low"):
    complexity_map = {
        "low": [
            "java:S1192",
            "java:S106",
            "java:S2447",
            "java:S2259",
            "java:S3655",
            "java:S1143",
            "java:S2142",
            "java:S1774",
            "java:S2057",
            "java:S2390",
            "java:S2095",
            "java:S4925",
            "java:S2699",
            "java:S3516",
            "java:S3973",
            "java:S2692",
            "java:S2638",
            "java:S131",
            "javabugs:S6466",
            "java:S1068",
        ],
        "high": [
            "java:S3776",
            "java:S1541",
            "java:S138",
            "java:S1820",
            "java:S1448",
            "java:S107",
            "java:S4970",
        ],
    }
    return [
        issue for issue in issues if issue.get("rule") in complexity_map[complexity]
    ]


def main():
    organization = "dglalperen"
    project_key = "tasks-backend"
    # https://github.com/dglalperen/api_backend.git
    # https://github.com/dglalperen/server-backend.git
    # https://github.com/dglalperen/webchat-backend.git
    # https://github.com/dglalperen/quarkus-todo-app.git
    # https://github.com/dglalperen/flutter_admin_backend.git
    # https://github.com/dglalperen/simplQ-backend.git
    # project_key = "dglalperen_Online-Banking-System"

    issues = get_issues(project_key)
    print(f"Total Issues for {project_key}: {len(issues)}")
    if issues:
        filtered_issues = filter_issues(issues)
        print(f"Total Filtered Issues for {project_key}: {len(filtered_issues)}")
        print(60 * "-")
        print(f"Filtered Issues for {project_key}: {filtered_issues}")


if __name__ == "__main__":
    main()

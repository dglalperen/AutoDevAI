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

projects = [
    "java-rest-api",
    "spring-restful-mongodb",
    "Vehicles-API",
    "ecommerce-spring-reactjs",
    "DemoRestAPI",
    "resteasy-restfull-examples",
    "login-registration-backend",
    "grohe-ondus-api-java",
    "rest-api-testing-framework",
    "restaurant-manager",
    "rest-api-with-jpa-criteria",
    "bank-app-rest-api",
    "spring-boot-postgresql-jpa-hibernate-rest-api-demo",
    "SpringBoot_REST_API",
    "parking_backend",
    "rest-api-series",
    "restapi",
    "car-rental",
    "car-rental-1",
    "exercise-generator-2",
    "expense-tracker-rest-api",
    "api-rest-spring-boot",
    "expense-manager-api",
    "ebay-sdk",
    "server-backend",
    "webchat-backend",
    "SpigotRestAPI",
    "java2022-kodlamaio",
    "api_backend",
    "Rental-Car-Agency",
    "simplQ-backend",
    "rest-examples-java",
    "restChatApplication",
    "expense-tracker-api",
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


def get_filtered_issues(project_key, complexity="low"):
    """
    Get filtered issues for a given project key based on complexity.
    """
    issues = get_issues(project_key)
    print(f"Total Issues for {project_key}: {len(issues)}")
    print(30 * "-")
    if issues:
        filtered_issues = get_issues_by_complexity(issues, complexity)
        print(
            f"Filtered Issues for {project_key} (Complexity: {complexity}): {len(filtered_issues)}"
        )
        return filtered_issues
    else:
        print(f"No issues found for {project_key} with complexity: {complexity}")
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
    filtered_issues = [
        issue for issue in issues if issue.get("rule") in complexity_map[complexity]
    ]
    return filtered_issues


def main():
    organization = "dglalperen"

    for project_key in projects:
        print(f"Checking project: {project_key}")

        # Check for high complexity issues
        print("Checking high complexity issues...")
        high_complexity_issues = get_filtered_issues(project_key, complexity="high")
        print(30 * "-")

        if high_complexity_issues:
            print(
                f"High complexity issues found in project {project_key}: {len(high_complexity_issues)}"
            )
        else:
            print(f"NO HIGH COMPLEXITY ISSUES FOR PROJECT {project_key}.")


if __name__ == "__main__":
    main()

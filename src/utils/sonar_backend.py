import requests

sonar_rules = [
    "java:S2259", "javabugs:S6466", "java:S115", "java:S3655", "java:S138",
    "java:S1541", "java:S1820", "java:S1192", "java:S1143", "java:S2142",
    "java:S1774", "java:S2057", "java:S106", "java:S2390", "java:S3552",
    "java:S2095", "java:S4925", "java:S2699", "java:S3776", "java:S1448",
    "java:S107", "java:S3516", "java:S2190", "java:S3973", "java:S2692",
    "java:S2638", "java:S2447", "java:S131", "java:S4970", "java:S2252"
]

def get_projects(organization):
    """
    Get projects for a given organization.
    """
    response = requests.get(f"http://localhost:3000/projects?organization={organization}")
    if response.status_code == 200:
        return response.json().get('components', [])
    else:
        return None

def get_issues(project_key):
    """
    Get issues for a given project key.
    """
    response = requests.get(f"http://localhost:3000/issues?projects={project_key}")
    if response.status_code == 200:
        return response.json().get('issues', [])
    else:
        return None

def filter_issues(issues):
    """
    Filter issues based on predefined sonar rules.
    """
    return [issue for issue in issues if issue.get('rule') in sonar_rules]

def get_filtered_issues(project_key):
    """
    Get filtered issues for a given project key.
    """
    issues = get_issues(project_key)
    if issues:
        return filter_issues(issues)
    else:
        return None

def main():
    organization = "dglalperen"
    project_key = "dglalperen_Rental-Car-Agency"
    #projects = get_projects(organization)
    
    issues = get_issues(project_key)
    if issues:
        filtered_issues = filter_issues(issues)
        print(f"Total Filtered Issues for {project_key}: {len(filtered_issues)}")
        print(60*"-")
        print(f"Filtered Issues for {project_key}: {filtered_issues}")

if __name__ == "__main__":
    main()

import pandas as pd
import json

# Load the data
file_path = "issue_resolutions.log"
with open(file_path, "r") as file:
    log_data = [json.loads(line) for line in file]

# Convert to DataFrame
df = pd.DataFrame(log_data)

# Check the total number of issues and their summaries
total_issues = len(df)
issues_fixed_first_attempt = df[df["retries"] == 0].shape[0]
average_retries = df["retries"].mean()
rule_distribution = df["rule"].value_counts()

# Display summary
summary = {
    "Total Issues": total_issues,
    "Issues Fixed on First Attempt": issues_fixed_first_attempt,
    "Average Retries per Issue": average_retries,
    "Rule Distribution": rule_distribution.to_dict(),
}

print(summary)

import matplotlib.pyplot as plt

# Bar chart for rule distribution
plt.figure(figsize=(10, 6))
rule_distribution.plot(kind="bar", color="skyblue")
plt.title("Distribution of Issues by SonarQube Rule")
plt.xlabel("SonarQube Rule")
plt.ylabel("Number of Issues")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("rule_distribution.png")
plt.show()

# Pie chart for issues fixed on first attempt vs. retries
labels = ["First Attempt", "Retries"]
sizes = [issues_fixed_first_attempt, total_issues - issues_fixed_first_attempt]
colors = ["#ff9999", "#66b3ff"]
explode = (0.1, 0)  # explode 1st slice

plt.figure(figsize=(6, 6))
plt.pie(
    sizes,
    explode=explode,
    labels=labels,
    colors=colors,
    autopct="%1.1f%%",
    shadow=True,
    startangle=140,
)
plt.title("Proportion of Issues Fixed on First Attempt vs. Retries")
plt.savefig("first_attempt_vs_retries.png")
plt.show()

# Histogram of retries
plt.figure(figsize=(10, 6))
df["retries"].plot(
    kind="hist",
    bins=range(0, df["retries"].max() + 2),
    color="lightgreen",
    edgecolor="black",
)
plt.title("Histogram of Number of Retries")
plt.xlabel("Number of Retries")
plt.ylabel("Frequency")
plt.xticks(range(0, df["retries"].max() + 1))
plt.tight_layout()
plt.savefig("retries_histogram.png")
plt.show()

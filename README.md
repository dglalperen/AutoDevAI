# Project Title: AutoDevAI (Automated Further Development of Software with the Help of Artificial Intelligence)

## Description

AutoDevAI leverages Large Language Models (LLMs) and SonarQube to autonomously enhance Java software repositories. By integrating automated issue detection with AI-driven code refactoring, this project explores the potential of AI in streamlining and improving software development processes.

## Table of Contents

1. [Description](#Description)
2. [Installation](#Installation)
3. [Usage](#Usage)
4. [Project Structure](#Project-Structure)
5. [Milestones](#Milestones)
6. [Contributing](#Contributing)
7. [License](#License)
8. [Acknowledgments](#Acknowledgments)

## Installation

### Python Requirements

Generate the `requirements.txt`:

```bash
pipreqs --savepath=requirements.in && pip-compile
```

### Clone the Repository

```bash
git clone https://github.com/yourusername/AutoDevAI.git
```

## Usage

Detailed usage instructions coming soon.

## Project Structure

- `main.py`: The main script running the automated refactoring process.
- `utils/`: Contains helper modules for various functionalities like repository cloning, prompt preparation, and SonarQube integration.
- `README.md`: Project documentation.

## Project Milestones

### Milestone 1: Project Initialization

- [x] Initialize GitHub Repository
- [x] Setup basic project structure
- [x] Configure a README with project details

### Milestone 2: SonarQube Integration

- [x] Setup SonarQube locally or on a server
- [x] Configure SonarQube to scan Java projects
- [x] Fetch SonarQube analysis data via API

### Milestone 3: LLM Integration

- [x] Research and integrate LLM API
- [x] Design and test LLM prompts for code refactoring

### Milestone 4: Automated Refactoring

- [x] Implement system to apply AI suggestions to code
- [x] Create backups for comparison
- [x] Automated review and application of changes

### Milestone 5: Evaluation and Feedback Loop

- [ ] Re-run SonarQube analysis on refactored code
- [ ] Compare metrics pre- and post-refactoring
- [ ] Adjust LLM integration based on feedback

### Milestone 6: Documentation and Reporting

- [ ] Document the methodology and results
- [ ] Prepare a comprehensive report
- [ ] Update README with project outcomes

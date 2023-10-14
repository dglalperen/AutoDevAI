# Project Title: AutoDevAI (Automated Further Development of Software with the Help of Artificial Intelligence)

## Description

This project aims to leverage the capabilities of Large Language Models (LLM) and SonarQube to autonomously improve and evolve existing Java software repositories. Through multiple cycles of analysis, refactoring suggestions, and re-evaluation, the project seeks to assess the effectiveness of LLMs in software development.

## Table of Contents

1. [Description](#Description)
2. [Installation](#Installation)
3. [Usage](#Usage)
4. [Milestones](#Milestones)
5. [Contributing](#Contributing)
6. [License](#License)
7. [Acknowledgments](#Acknowledgments)

## Installation

### Python Requirements

To generate the `requirements.txt` file, run:

```bash
pipreqs --savepath=requirements.in && pip-compile
```

# Clone the repository

```bash
git clone https://github.com/yourusername/AutoDevAI.git
```

## Usage

soon to be filled

## Project Milestones

- [ ] **Milestone 1: Project Initialization**

  #### Tasks:

  - [ ] Initialize GitHub Repository
  - [ ] Setup basic project structure
  - [ ] Configure a README with project details

---

- [ ] **Milestone 2: SonarQube Integration**

  #### Tasks:

  - [ ] Setup SonarQube locally or on a server
  - [ ] Configure SonarQube to scan a sample Java project
  - [ ] Write a script to automate SonarQube scans
  - [ ] Fetch SonarQube analysis data via API

---

- [ ] **Milestone 3: Data Analysis**

  #### Tasks:

  - [ ] Parse SonarQube data for relevant metrics
  - [ ] Identify issues requiring refactoring or fixes
  - [ ] Design schema to store parsed data for LLM prompts

---

- [ ] **Milestone 4: LLM Integration**

  #### Tasks:

  - [ ] Research LLM APIs and select one for the project
  - [ ] Design LLM prompts based on identified issues
  - [ ] Fetch refactoring suggestions from LLM

---

- [ ] **Milestone 5: Code Refactoring**

  #### Tasks:

  - [ ] Implement a system to apply LLM suggestions to codebase
  - [ ] Create backups of original code for comparison
  - [ ] Manually review and commit changes

---

- [ ] **Milestone 6: Evaluation and Feedback Loop**

  #### Tasks:

  - [ ] Re-run SonarQube analysis on refactored code
  - [ ] Compare metrics pre- and post-refactoring
  - [ ] Fine-tune LLM prompts based on evaluation

---

- [ ] **Milestone 7: Documentation and Reporting**

  #### Tasks:

  - [ ] Document the methodology and results
  - [ ] Prepare a report summarizing findings
  - [ ] Update GitHub README with project outcomes

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Your mentors, advisors, or anyone else who helped you.

import os
import yaml
import requests
from pathlib import Path

OLLAMA_API_URL = "http://192.168.1.115:11435/api/generate"
MODEL_NAME = "codellama:7b-instruct"

### 1. ReAct Prompt Template
def react_prompt(snippet):
    return f"""
You are a Cisco ACI and Ansible expert using the ReAct method.

Analyze the following Ansible task YAML, keeping in mind that the goal is to use these tasks to deploy and maintain a Cisco ACI Fabric as infrastructure as code:

--- BEGIN SNIPPET ---
{snippet}
--- END SNIPPET ---

Use this format:
THOUGHT: <explanation of what it does, variables, assumptions>
ACTION: <suggest improvements or next task>
"""

### 2. Call Ollama API directly
def call_codellama(prompt):
    response = requests.post(
        OLLAMA_API_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7
        },
        timeout=180
    )
    response.raise_for_status()
    return response.json()["response"]

### 3. Walk all roles and tasks
def find_task_files(roles_path="./roles"):
    task_files = []
    for role_dir in Path(roles_path).iterdir():
        task_dir = role_dir / "tasks"
        if task_dir.exists():
            task_files += list(task_dir.rglob("*.yml"))
    return task_files

### 4. Analyze one file
def analyze_task_file(path):
    with open(path, "r") as f:
        content = f.read()
    prompt = react_prompt(content)
    return call_codellama(prompt)

### 5. Main loop
def main():
    task_files = find_task_files()
    results = {}

    for file_path in task_files:
        print(f" Analyzing: {file_path}")
        try:
            output = analyze_task_file(file_path)
            results[str(file_path)] = output
            print(output)
        except Exception as e:
            print(f" Error analyzing {file_path}: {e}")
        print("=" * 80)

    with open("aci_role_analysis.md", "w") as f:
        for path, analysis in results.items():
            f.write(f"## {path}\n{analysis}\n\n")

if __name__ == "__main__":
    main()

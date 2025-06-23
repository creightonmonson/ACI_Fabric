import os
import requests
from pathlib import Path

OLLAMA_API_URL = "http://192.168.1.115:11435/api/generate"
MODEL_NAME = "codellama:7b-instruct"

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

def call_codellama(prompt):
    response = requests.post(
        OLLAMA_API_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7
        },
        timeout=300
    )
    response.raise_for_status()
    return response.json()["response"]

def find_task_files(roles_path="./roles"):
    task_files = []
    for role_dir in Path(roles_path).iterdir():
        task_dir = role_dir / "tasks"
        if task_dir.exists():
            task_files += list(task_dir.rglob("*.yml"))
    return task_files

def interactive_review(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    
    print(f"\n🔍 Analyzing: {file_path}\n{'='*60}")
    prompt = react_prompt(content)
    llm_output = call_codellama(prompt)
    
    print(f"\n🤖 LLM OUTPUT:\n{llm_output}\n")
    
    user_response = input("🧠 Your response (press Enter to skip or type feedback):\n> ").strip()
    
    # Optional second prompt with your input as context
    if user_response:
        followup_prompt = f"""{prompt}
        
Previous Output:
{llm_output}

User Feedback:
{user_response}

Please refine your THOUGHT and ACTION using this feedback.
"""
        refined_output = call_codellama(followup_prompt)
    else:
        refined_output = llm_output

    return {
        "llm_output": llm_output,
        "user_feedback": user_response,
        "refined_output": refined_output
    }

def main():
    task_files = find_task_files()
    results = {}

    for file_path in task_files:
        try:
            result = interactive_review(file_path)
            results[str(file_path)] = result
        except Exception as e:
            print(f"❌ Error: {file_path} — {e}")

    with open("aci_role_analysis_with_feedback.md", "w") as f:
        for path, result in results.items():
            f.write(f"## {path}\n")
            f.write(f"### 🤖 Original LLM Output:\n{result['llm_output']}\n")
            if result['user_feedback']:
                f.write(f"### 🧠 Your Feedback:\n{result['user_feedback']}\n")
                f.write(f"### 🔁 Refined Output:\n{result['refined_output']}\n")
            f.write("\n" + "-"*80 + "\n\n")

if __name__ == "__main__":
    main()

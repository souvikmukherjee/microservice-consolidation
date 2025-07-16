import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Optionally: from tavily import TavilyClient

SAMPLE_SIZE = 20  # Number of files/dependencies to sample per project

def escape_curly_braces(s):
    if isinstance(s, str):
        return s.replace('{', '{{').replace('}', '}}')
    elif isinstance(s, list):
        return [escape_curly_braces(item) for item in s]
    elif isinstance(s, dict):
        return {escape_curly_braces(k): escape_curly_braces(v) for k, v in s.items()}
    else:
        return s

def find_java_projects(base_dir):
    projects = []
    for root, dirs, files in os.walk(base_dir):
        if "build.gradle" in files or "pom.xml" in files:
            projects.append(root)
    return projects

def extract_project_structure(project_dir):
    structure = []
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".java"):
                structure.append(os.path.relpath(os.path.join(root, file), project_dir))
    return structure

def extract_dependencies(project_dir):
    deps_path = os.path.join(project_dir, "extracted_dependencies.json")
    if os.path.exists(deps_path):
        with open(deps_path, "r") as f:
            try:
                deps = json.load(f)
                return deps
            except Exception:
                return []
    return []

def main():
    base_dir = "repos"  # Fixed path for your repo structure
    projects = find_java_projects(base_dir)
    print(f"Discovered {len(projects)} Java projects:")
    for p in projects:
        print(f"  - {p}")
    print()
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    for project in projects:
        print(f"\nAnalyzing project: {project}")
        structure = extract_project_structure(project)
        dependencies = extract_dependencies(project)
        # Sample the first N files and dependencies
        structure_sample = structure[:SAMPLE_SIZE]
        dependencies_sample = dependencies[:SAMPLE_SIZE]
        print(f"  Sampled {len(structure_sample)} files and {len(dependencies_sample)} dependencies.")
        # Escape curly braces for safe formatting
        structure_sample_esc = escape_curly_braces(structure_sample)
        dependencies_sample_esc = escape_curly_braces(dependencies_sample)
        prompt = (
            "You are a senior Java architect. Here is a sample of the project structure and dependencies for a microservice. "
            "Summarize the key characteristics, potential risks, and any notable patterns. "
            "Suggest any improvements or refactoring opportunities.\n\n"
            "Sampled Java files (relative paths):\n{structure}\n\n"
            "Sampled dependencies (name, version, source):\n{dependencies}\n"
        )
        prompt_filled = prompt.format(
            structure=json.dumps(structure_sample_esc, indent=2),
            dependencies=json.dumps(dependencies_sample_esc, indent=2)
        )
        print("  Sending prompt to LLM...")
        try:
            summary = llm.invoke(prompt_filled)
            print("\n--- LLM Summary ---")
            print(summary)
            print("-------------------\n")
        except Exception as e:
            print(f"  LLM analysis failed: {e}")

if __name__ == "__main__":
    main() 
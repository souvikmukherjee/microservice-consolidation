import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from visualization import generate_service_structure_mermaid, write_mermaid_to_markdown
import subprocess

# Placeholder for compatibility engine integration
# from compatibility_engine import ...

CONSOLIDATED_DIR = "consolidated-service"
REPOS_DIR = "repos"

# Step 1: Discover microservice repos

def find_microservice_repos(base_dir):
    print(f"[LOG] Scanning for microservice repos in '{base_dir}'...")
    repos = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    print(f"[LOG] Found {len(repos)} repos: {repos}")
    return repos

# Step 2: Extract summaries and recommendations

def extract_service_summary(repo_dir):
    print(f"[LOG] Extracting summary for repo: {repo_dir}")
    # Placeholder: extract APIs, dependencies, key files, etc.
    summary = {
        "name": os.path.basename(repo_dir),
        "api": [],
        "dependencies": [],
        "key_files": [],
        "compatibility": []
    }
    # TODO: Load from analysis results, extracted_dependencies.json, etc.
    return summary

def run_compatibility_engine():
    print("[LOG] Running compatibility-engine CLI for API and dependency conflict analysis...")
    # Run API conflict analysis
    subprocess.run([
        "python", "compatibility-engine/compatibility_engine.py", "api-conflict", "repos", "--output=compatibility-engine/compatibility_results/api_conflict_results.json"
    ], check=True)
    # Run dependency conflict analysis
    subprocess.run([
        "python", "compatibility-engine/compatibility_engine.py", "dependency-conflict", "repos"
    ], check=True)
    print("[LOG] Compatibility-engine CLI runs complete.")


def load_compatibility_results():
    api_conflicts_path = "compatibility-engine/compatibility_results/api_conflict_results.json"
    dep_conflicts_path = "compatibility-engine/compatibility_results/dependency_conflict_results.json"
    api_conflicts = []
    dep_conflicts = []
    try:
        with open(api_conflicts_path) as f:
            api_conflicts = json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load API conflict results: {e}")
    try:
        with open(dep_conflicts_path) as f:
            dep_conflicts = json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load dependency conflict results: {e}")
    return {"api_conflicts": api_conflicts, "dependency_conflicts": dep_conflicts}

def summarize_compatibility_results(compatibility_recs, max_items=10):
    api_conflicts = compatibility_recs.get("api_conflicts", [])
    dep_conflicts = compatibility_recs.get("dependency_conflicts", [])
    # Summarize API conflicts
    api_summary = []
    for c in api_conflicts[:max_items]:
        api_summary.append({
            "service_a": c.get("service_a"),
            "endpoint_a": c.get("endpoint_a", {}),
            "service_b": c.get("service_b"),
            "endpoint_b": c.get("endpoint_b", {}),
            "llm_reasoning": (c.get("llm_reasoning", "")[:200] + ("..." if len(c.get("llm_reasoning", "")) > 200 else ""))
        })
    # Summarize dependency conflicts
    dep_summary = []
    for c in dep_conflicts[:max_items]:
        dep_summary.append({
            "dependency": c.get("dependency"),
            "versions": c.get("versions"),
            "services": list(c.get("services", {}).keys()),
            "llm_reasoning": (c.get("llm_reasoning", "")[:200] + ("..." if len(c.get("llm_reasoning", "")) > 200 else ""))
        })
    return {"api_conflicts": api_summary, "dependency_conflicts": dep_summary}

# Step 3: LLM planning

def generate_merge_plan(service_summaries, compatibility_recs):
    print("[LOG] Generating merge plan using LLM...")
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    summarized_recs = summarize_compatibility_results(compatibility_recs)
    prompt_text = (
        "You are an expert Java microservice consolidation agent. "
        "You must use the compatibility-engine's CLI outputs for all conflict identification and resolution. "
        "Do not attempt to re-analyze code for conflicts yourself. "
        "Reference the files in 'compatibility-engine/compatibility_results/' for all API and dependency conflict data. "
        "Here are the summaries of the microservices: " + json.dumps(service_summaries, indent=2) + "\n\n"
        "Here is a summary of compatibility-engine results (API and dependency conflicts): " + json.dumps(summarized_recs, indent=2) + "\n\n"
        "Generate a detailed, step-by-step plan to consolidate these services into a single Java microservice. "
        "Include which files to merge, how to resolve conflicts (using the compatibility-engine's recommendations), and any refactoring needed. Output the plan as a JSON checklist."
    )
    plan = llm.invoke(prompt_text)
    print("[LOG] Merge plan received from LLM.")
    # Save the full plan to a file (ensure string)
    plan_str = plan.content if isinstance(plan.content, str) else str(plan.content)
    with open("consolidation_merge_plan.json", "w") as f:
        f.write(plan_str)
    print("[LOG] Saved full merge plan to consolidation_merge_plan.json")
    return plan

# Step 4: Python executor (placeholder)

def parse_merge_plan(plan):
    # plan is an LLM object with a 'content' attribute containing JSON
    try:
        plan_json = json.loads(plan.content)
        return plan_json.get("plan", [])
    except Exception as e:
        print(f"[ERROR] Failed to parse merge plan: {e}")
        return []

def execute_merge_plan(plan, service_summaries):
    print("[LOG] Executing merge plan...")
    steps = parse_merge_plan(plan)
    for step in steps:
        print(f"[STEP {step.get('step')}] {step.get('description')}")
    # TODO: Implement file copying/merging logic for each step
    # Log actions and update visualization as needed

# Main orchestration

def main():
    print("[LOG] Starting iMCE consolidation orchestrator...")
    os.makedirs(CONSOLIDATED_DIR, exist_ok=True)
    repos = find_microservice_repos(REPOS_DIR)
    service_summaries = [extract_service_summary(r) for r in repos]
    print("[LOG] Generating live service structure visualization...")
    mermaid_str = generate_service_structure_mermaid(service_summaries)
    write_mermaid_to_markdown(mermaid_str)
    print("[LOG] Wrote live service structure visualization to consolidation_progress.md")
    # --- Agentic A2A: Run compatibility-engine as CLI subprocess ---
    run_compatibility_engine()
    compatibility_recs = load_compatibility_results()
    plan = generate_merge_plan(service_summaries, compatibility_recs)
    print("\n--- Merge Plan (Step-by-step) ---\n")
    execute_merge_plan(plan, service_summaries)
    print("[LOG] Consolidation orchestrator run complete.")

if __name__ == "__main__":
    main() 
import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from visualization import generate_service_structure_mermaid, write_mermaid_to_markdown
import subprocess
import shutil
import re
import requests
import zipfile
import io

# Placeholder for compatibility engine integration
# from compatibility_engine import ...

CONSOLIDATED_DIR = "consolidated-service"
REPOS_DIR = "repos"

def purge_and_scaffold():
    # 1. Purge consolidated-service/
    import shutil
    if os.path.exists('consolidated-service'):
        for filename in os.listdir('consolidated-service'):
            file_path = os.path.join('consolidated-service', filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'[WARN] Failed to delete {file_path}: {e}')
    # 2. Create ms-imce subfolder
    target_dir = os.path.join('consolidated-service', 'ms-imce')
    os.makedirs(target_dir, exist_ok=True)
    # 3. Scaffold Spring Boot app using Spring Initializr
    print('[LOG] Downloading Spring Boot scaffold from Initializr...')
    url = (
        'https://start.spring.io/starter.zip?'
        'type=gradle-project&language=java&bootVersion=3.4.0'
        '&baseDir=ms-imce&groupId=com.imce.app&artifactId=ms-imce'
        '&name=ms-imce&packageName=com.imce.app&javaVersion=21'
        '&dependencies=web,data-jpa,actuator'
    )
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall('consolidated-service')
    print('[LOG] Spring Boot scaffold created in consolidated-service/ms-imce/')
    return target_dir

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
    # Use the compatibility-engine's virtual environment
    python_path = "compatibility-engine/venv/bin/python"
    
    # Run API conflict analysis
    subprocess.run([
        python_path, "compatibility-engine/compatibility_engine.py", "api-conflict", "repos", "--output=compatibility-engine/compatibility_results/api_conflict_results.json"
    ], check=True)
    # Run dependency conflict analysis
    subprocess.run([
        python_path, "compatibility-engine/compatibility_engine.py", "dependency-conflict", "repos"
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

def find_java_files(repo_path):
    """Find all Java source files in a repository."""
    java_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    return java_files

def extract_package_from_java(file_path):
    """Extract package declaration from a Java file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            package_match = re.search(r'package\s+([\w\.]+)\s*;', content)
            if package_match:
                return package_match.group(1)
    except Exception as e:
        print(f"[WARN] Could not read {file_path}: {e}")
    return None

def classify_java_file(file_path, content=None):
    """Classify Java file into Spring Boot package categories."""
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return 'other'
    
    filename = os.path.basename(file_path).lower()
    content_lower = content.lower()
    
    # Spring Boot main application
    if '@springbootapplication' in content_lower:
        return 'main'
    # Controllers
    elif '@controller' in content_lower or '@restcontroller' in content_lower:
        return 'controller'
    # Services
    elif '@service' in content_lower or 'service' in filename:
        return 'service'
    # Repositories
    elif '@repository' in content_lower or 'repository' in filename or 'dao' in filename:
        return 'repository'
    # Entities/Models
    elif '@entity' in content_lower or '@document' in content_lower or 'model' in filename or 'entity' in filename:
        return 'model'
    # Configuration
    elif '@configuration' in content_lower or 'config' in filename:
        return 'config'
    # DTOs
    elif 'dto' in filename or 'request' in filename or 'response' in filename:
        return 'dto'
    # Exceptions
    elif 'exception' in filename or 'error' in filename:
        return 'exception'
    # Utilities
    elif 'util' in filename or 'helper' in filename:
        return 'util'
    # Tests
    elif 'test' in filename:
        return 'test'
    else:
        return 'other'

def find_resource_files(repo_path):
    """Find all resource files (properties, yml, xml, etc.)."""
    resource_files = []
    resource_extensions = ['.properties', '.yml', '.yaml', '.xml', '.json', '.sql']
    
    for root, dirs, files in os.walk(repo_path):
        # Look specifically in resources directories
        if 'resources' in root or 'config' in root:
            for file in files:
                if any(file.endswith(ext) for ext in resource_extensions):
                    resource_files.append(os.path.join(root, file))
    return resource_files

def merge_properties_files(source_files, target_path):
    """Merge multiple .properties files intelligently."""
    merged_content = []
    merged_content.append("# Merged configuration from multiple microservices")
    merged_content.append("# Generated by iMCE consolidation orchestrator")
    merged_content.append("")
    
    for source_file in source_files:
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    merged_content.append(f"# === From {source_file} ===")
                    merged_content.append(content)
                    merged_content.append("")
        except Exception as e:
            print(f"[WARN] Could not read {source_file}: {e}")
    
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_content))

def execute_merge_plan(merge_plan, repos, consolidated_dir):
    print("[LOG] Executing merge plan...")
    
    # Package structure for consolidated service
    target_java_dir = os.path.join(consolidated_dir, 'src', 'main', 'java', 'com', 'imce', 'app')
    target_resources_dir = os.path.join(consolidated_dir, 'src', 'main', 'resources')
    target_test_dir = os.path.join(consolidated_dir, 'src', 'test', 'java', 'com', 'imce', 'app')
    
    # Create package directories
    package_dirs = {
        'controller': os.path.join(target_java_dir, 'controller'),
        'service': os.path.join(target_java_dir, 'service'),
        'repository': os.path.join(target_java_dir, 'repository'),
        'model': os.path.join(target_java_dir, 'model'),
        'config': os.path.join(target_java_dir, 'config'),
        'dto': os.path.join(target_java_dir, 'dto'),
        'exception': os.path.join(target_java_dir, 'exception'),
        'util': os.path.join(target_java_dir, 'util'),
        'other': os.path.join(target_java_dir, 'other'),
        'test': target_test_dir
    }
    
    for dir_path in package_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # Process each repository
    all_properties_files = []
    file_counter = {}  # Track duplicate filenames
    
    for repo in repos:
        print(f"[LOG] Processing repository: {repo}")
        
        # Process Java files
        java_files = find_java_files(repo)
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Classify the file
                file_type = classify_java_file(java_file, content)
                filename = os.path.basename(java_file)
                
                # Skip main application files (we already have one)
                if file_type == 'main':
                    print(f"[LOG] Skipping main application file: {java_file}")
                    continue
                
                # Handle duplicate filenames
                base_name = os.path.splitext(filename)[0]
                if filename in file_counter:
                    file_counter[filename] += 1
                    new_filename = f"{base_name}_{file_counter[filename]}.java"
                    print(f"[LOG] Renaming duplicate {filename} -> {new_filename}")
                    filename = new_filename
                else:
                    file_counter[filename] = 1
                
                # Determine target directory
                target_dir = package_dirs.get(file_type, package_dirs['other'])
                target_file = os.path.join(target_dir, filename)
                
                # Update package declaration to match new structure
                new_package = f"com.imce.app.{file_type}" if file_type != 'main' else "com.imce.app"
                if file_type == 'test':
                    new_package = "com.imce.app"
                
                # Replace package declaration
                updated_content = re.sub(
                    r'package\s+[\w\.]+\s*;',
                    f'package {new_package};',
                    content
                )
                
                # Write the file
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"[LOG] Copied and organized: {java_file} -> {target_file}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process {java_file}: {e}")
        
        # Collect resource files
        resource_files = find_resource_files(repo)
        for resource_file in resource_files:
            if resource_file.endswith('.properties'):
                all_properties_files.append(resource_file)
            else:
                # Copy other resource files directly
                filename = os.path.basename(resource_file)
                target_file = os.path.join(target_resources_dir, filename)
                
                if not os.path.exists(target_file):
                    try:
                        shutil.copy2(resource_file, target_file)
                        print(f"[LOG] Copied resource: {resource_file} -> {target_file}")
                    except Exception as e:
                        print(f"[ERROR] Failed to copy {resource_file}: {e}")
    
    # Merge all properties files
    if all_properties_files:
        target_properties = os.path.join(target_resources_dir, 'application.properties')
        merge_properties_files(all_properties_files, target_properties)
        print(f"[LOG] Merged {len(all_properties_files)} properties files -> {target_properties}")
    
    print("[LOG] Merge execution complete.")
    print(f"[LOG] Consolidated Spring Boot application structure created in: {consolidated_dir}")
    print("[LOG] Package structure:")
    for pkg_type, pkg_dir in package_dirs.items():
        if os.path.exists(pkg_dir):
            file_count = len([f for f in os.listdir(pkg_dir) if f.endswith('.java')])
            if file_count > 0:
                print(f"  - {pkg_type}: {file_count} files")

# Main orchestration

def main():
    print("[LOG] Starting iMCE consolidation orchestrator...")
    # os.makedirs(CONSOLIDATED_DIR, exist_ok=True) # This line is removed as consolidation_dir is now scaffolded
    target_dir = purge_and_scaffold()
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
    with open("consolidation_merge_plan.json") as f:
        merge_plan = json.load(f)
    execute_merge_plan(merge_plan, repos, consolidated_dir=target_dir)
    print("[LOG] Consolidation orchestrator run complete.")

if __name__ == "__main__":
    main() 
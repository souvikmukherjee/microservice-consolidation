import os
import json
import csv
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def load_dependencies_from_extracted(repo_dir: str):
    deps = []
    for root, dirs, files in os.walk(repo_dir):
        if 'extracted_dependencies.json' in files:
            path = os.path.join(root, 'extracted_dependencies.json')
            with open(path, 'r') as f:
                try:
                    data = json.load(f)
                    service_name = os.path.basename(root)
                    for dep in data:
                        dep['service'] = service_name
                        deps.append(dep)
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
    return deps

def aggregate_dependency_versions(dependency_list):
    dep_map = {}
    for dep in dependency_list:
        name = dep.get('name')
        version = dep.get('version')
        service = dep.get('service')
        if not name or version is None or service is None:
            continue
        if name not in dep_map:
            dep_map[name] = {}
        if version not in dep_map[name]:
            dep_map[name][version] = []
        dep_map[name][version].append(service)
    return dep_map

def escape_curly_braces(s):
    return s.replace('{', '{{').replace('}', '}}')

def llm_reason_dependency_conflict(dep_name, versions_services, llm):
    # Escape curly braces in all relevant strings
    dep_name_esc = escape_curly_braces(dep_name)
    versions = [escape_curly_braces(v) for v in versions_services.keys()]
    services = {escape_curly_braces(v): versions_services[v] for v in versions_services}
    latest_version = sorted(versions, reverse=True)[0] if versions else None
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Java dependency manager. Given the following dependency and its versions across multiple microservices, determine if there is a conflict, what the risks are, and recommend a resolution. If there are multiple versions, recommend updating all services to the latest version unless there is a strong reason not to. If all services use the same version, confirm there is no conflict and explain why."),
        ("human", f"Dependency: {dep_name_esc}\nVersions found: {', '.join(versions)}\nService usage: " + ", ".join([f'{v}: {', '.join(services[v])}' for v in versions]) + (f"\nLatest version: {latest_version}" if latest_version else "") + "\nPlease provide a clear recommendation.")
    ])
    variables = {
        "dep_name": dep_name_esc,
        "versions": versions,
        "services": services,
        "latest_version": latest_version
    }
    prompt = prompt_template.format(**variables)
    response = llm.invoke(prompt)
    return response.content

def find_dependency_conflicts_semantic(repos_dir: str, output_path: Optional[str] = None) -> List[Dict]:
    dependency_list = load_dependencies_from_extracted(repos_dir)
    dep_map = aggregate_dependency_versions(dependency_list)
    # Build a map of dep_name -> set of services
    dep_services = {}
    for dep in dependency_list:
        name = dep.get('name')
        service = dep.get('service')
        if name and service:
            dep_services.setdefault(name, set()).add(service)
    # Only analyze dependencies present in more than one service
    filtered_dep_map = {dep_name: versions_services for dep_name, versions_services in dep_map.items() if len(dep_services.get(dep_name, set())) > 1}
    llm = ChatOpenAI(model="gpt-4o")
    results = []
    for dep_name, versions_services in filtered_dep_map.items():
        print(f"Analyzing {dep_name}: {list(versions_services.keys())}")
        reasoning = llm_reason_dependency_conflict(dep_name, versions_services, llm)
        results.append({
            'dependency': dep_name,
            'versions': list(versions_services.keys()),
            'services': versions_services,
            'llm_reasoning': reasoning
        })
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults written to {output_path}")
        # Also write to CSV
        csv_path = output_path.replace('.json', '.csv')
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['dependency', 'versions', 'services', 'llm_reasoning']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({
                    'dependency': r['dependency'],
                    'versions': ", ".join(r['versions']),
                    'services': json.dumps(r['services']),
                    'llm_reasoning': r['llm_reasoning']
                })
        print(f"Results written to {csv_path}")
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python dependency_conflict.py <repos_dir> [output_path]")
        sys.exit(1)
    repos_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    find_dependency_conflicts_semantic(repos_dir, output_path)

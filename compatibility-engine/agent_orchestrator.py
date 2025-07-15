import os
import subprocess
import json
import csv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
REPOS_DIR = os.path.join(PROJECT_ROOT, "repos")
SPRINGBOOT_BACKEND_DIR = os.path.join(PROJECT_ROOT, "springboot-backend")
ANALYSIS_FILENAME = "analysis_result.json"
JAR_NAME = "springboot-backend-0.0.1-SNAPSHOT-all.jar"
JAR_PATH = os.path.join(SPRINGBOOT_BACKEND_DIR, "build", "libs", JAR_NAME)


def build_java_jar():
    print(f"Building Java analysis JAR (fat JAR with dependencies) in {SPRINGBOOT_BACKEND_DIR} ...")
    subprocess.run(["./gradlew", "clean", "shadowJar"], cwd=SPRINGBOOT_BACKEND_DIR, check=True)
    print(f"JAR built at {JAR_PATH}")


def discover_repos(repos_dir=REPOS_DIR):
    return [
        os.path.join(repos_dir, d)
        for d in os.listdir(repos_dir)
        if os.path.isdir(os.path.join(repos_dir, d))
    ]


def check_analysis_file(repo_path):
    return os.path.exists(os.path.join(repo_path, ANALYSIS_FILENAME))


def run_java_analysis(repo_path):
    # Pass repo_path as './repos/<name>' (with leading './')
    rel_repo_path = os.path.relpath(repo_path, PROJECT_ROOT)
    if not rel_repo_path.startswith("./"):  # ensure leading './'
        rel_repo_path = f"./{rel_repo_path}"
    cmd = [
        "java", "-cp", JAR_PATH,
        "com.example.springboot_backend.RepoAnalysisModule", rel_repo_path
    ]
    print(f"Running Java analysis: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    return f"Analysis complete for {rel_repo_path}"


def load_all_endpoints():
    """Load endpoints from all analysis_result.json files, grouped by service (repo name)."""
    endpoints_by_service = {}
    for repo in discover_repos():
        analysis_path = os.path.join(repo, ANALYSIS_FILENAME)
        if os.path.exists(analysis_path):
            with open(analysis_path) as f:
                data = json.load(f)
                service = os.path.basename(repo)
                endpoints_by_service[service] = data.get("endpoints", [])
    return endpoints_by_service


def get_all_cross_service_pairs(endpoints_by_service):
    pairs = []
    services = list(endpoints_by_service.keys())
    for i, service_a in enumerate(services):
        for service_b in services[i+1:]:
            for ep_a in endpoints_by_service[service_a]:
                for ep_b in endpoints_by_service[service_b]:
                    pairs.append((service_a, ep_a, service_b, ep_b))
    return pairs


def llm_api_conflict(ep1, ep2, service_a, service_b, llm):
    messages = [
        SystemMessage(content="You are an expert API reviewer. Your job is to determine if two REST API endpoints from different microservices are functionally equivalent, conflicting, or unrelated. Consider HTTP method, path, and context. Respond with 'Conflict', 'Equivalent', or 'No Conflict', and explain your reasoning."),
        HumanMessage(content=(
            f"Service A: {service_a}\nEndpoint 1: {ep1['httpMethod']} {ep1['path']} (Class: {ep1.get('className')}, Method: {ep1.get('methodName')})\n"
            f"Service B: {service_b}\nEndpoint 2: {ep2['httpMethod']} {ep2['path']} (Class: {ep2.get('className')}, Method: {ep2.get('methodName')})"
        ))
    ]
    response = llm.invoke(messages)
    return response.content


def orchestrate_analysis():
    build_java_jar()
    repos = discover_repos()
    for repo in repos:
        if not check_analysis_file(repo):
            print(f"No analysis file found for {repo}. Running static analysis...")
            run_java_analysis(repo)
        else:
            print(f"Analysis file already exists for {repo}.")
    print("All repos analyzed. Ready for LLM reasoning.")

    # --- LLM Reasoning Pipeline ---
    endpoints_by_service = load_all_endpoints()
    print(f"Loaded endpoints for services: {list(endpoints_by_service.keys())}")
    pairs = get_all_cross_service_pairs(endpoints_by_service)
    print(f"Total cross-service endpoint pairs: {len(pairs)}")

    llm = ChatOpenAI(model="gpt-4o")
    results = []
    for idx, (service_a, ep1, service_b, ep2) in enumerate(pairs):
        print(f"\n[{idx+1}/{len(pairs)}] Analyzing: {service_a} {ep1['httpMethod']} {ep1['path']} <-> {service_b} {ep2['httpMethod']} {ep2['path']}")
        reasoning = llm_api_conflict(ep1, ep2, service_a, service_b, llm)
        print(f"LLM Reasoning: {reasoning}")
        results.append({
            'service_a': service_a,
            'endpoint_a': ep1,
            'service_b': service_b,
            'endpoint_b': ep2,
            'llm_reasoning': reasoning
        })

    # Output to JSON
    with open("api_conflict_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults written to api_conflict_results.json")

    # Output to CSV
    with open("api_conflict_results.csv", "w", newline='') as csvfile:
        fieldnames = [
            'service_a', 'endpoint_a_class', 'endpoint_a_method', 'endpoint_a_http', 'endpoint_a_path',
            'service_b', 'endpoint_b_class', 'endpoint_b_method', 'endpoint_b_http', 'endpoint_b_path',
            'llm_reasoning'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                'service_a': r['service_a'],
                'endpoint_a_class': r['endpoint_a'].get('className'),
                'endpoint_a_method': r['endpoint_a'].get('methodName'),
                'endpoint_a_http': r['endpoint_a'].get('httpMethod'),
                'endpoint_a_path': r['endpoint_a'].get('path'),
                'service_b': r['service_b'],
                'endpoint_b_class': r['endpoint_b'].get('className'),
                'endpoint_b_method': r['endpoint_b'].get('methodName'),
                'endpoint_b_http': r['endpoint_b'].get('httpMethod'),
                'endpoint_b_path': r['endpoint_b'].get('path'),
                'llm_reasoning': r['llm_reasoning']
            })
    print("Results written to api_conflict_results.csv")


if __name__ == "__main__":
    orchestrate_analysis() 
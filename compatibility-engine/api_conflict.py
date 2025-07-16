import os
import json
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# Helper to load endpoints from analysis_result.json

def load_endpoints_from_analysis(analysis_path: str):
    with open(analysis_path, 'r') as f:
        data = json.load(f)
    endpoints = data.get('endpoints', [])
    service_name = os.path.basename(os.path.dirname(analysis_path))
    for ep in endpoints:
        ep['service'] = service_name
    return endpoints

# Generate all cross-service endpoint pairs (Cartesian product, all methods)
def get_all_cross_service_pairs_all_methods(endpoints):
    pairs = []
    n = len(endpoints)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            ep1, ep2 = endpoints[i], endpoints[j]
            if ep1['service'] == ep2['service']:
                continue
            # Only pair endpoints with the same HTTP method
            if ep1.get('httpMethod') != ep2.get('httpMethod'):
                continue
            pairs.append((ep1, ep2))
    return pairs

# Use LangChain + GPT-4o to reason about endpoint pairs

def llm_reason_conflict(ep1, ep2, llm):
    messages = [
        SystemMessage(content="You are an expert API reviewer. Your job is to determine if two REST API endpoints are functionally equivalent or conflicting, even if their path parameters differ. Consider HTTP method, path, and context. Respond with 'Conflict', 'Equivalent', or 'No Conflict', and explain your reasoning."),
        HumanMessage(content=(
            f"Endpoint 1: {ep1['httpMethod']} {ep1['path']} (Service: {ep1['service']}, Class: {ep1.get('className')}, Method: {ep1.get('methodName')})\n"
            f"Endpoint 2: {ep2['httpMethod']} {ep2['path']} (Service: {ep2['service']}, Class: {ep2.get('className')}, Method: {ep2.get('methodName')})"
        ))
    ]
    response = llm.invoke(messages)
    return response.content

def find_api_conflicts_semantic(repos_dir: str, output_path: Optional[str] = None) -> List[Dict]:
    endpoint_list = []
    for root, dirs, files in os.walk(repos_dir):
        for file in files:
            if file == 'analysis_result.json':
                analysis_path = os.path.join(root, file)
                endpoint_list.extend(load_endpoints_from_analysis(analysis_path))
    pairs = get_all_cross_service_pairs_all_methods(endpoint_list)
    if not pairs:
        print("No cross-service endpoint pairs found for semantic analysis.")
        return []
    # Setup LangChain LLM (GPT-4o)
    llm = ChatOpenAI(model="gpt-4o")
    results = []
    for ep1, ep2 in pairs:
        print(f"\nAnalyzing: {ep1['httpMethod']} {ep1['path']} (Service: {ep1['service']}) <-> {ep2['httpMethod']} {ep2['path']} (Service: {ep2['service']})")
        reasoning = llm_reason_conflict(ep1, ep2, llm)
        print(f"LLM Reasoning: {reasoning}")
        results.append({
            'ep1': ep1,
            'ep2': ep2,
            'llm_reasoning': reasoning
        })
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults written to {output_path}")
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python api_conflict.py <repos_dir> [output_path]")
        sys.exit(1)
    repos_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    find_api_conflicts_semantic(repos_dir, output_path)

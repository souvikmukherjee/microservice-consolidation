import os
import json
import logging
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def find_build_files(repo_dir):
    gradle_files = []
    maven_files = []
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file == "build.gradle":
                gradle_files.append(os.path.join(root, file))
            elif file == "pom.xml":
                maven_files.append(os.path.join(root, file))
    return gradle_files, maven_files

def extract_json_from_llm_response(response_content):
    """
    Strips all markdown code block markers (lines starting with ```) from the LLM response.
    """
    lines = response_content.strip().splitlines()
    cleaned_lines = [line for line in lines if not line.strip().startswith('```')]
    cleaned = '\n'.join(cleaned_lines).strip()
    return cleaned

def extract_dependencies_with_llm(file_path, file_type, llm, debug_first_maven=False):
    with open(file_path, "r") as f:
        content = f.read()
    prompt = (
        f"You are an expert Java build tool analyst. Given the following {file_type} file, extract all dependencies (including those defined via variables, plugins, or parent POMs) and output them as a JSON array of objects with 'name' (group:artifact) and 'version'. If a version is inherited or managed, resolve it if possible. Only output the JSON array, no explanation.\n\n"
        f"{content}"
    )
    if debug_first_maven:
        logger.info(f"[DEBUG] Outgoing prompt for {file_path} (full):\n{prompt}")
    else:
        logger.info(f"Sending prompt to LLM for {file_path} (first 500 chars):\n{prompt[:500]}{'...' if len(prompt) > 500 else ''}")
    response = llm.invoke(prompt)
    if debug_first_maven:
        logger.info(f"[DEBUG] Full LLM response for {file_path}:\n{getattr(response, 'content', str(response))}")
    else:
        logger.info(f"Raw LLM response for {file_path} (first 500 chars):\n{getattr(response, 'content', str(response))[:500]}{'...' if len(getattr(response, 'content', str(response))) > 500 else ''}")
    try:
        cleaned = extract_json_from_llm_response(response.content)
        if debug_first_maven:
            logger.info(f"[DEBUG] Cleaned LLM response for {file_path}:\n{cleaned}")
        deps = json.loads(cleaned)
        for dep in deps:
            dep["source"] = file_type
            dep["path"] = file_path
        return deps
    except Exception as e:
        logger.error(f"Failed to parse dependencies from {file_path}: {e}\nRaw response: {getattr(response, 'content', str(response))}")
        if debug_first_maven:
            logger.error(f"[DEBUG] Cleaned response before parsing error for {file_path}:\n{cleaned}")
        return []

def main(repo_dir):
    gradle_files, maven_files = find_build_files(repo_dir)
    logger.info(f"Found {len(gradle_files)} build.gradle files and {len(maven_files)} pom.xml files in {repo_dir}")
    llm = ChatOpenAI(model="gpt-4o")
    all_deps = []
    for gradle_file in gradle_files:
        logger.info(f"Extracting dependencies from {gradle_file}")
        all_deps.extend(extract_dependencies_with_llm(gradle_file, "build.gradle", llm))
    logger.info(f"[DEBUG] Number of Maven files found: {len(maven_files)}")
    for idx, maven_file in enumerate(maven_files):
        logger.info(f"Extracting dependencies from {maven_file}")
        debug_first = (idx == 0)
        all_deps.extend(extract_dependencies_with_llm(maven_file, "pom.xml", llm, debug_first_maven=debug_first))
    output_path = os.path.join(repo_dir, "extracted_dependencies.json")
    with open(output_path, "w") as f:
        json.dump(all_deps, f, indent=2)
    logger.info(f"Extracted dependencies written to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logger.error("Usage: python agentic_dependency_extractor.py <repo_dir>")
        sys.exit(1)
    main(sys.argv[1]) 
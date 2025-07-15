import re
from github import Github
from github.GithubException import UnknownObjectException, GithubException

GITHUB_REPO_REGEX = re.compile(r'^(https://github.com/|git@github.com:)([\w.-]+)/([\w.-]+)(.git)?/?$')

def is_valid_github_url(url):
    """
    Checks if the provided URL matches the GitHub repository pattern.
    Returns (owner, repo) if valid, else None.
    """
    match = GITHUB_REPO_REGEX.match(url)
    if match:
        owner = match.group(2)
        repo = match.group(3)
        return owner, repo
    return None

def repo_exists(github_client, url):
    """
    Checks if the repository exists and is accessible using the authenticated Github client.
    Returns True if accessible, False otherwise.
    """
    parsed = is_valid_github_url(url)
    if not parsed:
        print(f"Invalid GitHub repository URL: {url}")
        return False
    owner, repo = parsed
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        print(f"Repository '{owner}/{repo}' exists and is accessible.")
        return True
    except UnknownObjectException:
        print(f"Repository '{owner}/{repo}' does not exist or is not accessible.")
        return False
    except GithubException as e:
        print(f"Error accessing repository: {e}")
        return False

def extract_repo_metadata(github_client, url):
    """
    Extracts metadata from a GitHub repository using the authenticated Github client.
    Returns a dictionary with key details or None if not accessible.
    """
    parsed = is_valid_github_url(url)
    if not parsed:
        print(f"Invalid GitHub repository URL: {url}")
        return None
    owner, repo = parsed
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        metadata = {
            "name": repository.name,
            "full_name": repository.full_name,
            "description": repository.description,
            "owner": repository.owner.login,
            "private": repository.private,
            "size_kb": repository.size,
            "stargazers_count": repository.stargazers_count,
            "forks_count": repository.forks_count,
            "open_issues_count": repository.open_issues_count,
            "default_branch": repository.default_branch,
            "created_at": str(repository.created_at),
            "updated_at": str(repository.updated_at),
            "html_url": repository.html_url
        }
        print(f"Metadata for '{owner}/{repo}':\n{metadata}")
        return metadata
    except Exception as e:
        print(f"Failed to extract metadata for '{owner}/{repo}': {e}")
        return None

def list_all_files(github_client, owner, repo):
    """
    Lists all files in a GitHub repository using the tree API (recursive).
    Handles large repositories efficiently.
    """
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        sha = repository.get_branch(repository.default_branch).commit.sha
        tree = repository.get_git_tree(sha=sha, recursive=True)
        files = [item.path for item in tree.tree if item.type == 'blob']
        print(f"Total files found in {owner}/{repo}: {len(files)}")
        # Optionally, print the first 10 files as a sample
        print("Sample files:", files[:10])
        return files
    except Exception as e:
        print(f"Error listing files in {owner}/{repo}: {e}")
        return []

def demo():
    from github_auth import authenticate_github
    github_client = authenticate_github()
    if not github_client:
        print("GitHub authentication failed. Cannot proceed.")
        return
    test_urls = [
        "https://github.com/octocat/Hello-World",
        "git@github.com:octocat/Hello-World.git",
        "https://github.com/invalid/repo",
        "not-a-github-url"
    ]
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        if is_valid_github_url(url):
            repo_exists(github_client, url)
            extract_repo_metadata(github_client, url)
        else:
            print("Invalid GitHub URL format.")
    # Demo for large repo: apache/dubbo
    print("\n--- Large Repository File Listing Demo: apache/dubbo ---")
    list_all_files(github_client, "apache", "dubbo")

if __name__ == "__main__":
    demo() 
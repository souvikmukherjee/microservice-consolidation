import os
from github import Github
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def authenticate_github():
    token = os.getenv('GITHUB_TOKEN') or os.getenv('github_token') or os.getenv('github_token'.upper())
    # Debug: Print which variable is loaded and the token (masked)
    if os.getenv('GITHUB_TOKEN'):
        print("Loaded token from GITHUB_TOKEN")
    elif os.getenv('github_token'):
        print("Loaded token from github_token")
    elif os.getenv('github_token'.upper()):
        print("Loaded token from GITHUB_TOKEN (lowercase)")
    else:
        print("No GitHub token found in environment variables.")
    if token:
        print(f"Token loaded: {token[:6]}...{token[-4:]}")
    else:
        raise ValueError("GitHub token not found in environment variables. Please set 'GITHUB_TOKEN' or 'github_token' in your .env file.")
    try:
        g = Github(token)
        user = g.get_user()
        print(f"Authenticated as: {user.login}")
        return g
    except Exception as e:
        print(f"Failed to authenticate with GitHub: {e}")
        return None

if __name__ == "__main__":
    authenticate_github() 
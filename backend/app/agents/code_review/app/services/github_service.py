import os
import tempfile
import shutil
from github import Github
from git import Repo
from typing import Dict, Any
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv(override=True)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER = os.getenv('GITHUB_USER')

print(f"GitHub Service - Token loaded: {'Yes' if GITHUB_TOKEN else 'No'}")
print(f"GitHub Service - User: {GITHUB_USER}")

def clone_repo(url, dest_dir):
    """Clone GitHub repository"""
    dest = os.path.join(dest_dir, 'repo')
    
    # Clean and validate URL
    url = url.strip()  # Remove leading/trailing spaces
    url = ' '.join(url.split())  # Remove extra spaces in middle
    
    # Handle different URL formats
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', 'https://github.com/')
    
    if not url.endswith('.git'):
        url += '.git'
    
    print(f"Cloning from: {url}")
    Repo.clone_from(url, dest)
    return dest

def push_new_repo(repo_path, original_repo_url, github_token=None):
    """Push changes to original repository"""
    push_enabled = os.getenv('PUSH_ENABLED', 'false').lower() == 'true'
    
    # Use provided token or fall back to environment variable
    token = github_token or GITHUB_TOKEN
    
    print(f"Push enabled: {push_enabled}")
    print(f"GitHub token exists: {'Yes' if token else 'No'}")
    print(f"GitHub user: {GITHUB_USER}")
    
    if not push_enabled or not token:
        print("Push disabled or missing token")
        return original_repo_url
    
    try:
        # Initialize GitHub client
        github = Github(token)
        user = github.get_user()
        
        print(f"Authenticated as: {user.login}")
        
        # Get the repo object from cloned directory
        repo = Repo(repo_path)
        
        # Configure git user
        repo.config_writer().set_value("user", "name", user.login).release()
        repo.config_writer().set_value("user", "email", f"{user.login}@users.noreply.github.com").release()
        
        # Add all changes
        repo.git.add(A=True)
        
        # Check if there are changes to commit
        if repo.is_dirty() or repo.untracked_files:
            repo.index.commit('Auto-fixed code based on scan report')
            print("Committed changes")
        else:
            print("No changes to commit")
            return original_repo_url
        
        # Get authenticated URL for pushing
        auth_url = original_repo_url.replace('https://github.com/', f'https://{token}@github.com/')
        if not auth_url.endswith('.git'):
            auth_url += '.git'
        
        # Update origin remote
        try:
            origin = repo.remote('origin')
            origin.set_url(auth_url)
        except:
            origin = repo.create_remote('origin', auth_url)
        
        # Detect default branch
        try:
            current_branch = repo.active_branch.name
            print(f"Current branch: {current_branch}")
        except:
            current_branch = 'main'
        
        # Push to original repo
        try:
            origin.push(current_branch)
            print(f"Successfully pushed to {current_branch} branch")
            return original_repo_url
        except Exception as e:
            print(f"Push to {current_branch} failed: {e}")
            # Try alternate branch
            alt_branch = 'master' if current_branch == 'main' else 'main'
            try:
                origin.push(alt_branch)
                print(f"Successfully pushed to {alt_branch} branch")
                return original_repo_url
            except Exception as e2:
                print(f"Push to {alt_branch} also failed: {e2}")
                return original_repo_url
        
    except Exception as e:
        print(f"GitHub push error: {str(e)}")
        return original_repo_url

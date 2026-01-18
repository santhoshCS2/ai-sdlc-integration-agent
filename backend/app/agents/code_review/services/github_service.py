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

def clone_repo(url, dest_dir, token=None):
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
    
    # Use token if provided for private repos
    clone_url = url
    if token and "github.com" in url:
        clone_url = url.replace('https://github.com/', f'https://{token}@github.com/')
    
    print(f"Cloning from: {url}")
    Repo.clone_from(clone_url, dest)
    return dest

def push_new_repo(repo_path, original_repo_url, github_token=None, commit_message="Update", skip_env_check=False):
    """
    Push changes to a NEW repository (or update existing if new creation fails).
    """
    push_enabled = os.getenv('PUSH_ENABLED', 'false').lower() == 'true'
    
    # Use provided token or fall back to environment variable
    token = github_token or GITHUB_TOKEN
    
    print(f"Push enabled env: {push_enabled}")
    print(f"Skip env check: {skip_env_check}")
    
    if not token:
        print("Missing GitHub token")
        return original_repo_url
        
    if not push_enabled and not skip_env_check:
        print("Push disabled by environment")
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
            try:
                repo.index.commit(commit_message)
                print("Committed changes")
            except Exception as e:
                print(f"Commit failed (might be nothing to commit): {e}")
        else:
            print("No changes to commit")
            # Even if no changes, we might want to check the repo situation, 
            # but usually we just return raw url
            return original_repo_url
        
        # LOGIC TO CREATE NEW REPOSITORY
        original_name = original_repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        new_repo_name = f"{original_name}-fixed-{str(uuid.uuid4())[:8]}"
        
        try:
            print(f"Creating new repository: {new_repo_name}")
            new_gh_repo = user.create_repo(
                new_repo_name,
                description=f"Automated fix of {original_name} by Code Review Agent",
                private=True # Default to private for safety
            )
            new_repo_url = new_gh_repo.html_url
            print(f"Created new repo: {new_repo_url}")
            
            # Construct auth URL for pushing
            auth_url = new_repo_url.replace('https://github.com/', f'https://{token}@github.com/')
            if not auth_url.endswith('.git'):
                auth_url += '.git'
                
            # Add new remote
            try:
                repo.create_remote('new_origin', auth_url)
                remote = repo.remote('new_origin')
            except ValueError:
                remote = repo.remote('new_origin')
                remote.set_url(auth_url)
                
            # Push to new repo main branch
            print(f"Pushing to {new_repo_url}...")
            remote.push('refs/heads/main:refs/heads/main', force=True)
            return new_repo_url

        except Exception as create_e:
            print(f"Failed to create new repo: {create_e}")
            print("Falling back to pushing to original repo...")
            
            # Fallback: Push to original
            org_auth_url = original_repo_url.replace('https://github.com/', f'https://{token}@github.com/')
            try:
                origin = repo.remote('origin')
                origin.set_url(org_auth_url)
            except:
                origin = repo.create_remote('origin', org_auth_url)
            
            origin.push()
            return original_repo_url
        
    except Exception as e:
        print(f"GitHub push/create error: {str(e)}")
        return original_repo_url

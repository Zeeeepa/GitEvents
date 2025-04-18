import os
import logging
import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import threading
import time

from github import Github
from github.Repository import Repository
from github.Branch import Branch
from github.PullRequest import PullRequest

logger = logging.getLogger(__name__)

class AutoBranchPRManager:
    """
    Manages automatic PR creation from branches and post-merge script execution.
    Features:
    1. Auto-create PRs for new branches
    2. Execute scripts after PR merges
    """
    
    def __init__(self, config_path: str = "auto_branch_pr_config.json"):
        """Initialize the manager with configuration path"""
        self.config_path = config_path
        self.github_client = None
        self.config = self._load_config()
        self.branch_monitor_thread = None
        self.running = False
    
    def initialize(self, github_token: str) -> bool:
        """Initialize with GitHub token"""
        try:
            self.github_client = Github(github_token)
            logger.info("Auto Branch PR Manager initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing Auto Branch PR Manager: {e}")
            return False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "auto_pr_enabled": False,
            "auto_pr_settings": {
                "title_template": "PR for branch: {branch_name}",
                "body_template": "Automatically created PR for branch `{branch_name}`.",
                "base_branch": "main",
                "auto_assign_creator": True,
                "excluded_branches": ["main", "master", "dev", "develop", "release", "hotfix"],
                "included_repos": []
            },
            "post_merge_scripts": {
                "enabled": False,
                "scripts": []
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                    # Merge with default config to ensure all fields exist
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in loaded_config[key]:
                                    loaded_config[key][subkey] = subvalue
                    return loaded_config
            else:
                # Save default config
                with open(self.config_path, "w") as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config
    
    def save_config(self) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update configuration with new settings"""
        try:
            # Update only the fields that are provided
            for key, value in new_config.items():
                if key in self.config:
                    if isinstance(value, dict) and isinstance(self.config[key], dict):
                        self.config[key].update(value)
                    else:
                        self.config[key] = value
            
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False
    
    def add_post_merge_script(self, project_name: str, script_path: str, repo_patterns: List[str] = None) -> bool:
        """Add a new post-merge script"""
        if not os.path.exists(script_path):
            logger.error(f"Script file not found: {script_path}")
            return False
        
        try:
            new_script = {
                "project_name": project_name,
                "script_path": script_path,
                "repo_patterns": repo_patterns or [],
                "enabled": True,
                "added_at": datetime.now().isoformat()
            }
            
            self.config["post_merge_scripts"]["scripts"].append(new_script)
            logger.info(f"Added post-merge script: {project_name}")
            return self.save_config()
        except Exception as e:
            logger.error(f"Error adding post-merge script: {e}")
            return False
    
    def remove_post_merge_script(self, project_name: str) -> bool:
        """Remove a post-merge script by project name"""
        try:
            initial_count = len(self.config["post_merge_scripts"]["scripts"])
            self.config["post_merge_scripts"]["scripts"] = [
                script for script in self.config["post_merge_scripts"]["scripts"]
                if script["project_name"] != project_name
            ]
            
            if len(self.config["post_merge_scripts"]["scripts"]) < initial_count:
                logger.info(f"Removed post-merge script: {project_name}")
                return self.save_config()
            else:
                logger.warning(f"Post-merge script not found: {project_name}")
                return False
        except Exception as e:
            logger.error(f"Error removing post-merge script: {e}")
            return False
    
    def get_post_merge_scripts(self) -> List[Dict[str, Any]]:
        """Get all configured post-merge scripts"""
        return self.config["post_merge_scripts"]["scripts"]
    
    def execute_post_merge_script(self, repo_name: str, branch_name: str, pr_number: int) -> Tuple[bool, str]:
        """Execute appropriate post-merge script for a merged PR"""
        if not self.config["post_merge_scripts"]["enabled"]:
            return False, "Post-merge scripts are disabled"
        
        for script in self.config["post_merge_scripts"]["scripts"]:
            if not script["enabled"]:
                continue
                
            # Check if this script applies to this repository
            if script["repo_patterns"]:
                matches = False
                for pattern in script["repo_patterns"]:
                    if pattern in repo_name:
                        matches = True
                        break
                if not matches:
                    continue
            
            # Execute the script with environment variables for context
            script_path = script["script_path"]
            project_name = script["project_name"]
            
            try:
                # Set up environment variables for the script
                env = os.environ.copy()
                env["GITHUB_REPOSITORY"] = repo_name
                env["GITHUB_BRANCH"] = branch_name
                env["GITHUB_PR_NUMBER"] = str(pr_number)
                env["GITHUB_PROJECT"] = project_name
                
                # Check script type and execute
                if script_path.endswith(".py"):
                    result = subprocess.run(
                        ["python", script_path],
                        env=env,
                        capture_output=True,
                        text=True
                    )
                elif script_path.endswith(".bat"):
                    result = subprocess.run(
                        [script_path],
                        env=env,
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                else:
                    logger.error(f"Unsupported script type: {script_path}")
                    continue
                
                if result.returncode == 0:
                    logger.info(f"Successfully executed post-merge script: {project_name}")
                    return True, f"Script executed successfully: {project_name}"
                else:
                    logger.error(f"Script execution failed: {result.stderr}")
                    return False, f"Script execution failed: {result.stderr}"
            except Exception as e:
                logger.error(f"Error executing post-merge script: {e}")
                return False, f"Error executing script: {str(e)}"
        
        return False, "No matching post-merge scripts found"
    
    def create_pull_request_for_branch(self, repo: Repository, branch_name: str) -> Optional[PullRequest]:
        """Create a pull request for a new branch"""
        if not self.config["auto_pr_enabled"]:
            logger.info("Auto PR creation is disabled")
            return None
        
        # Check if branch should be excluded
        excluded_branches = self.config["auto_pr_settings"]["excluded_branches"]
        for excluded in excluded_branches:
            if excluded in branch_name:
                logger.info(f"Branch {branch_name} matches exclusion pattern {excluded}, skipping PR creation")
                return None
        
        # Check if repo should be included
        included_repos = self.config["auto_pr_settings"]["included_repos"]
        if included_repos and repo.full_name not in included_repos:
            logger.info(f"Repository {repo.full_name} not in inclusion list, skipping PR creation")
            return None
        
        try:
            # Check if PR already exists for this branch
            existing_prs = repo.get_pulls(state='open', head=f"{repo.owner.login}:{branch_name}")
            if existing_prs.totalCount > 0:
                logger.info(f"PR already exists for branch {branch_name} in {repo.full_name}")
                return None
            
            # Get branch
            try:
                branch = repo.get_branch(branch_name)
            except Exception:
                logger.error(f"Branch {branch_name} not found in {repo.full_name}")
                return None
            
            # Generate PR title and body from templates
            title_template = self.config["auto_pr_settings"]["title_template"]
            body_template = self.config["auto_pr_settings"]["body_template"]
            base_branch = self.config["auto_pr_settings"]["base_branch"]
            
            title = title_template.format(branch_name=branch_name, repo_name=repo.name)
            body = body_template.format(branch_name=branch_name, repo_name=repo.name)
            
            # Create the PR
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base_branch
            )
            
            logger.info(f"Created PR #{pr.number} for branch {branch_name} in {repo.full_name}")
            return pr
        except Exception as e:
            logger.error(f"Error creating PR for branch {branch_name}: {e}")
            return None
    
    def start_branch_monitor(self) -> bool:
        """Start background thread to monitor for new branches"""
        if self.running:
            logger.warning("Branch monitor already running")
            return False
        
        self.running = True
        self.branch_monitor_thread = threading.Thread(target=self._branch_monitor_loop)
        self.branch_monitor_thread.daemon = True
        self.branch_monitor_thread.start()
        logger.info("Branch monitor started")
        return True
    
    def stop_branch_monitor(self) -> bool:
        """Stop the branch monitor thread"""
        if not self.running:
            logger.warning("Branch monitor not running")
            return False
        
        self.running = False
        if self.branch_monitor_thread:
            self.branch_monitor_thread.join(timeout=3)
        logger.info("Branch monitor stopped")
        return True
    
    def _branch_monitor_loop(self) -> None:
        """Background loop to monitor for new branches"""
        if not self.github_client:
            logger.error("GitHub client not initialized")
            self.running = False
            return
        
        known_branches = {}  # {repo_name: set(branch_names)}
        
        while self.running:
            try:
                # Get repositories to monitor
                included_repos = self.config["auto_pr_settings"]["included_repos"]
                repos_to_check = []
                
                if included_repos:
                    # Only check specified repositories
                    for repo_name in included_repos:
                        try:
                            repo = self.github_client.get_repo(repo_name)
                            repos_to_check.append(repo)
                        except Exception as e:
                            logger.error(f"Error accessing repository {repo_name}: {e}")
                else:
                    # Check all accessible repositories
                    repos = self.github_client.get_user().get_repos()
                    repos_to_check = list(repos)
                
                # Process each repository
                for repo in repos_to_check:
                    repo_name = repo.full_name
                    
                    # Get current branches
                    try:
                        current_branches = set(branch.name for branch in repo.get_branches())
                    except Exception as e:
                        logger.error(f"Error getting branches for {repo_name}: {e}")
                        continue
                    
                    # Initialize if first time seeing this repo
                    if repo_name not in known_branches:
                        known_branches[repo_name] = current_branches
                        continue
                    
                    # Find new branches
                    old_branches = known_branches[repo_name]
                    new_branches = current_branches - old_branches
                    
                    # Create PRs for new branches
                    for branch_name in new_branches:
                        logger.info(f"New branch detected: {branch_name} in {repo_name}")
                        if self.config["auto_pr_enabled"]:
                            self.create_pull_request_for_branch(repo, branch_name)
                    
                    # Update known branches
                    known_branches[repo_name] = current_branches
                
                # Sleep before next check
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in branch monitor loop: {e}")
                time.sleep(120)  # Longer sleep on error
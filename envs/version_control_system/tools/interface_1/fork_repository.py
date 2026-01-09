import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class ForkRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        access_token: str,
        repository_id: str,
        owner_id: str,
        owner_type: str,
        repository_name: Optional[str] = None
    ) -> str:
        """
        Fork a repository to a new owner, including all branches, commits, files, and content.
        """
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "1"
            return str(max(int(k) for k in table.keys()) + 1)
        
        def get_user_from_token(token: str, tokens_data: Dict[str, Any]) -> Optional[str]:
            """Encode token and find associated user_id"""
            try:
                encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
                for token_info in tokens_data.values():
                    if token_info.get("token_encoded") == encoded_token:
                        return token_info.get("user_id")
                return None
            except:
                return None
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        repositories = data.get("repositories", {})
        users = data.get("users", {})
        organizations = data.get("organizations", {})
        access_tokens = data.get("access_tokens", {})
        branches = data.get("branches", {})
        commits = data.get("commits", {})
        directories = data.get("directories", {})
        files = data.get("files", {})
        file_contents = data.get("file_contents", {})
        
        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
        
        # Check if source repository exists
        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' not found"
            })
        
        source_repo = repositories[repository_id]
        
        # Validate owner exists
        if owner_type == "user":
            if owner_id not in users:
                return json.dumps({
                    "success": False,
                    "error": f"User with ID '{owner_id}' not found"
                })
        elif owner_type == "organization":
            if owner_id not in organizations:
                return json.dumps({
                    "success": False,
                    "error": f"Organization with ID '{owner_id}' not found"
                })
        else:
            return json.dumps({
                "success": False,
                "error": f"Invalid owner_type '{owner_type}'. Must be 'user' or 'organization'"
            })
        
        # Use original repository name if not provided
        fork_name = repository_name if repository_name else source_repo.get("repository_name")
        
        # Check for duplicate repository name for new owner
        for repo in repositories.values():
            if (repo.get("repository_name") == fork_name and
                repo.get("owner_id") == owner_id and
                repo.get("owner_type") == owner_type):
                return json.dumps({
                    "success": False,
                    "error": f"Repository '{fork_name}' already exists for this owner"
                })
        
        timestamp = "2026-01-01T23:59:00"
        new_repo_id = generate_id(repositories)
        
        # Create forked repository
        forked_repo = {
            "repository_id": new_repo_id,
            "repository_name": fork_name,
            "owner_type": owner_type,
            "owner_id": owner_id,
            "description": source_repo.get("description"),
            "visibility": source_repo.get("visibility"),
            "default_branch": source_repo.get("default_branch"),
            "is_fork": True,
            "parent_repository_id": repository_id,
            "is_archived": False,
            "is_template": False,
            "stars_count": 0,
            "forks_count": 0,
            "license_type": source_repo.get("license_type"),
            "created_at": timestamp,
            "updated_at": timestamp,
            "pushed_at": None
        }
        
        repositories[new_repo_id] = forked_repo
        
        # Mapping from old IDs to new IDs
        branch_id_map = {}
        commit_id_map = {}
        directory_id_map = {}
        file_id_map = {}
        
        # Collect all commits to copy (don't modify during iteration)
        commits_to_copy = []
        for commit in list(commits.values()):
            if commit.get("repository_id") == repository_id:
                commits_to_copy.append(commit)
        
        # Copy all commits from source repository
        for commit in commits_to_copy:
            old_commit_id = commit.get("commit_id")
            new_commit_id = generate_id(commits)
            commit_id_map[old_commit_id] = new_commit_id
            
            new_commit = {
                "commit_id": new_commit_id,
                "repository_id": new_repo_id,
                "commit_sha": commit.get("commit_sha"),
                "author_id": commit.get("author_id"),
                "committer_id": commit.get("committer_id"),
                "message": commit.get("message"),
                "parent_commit_id": None,
                "committed_at": commit.get("committed_at"),
                "created_at": timestamp
            }
            commits[new_commit_id] = new_commit
        
        # Update parent_commit_id references
        for commit in commits_to_copy:
            old_commit_id = commit.get("commit_id")
            new_commit_id = commit_id_map[old_commit_id]
            
            if commit.get("parent_commit_id"):
                old_parent_id = commit.get("parent_commit_id")
                if old_parent_id in commit_id_map:
                    commits[new_commit_id]["parent_commit_id"] = commit_id_map[old_parent_id]
        
        # Collect all branches to copy
        branches_to_copy = []
        for branch in list(branches.values()):
            if branch.get("repository_id") == repository_id:
                branches_to_copy.append(branch)
        
        # Copy all branches from source repository
        for branch in branches_to_copy:
            old_branch_id = branch.get("branch_id")
            new_branch_id = generate_id(branches)
            branch_id_map[old_branch_id] = new_branch_id
            
            new_branch = {
                "branch_id": new_branch_id,
                "repository_id": new_repo_id,
                "branch_name": branch.get("branch_name"),
                "commit_sha": branch.get("commit_sha"),
                "source_branch": None,
                "is_default": branch.get("is_default"),
                "created_at": timestamp,
                "updated_at": timestamp
            }
            branches[new_branch_id] = new_branch
        
        # Update source_branch references
        for branch in branches_to_copy:
            old_branch_id = branch.get("branch_id")
            new_branch_id = branch_id_map[old_branch_id]
            
            if branch.get("source_branch"):
                old_source_id = branch.get("source_branch")
                if old_source_id in branch_id_map:
                    branches[new_branch_id]["source_branch"] = branch_id_map[old_source_id]
        
        # Collect all directories to copy
        directories_to_copy = []
        for directory in list(directories.values()):
            if directory.get("repository_id") == repository_id:
                directories_to_copy.append(directory)
        
        # Copy all directories from source repository
        for directory in directories_to_copy:
            old_dir_id = directory.get("directory_id")
            new_dir_id = generate_id(directories)
            directory_id_map[old_dir_id] = new_dir_id
            
            old_branch_id = directory.get("branch_id")
            new_branch_id = branch_id_map.get(old_branch_id)
            
            new_directory = {
                "directory_id": new_dir_id,
                "repository_id": new_repo_id,
                "branch_id": new_branch_id,
                "directory_path": directory.get("directory_path"),
                "parent_directory_id": None,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            directories[new_dir_id] = new_directory
        
        # Update parent_directory_id references
        for directory in directories_to_copy:
            old_dir_id = directory.get("directory_id")
            new_dir_id = directory_id_map[old_dir_id]
            
            if directory.get("parent_directory_id"):
                old_parent_id = directory.get("parent_directory_id")
                if old_parent_id in directory_id_map:
                    directories[new_dir_id]["parent_directory_id"] = directory_id_map[old_parent_id]
        
        # Collect all files to copy
        files_to_copy = []
        for file in list(files.values()):
            if file.get("repository_id") == repository_id:
                files_to_copy.append(file)
        
        # Copy all files from source repository
        for file in files_to_copy:
            old_file_id = file.get("file_id")
            new_file_id = generate_id(files)
            file_id_map[old_file_id] = new_file_id
            
            old_branch_id = file.get("branch_id")
            new_branch_id = branch_id_map.get(old_branch_id)
            
            old_dir_id = file.get("directory_id")
            new_dir_id = directory_id_map.get(old_dir_id) if old_dir_id else None
            
            old_commit_id = file.get("last_commit_id")
            new_commit_id = commit_id_map.get(old_commit_id) if old_commit_id else None
            
            new_file = {
                "file_id": new_file_id,
                "repository_id": new_repo_id,
                "branch_id": new_branch_id,
                "directory_id": new_dir_id,
                "file_path": file.get("file_path"),
                "file_name": file.get("file_name"),
                "language": file.get("language"),
                "is_binary": file.get("is_binary"),
                "last_modified_at": file.get("last_modified_at"),
                "last_commit_id": new_commit_id,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            files[new_file_id] = new_file
        
        # Collect all file contents to copy
        contents_to_copy = []
        for content in list(file_contents.values()):
            old_file_id = content.get("file_id")
            if old_file_id in file_id_map:
                contents_to_copy.append(content)
        
        # Copy all file contents
        for content in contents_to_copy:
            new_content_id = generate_id(file_contents)
            old_file_id = content.get("file_id")
            new_file_id = file_id_map[old_file_id]
            
            old_commit_id = content.get("commit_id")
            new_commit_id = commit_id_map.get(old_commit_id)
            
            new_content = {
                "content_id": new_content_id,
                "file_id": new_file_id,
                "commit_id": new_commit_id,
                "content": content.get("content"),
                "encoding": content.get("encoding"),
                "created_at": timestamp
            }
            file_contents[new_content_id] = new_content
        
        # Increment forks_count on source repository
        source_repo["forks_count"] = source_repo.get("forks_count", 0) + 1
        
        return json.dumps({
            "success": True,
            "repository_id": new_repo_id,
            "parent_repository_id": repository_id,
            "repository_data": forked_repo,
            "copied_items": {
                "branches": len(branch_id_map),
                "commits": len(commit_id_map),
                "directories": len(directory_id_map),
                "files": len(file_id_map),
                "file_contents": len(contents_to_copy)
            }
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "fork_repository",
                "description": "Fork a repository to a new owner (user or organization). Creates a complete copy of the repository including all branches, commits, directories, files, and file contents. Sets is_fork to True and increments the forks_count on the source repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID to fork (required)"
                        },
                        "owner_id": {
                            "type": "string",
                            "description": "ID of the new owner (user_id or organization_id) (required)"
                        },
                        "owner_type": {
                            "type": "string",
                            "description": "Type of new owner. Allowed values: 'user', 'organization' (required)"
                        },
                        "repository_name": {
                            "type": "string",
                            "description": "Name for the forked repository (optional, defaults to source repository name)"
                        }
                    },
                    "required": ["access_token", "repository_id", "owner_id", "owner_type"]
                }
            }
        }

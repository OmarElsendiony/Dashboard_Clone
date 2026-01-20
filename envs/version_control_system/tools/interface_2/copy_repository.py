import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CopyRepository(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        repository_id: str,
        target_project_id: str,
        target_repository_name: str,
        user_id: str,
    ) -> str:
        
        timestamp = "2026-01-01T23:59:00"

        def generate_id(table: Dict[str, Any]) -> str:
            
            return "1" if not table else str(max(int(k) for k in table.keys()) + 1)

        def validate_data_structure(data: Dict[str, Any]):
            
            if not isinstance(data, dict):
                return False, "Invalid data format: 'data' must be a dict"
            return True, None

        is_valid, error_msg = validate_data_structure(data)
        if not is_valid:
            return json.dumps({"success": False, "error": error_msg})

        repositories_dict = data.get("repositories", {})
        projects_dict = data.get("projects", {})
        workspaces_dict = data.get("workspaces", {})
        branches_dict = data.get("branches", {})
        commits_dict = data.get("commits", {})
        directories_dict = data.get("directories", {})
        files_dict = data.get("files", {})
        file_contents_dict = data.get("file_contents", {})
        repository_collaborators_dict = data.get("repository_collaborators", {})
        users_dict = data.get("users", {})

        repository_id_str = str(repository_id).strip()
        target_project_id_str = str(target_project_id).strip()
        target_repository_name_str = str(target_repository_name).strip()
        user_id_str = str(user_id).strip()

        if repository_id_str not in repositories_dict:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id_str}' not found",
            })

        source_repository = repositories_dict[repository_id_str]

        if target_project_id_str not in projects_dict:
            return json.dumps({
                "success": False,
                "error": f"Target project with ID '{target_project_id_str}' not found",
            })

        target_project = projects_dict[target_project_id_str]

        target_workspace_id = str(target_project.get("workspace_id"))
        
        if target_workspace_id not in workspaces_dict:
            return json.dumps({
                "success": False,
                "error": f"Workspace with ID '{target_workspace_id}' not found",
            })

        target_workspace = workspaces_dict[target_workspace_id]
        
        target_owner_id = str(target_workspace.get("owner_id"))
        target_owner_type = users_dict.get(target_owner_id, {}).get("account_type", "personal")

        for rid, repository in repositories_dict.items():
            if not isinstance(repository, dict):
                continue
            
            if str(repository.get("project_id")) == target_project_id_str and str(repository.get("repository_name", "")).strip() == target_repository_name_str:
                return json.dumps({
                    "success": False,
                    "error": f"Repository with name '{target_repository_name_str}' already exists in project '{target_project_id_str}' (repository_id: {rid})",
                })

        new_repo_id = generate_id(repositories_dict)
        new_repository = {
            "repository_id": new_repo_id,
            "owner_type": target_owner_type,
            "owner_id": target_owner_id,
            "project_id": target_project_id_str,
            "repository_name": target_repository_name_str,
            "description": source_repository.get("description"),
            "visibility": source_repository.get("visibility"),
            "default_branch": source_repository.get("default_branch"),
            "is_fork": True,
            "parent_repository_id": repository_id_str,
            "is_archived": False,
            "is_template": False,
            "stars_count": 0,
            "forks_count": 0,
            "license_type": source_repository.get("license_type"),
            "created_at": timestamp,
            "updated_at": timestamp,
            "pushed_at": timestamp,
        }
        repositories_dict[new_repo_id] = new_repository

        # Map old IDs to new IDs
        branch_id_map = {}
        commit_id_map = {}
        directory_id_map = {}
        file_id_map = {}

        # Copy commits
        commits_copied = []
        for cid, commit in list(commits_dict.items()):
            if not isinstance(commit, dict):
                continue
            
            if str(commit.get("repository_id")) == repository_id_str:
                new_commit_id = generate_id(commits_dict)
                commit_id_map[str(cid)] = new_commit_id
                
                # Map parent_commit_id if it exists in the map
                parent_commit_id = commit.get("parent_commit_id")
                new_parent_commit_id = commit_id_map.get(str(parent_commit_id)) if parent_commit_id else None
                
                new_commit = {
                    "commit_id": new_commit_id,
                    "repository_id": new_repo_id,
                    "commit_sha": commit.get("commit_sha"),
                    "author_id": commit.get("author_id"),
                    "committer_id": commit.get("committer_id"),
                    "message": commit.get("message"),
                    "parent_commit_id": new_parent_commit_id,
                    "committed_at": commit.get("committed_at"),
                    "created_at": timestamp,
                }
                commits_dict[new_commit_id] = new_commit
                commits_copied.append(new_commit)

        # Copy branches
        branches_copied = []
        for bid, branch in list(branches_dict.items()):
            if not isinstance(branch, dict):
                continue
            
            if str(branch.get("repository_id")) == repository_id_str:
                new_branch_id = generate_id(branches_dict)
                branch_id_map[str(bid)] = new_branch_id
                
                # Map source_branch if it exists in the map
                source_branch = branch.get("source_branch")
                new_source_branch = branch_id_map.get(str(source_branch)) if source_branch else None
                
                new_branch = {
                    "branch_id": new_branch_id,
                    "repository_id": new_repo_id,
                    "branch_name": branch.get("branch_name"),
                    "commit_sha": branch.get("commit_sha"),
                    "source_branch": new_source_branch,
                    "is_default": branch.get("is_default"),
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                branches_dict[new_branch_id] = new_branch
                branches_copied.append(new_branch)

        # Copy directories
        directories_copied = []
        for did, directory in list(directories_dict.items()):
            if not isinstance(directory, dict):
                continue
            
            if str(directory.get("repository_id")) == repository_id_str:
                new_directory_id = generate_id(directories_dict)
                directory_id_map[str(did)] = new_directory_id
                
                # Map branch_id
                old_branch_id = str(directory.get("branch_id"))
                new_branch_id = branch_id_map.get(old_branch_id)
                
                # Map parent_directory_id if it exists in the map
                parent_directory_id = directory.get("parent_directory_id")
                new_parent_directory_id = directory_id_map.get(str(parent_directory_id)) if parent_directory_id else None
                
                new_directory = {
                    "directory_id": new_directory_id,
                    "repository_id": new_repo_id,
                    "branch_id": new_branch_id,
                    "directory_path": directory.get("directory_path"),
                    "parent_directory_id": new_parent_directory_id,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                directories_dict[new_directory_id] = new_directory
                directories_copied.append(new_directory)

        # Copy files
        files_copied = []
        for fid, file in list(files_dict.items()):
            if not isinstance(file, dict):
                continue
            
            if str(file.get("repository_id")) == repository_id_str:
                new_file_id = generate_id(files_dict)
                file_id_map[str(fid)] = new_file_id
                
                # Map branch_id, directory_id, and last_commit_id
                old_branch_id = str(file.get("branch_id"))
                new_branch_id = branch_id_map.get(old_branch_id)
                
                old_directory_id = file.get("directory_id")
                new_directory_id = directory_id_map.get(str(old_directory_id)) if old_directory_id else None
                
                old_last_commit_id = file.get("last_commit_id")
                new_last_commit_id = commit_id_map.get(str(old_last_commit_id)) if old_last_commit_id else None
                
                new_file = {
                    "file_id": new_file_id,
                    "repository_id": new_repo_id,
                    "branch_id": new_branch_id,
                    "directory_id": new_directory_id,
                    "file_path": file.get("file_path"),
                    "file_name": file.get("file_name"),
                    "language": file.get("language"),
                    "is_binary": file.get("is_binary"),
                    "last_modified_at": file.get("last_modified_at"),
                    "last_commit_id": new_last_commit_id,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
                files_dict[new_file_id] = new_file
                files_copied.append(new_file)

        # Copy file_contents
        file_contents_copied = []
        for cid, content in list(file_contents_dict.items()):
            if not isinstance(content, dict):
                continue
            
            old_file_id = str(content.get("file_id"))
            if old_file_id in file_id_map:
                new_content_id = generate_id(file_contents_dict)
                new_file_id = file_id_map[old_file_id]
                
                # Map commit_id
                old_commit_id = content.get("commit_id")
                new_commit_id = commit_id_map.get(str(old_commit_id)) if old_commit_id else None
                
                new_content = {
                    "content_id": new_content_id,
                    "file_id": new_file_id,
                    "commit_id": new_commit_id,
                    "content": content.get("content"),
                    "encoding": content.get("encoding"),
                    "created_at": timestamp,
                }
                file_contents_dict[new_content_id] = new_content
                file_contents_copied.append(new_content)

        collaborators_created = []

        user_collab_id = generate_id(repository_collaborators_dict)
        user_collaborator = {
            "collaborator_id": user_collab_id,
            "repository_id": new_repo_id,
            "user_id": user_id_str,
            "permission_level": "admin",
            "status": "active",
            "added_at": timestamp,
        }
        repository_collaborators_dict[user_collab_id] = user_collaborator
        collaborators_created.append(user_collaborator)

        if user_id_str != target_owner_id:
            owner_collab_id = generate_id(repository_collaborators_dict)
            owner_collaborator = {
                "collaborator_id": owner_collab_id,
                "repository_id": new_repo_id,
                "user_id": target_owner_id,
                "permission_level": "admin",
                "status": "active",
                "added_at": timestamp,
            }
            repository_collaborators_dict[owner_collab_id] = owner_collaborator
            collaborators_created.append(owner_collaborator)

        return json.dumps({
            "success": True,
            "repository": new_repository,
            "commits_copied": len(commits_copied),
            "branches_copied": len(branches_copied),
            "directories_copied": len(directories_copied),
            "files_copied": len(files_copied),
            "file_contents_copied": len(file_contents_copied),
            "collaborators_created": collaborators_created,
            "message": f"Repository '{target_repository_name_str}' copied successfully to project '{target_project_id_str}'",
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        
        return {
            "type": "function",
            "function": {
                "name": "copy_repository",
                "description": (
                    "Copies a repository into a target project with its full history and structure. Creates new entities with preserved relationships, marks the result as a fork of the source, does not copy existing collaborators, and creates new admin access for the requesting user and the target workspace owner when different. Validates inputs, enforces name uniqueness, and returns the new repository details with counts of copied items."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "The ID of the source repository to copy.",
                        },
                        "target_project_id": {
                            "type": "string",
                            "description": "The ID of the target project where the copied repository will be created.",
                        },
                        "target_repository_name": {
                            "type": "string",
                            "description": "The name for the copied repository. Must be unique within the target project.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the copy.",
                        },
                    },
                    "required": ["repository_id", "target_project_id", "target_repository_name", "user_id"],
                },
            },
        }
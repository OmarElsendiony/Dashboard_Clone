import json
import base64
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class UpsertFileDirectory(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        action: str,
        access_token: str,
        repository_id: str,
        branch_id: str,
        item_type: str,
        file_name: Optional[str] = None,
        directory_path: Optional[str] = None,
        parent_directory_id: Optional[str] = None,
        content: Optional[str] = None,
        encoding: Optional[str] = None,
        commit_message: Optional[str] = None,
        author_id: Optional[str] = None,
        language: Optional[str] = None,
        is_binary: Optional[bool] = None,
        file_id: Optional[str] = None,
        directory_id: Optional[str] = None
    ) -> str:
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
        
        def get_latest_content_entry(f_id: str, f_contents: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            """Finds the most recent content entry for a file to support carry-over."""
            entries = [v for v in f_contents.values() if v.get("file_id") == f_id]
            if not entries:
                return None
            # Assuming higher content_id means newer
            return max(entries, key=lambda x: int(x.get("content_id", 0)))
        
        # Validate action
        if action not in ["create", "update"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid action '{action}'. Must be 'create' or 'update'"
            })
        
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        # Validate item_type
        if item_type not in ["file", "directory"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid item_type '{item_type}'. Must be 'file' or 'directory'"
            })
        
        repositories = data.get("repositories", {})
        branches = data.get("branches", {})
        files = data.get("files", {})
        directories = data.get("directories", {})
        commits = data.get("commits", {})
        file_contents = data.get("file_contents", {})
        access_tokens = data.get("access_tokens", {})
        repository_collaborators = data.get("repository_collaborators", {})
        organization_members = data.get("organization_members", {})
        users = data.get("users", {})
        
        # Validate access token
        requesting_user_id = get_user_from_token(access_token, access_tokens)
        if not requesting_user_id:
            return json.dumps({
                "success": False,
                "error": "Invalid or expired access token"
            })
        
        # Check if repository exists
        if repository_id not in repositories:
            return json.dumps({
                "success": False,
                "error": f"Repository with ID '{repository_id}' not found"
            })
        
        # Check if branch exists
        if branch_id not in branches:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' not found"
            })
        
        # Validate branch belongs to repository
        branch = branches[branch_id]
        if branch.get("repository_id") != repository_id:
            return json.dumps({
                "success": False,
                "error": f"Branch with ID '{branch_id}' does not belong to repository '{repository_id}'"
            })
        
        # Validate author_id if provided
        if author_id and author_id not in users:
            return json.dumps({
                "success": False,
                "error": f"Author with ID '{author_id}' not found"
            })
        
        repository = repositories[repository_id]
        owner_id = repository.get("owner_id")
        owner_type = repository.get("owner_type")
        
        # Check if user has permission to modify files/directories
        has_permission = False
        
        # Check if user is the owner
        if owner_type == "user" and owner_id == requesting_user_id:
            has_permission = True
        
        # Check if user is a collaborator with write or admin access
        if not has_permission:
            for collab in repository_collaborators.values():
                if (collab.get("repository_id") == repository_id and
                    collab.get("user_id") == requesting_user_id and
                    collab.get("permission_level") in ["write", "admin"] and
                    collab.get("status") == "active"):
                    has_permission = True
                    break
        
        # Check if repository is owned by an organization and user is a member
        if not has_permission and owner_type == "organization":
            for membership in organization_members.values():
                if (membership.get("organization_id") == owner_id and
                    membership.get("user_id") == requesting_user_id and
                    membership.get("status") == "active"):
                    has_permission = True
                    break
        
        if not has_permission:
            return json.dumps({
                "success": False,
                "error": "Insufficient permissions. You must have write access to this repository"
            })
        
        timestamp = "2026-01-01T23:59:00"
        
        # Handle file operations
        if item_type == "file":
            # Validate file_name is provided for create
            if action == "create" and not file_name:
                return json.dumps({
                    "success": False,
                    "error": "file_name is required for file creation"
                })
            
            # Validate encoding if provided
            if encoding and encoding not in ["utf-8", "base64", "binary"]:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid encoding '{encoding}'. Must be 'utf-8', 'base64', or 'binary'"
                })
            
            if action == "update":
                # file_id is required for update
                if not file_id:
                    return json.dumps({
                        "success": False,
                        "error": "file_id is required for update action"
                    })
                
                if file_id not in files:
                    return json.dumps({
                        "success": False,
                        "error": f"File with ID '{file_id}' not found"
                    })
                
                file_obj = files[file_id]
                
                # Validate file belongs to the repository and branch
                if file_obj.get("repository_id") != repository_id:
                    return json.dumps({
                        "success": False,
                        "error": f"File does not belong to repository '{repository_id}'"
                    })
                if file_obj.get("branch_id") != branch_id:
                    return json.dumps({
                        "success": False,
                        "error": f"File does not belong to branch '{branch_id}'"
                    })
                
                # Check if this is a delete operation (no parameters except file_id)
                is_delete = (content is None and file_name is None and parent_directory_id is None and 
                             language is None and is_binary is None)
                
                if is_delete:
                    # DELETE operation
                    # Get the branch's current commit as parent
                    parent_commit_sha = branch.get("commit_sha")
                    parent_commit_id = None
                    
                    if parent_commit_sha:
                        for cid, commit in commits.items():
                            if commit.get("commit_sha") == parent_commit_sha:
                                parent_commit_id = cid
                                break
                    
                    # Create commit for the deletion
                    commit_author = author_id if author_id else requesting_user_id
                    new_commit_id = generate_id(commits)
                    new_commit_sha = f"commit_{new_commit_id}"
                    
                    new_commit = {
                        "commit_id": new_commit_id,
                        "repository_id": repository_id,
                        "commit_sha": new_commit_sha,
                        "author_id": commit_author,
                        "committer_id": commit_author,
                        "message": commit_message if commit_message else f"Delete {file_obj.get('file_name')}",
                        "parent_commit_id": parent_commit_id,
                        "committed_at": timestamp,
                        "created_at": timestamp
                    }
                    commits[new_commit_id] = new_commit
                    
                    # Update branch to point to new commit
                    branch["commit_sha"] = new_commit_sha
                    branch["updated_at"] = timestamp
                    
                    # Delete the file
                    deleted_file = files.pop(file_id)
                    
                    return json.dumps({
                        "success": True,
                        "action": "delete",
                        "item_type": "file",
                        "file_id": file_id,
                        "commit_id": new_commit_id,
                        "deleted_file": deleted_file
                    })
                
                # Check if this is a move operation (file_name or parent_directory_id changed)
                current_file_name = file_obj.get("file_name")
                current_parent_id = file_obj.get("directory_id")
                
                new_file_name = file_name if file_name is not None else current_file_name
                new_parent_id = parent_directory_id if parent_directory_id is not None else current_parent_id
                
                is_move = (new_file_name != current_file_name or new_parent_id != current_parent_id)
                
                if is_move:
                    # MOVE operation (could also include content update)
                    # Validate new parent_directory_id if provided
                    if new_parent_id:
                        if new_parent_id not in directories:
                            return json.dumps({
                                "success": False,
                                "error": f"Parent directory with ID '{new_parent_id}' not found"
                            })
                        
                        parent_dir = directories[new_parent_id]
                        if parent_dir.get("repository_id") != repository_id:
                            return json.dumps({
                                "success": False,
                                "error": f"Parent directory does not belong to repository '{repository_id}'"
                            })
                        if parent_dir.get("branch_id") != branch_id:
                            return json.dumps({
                                "success": False,
                                "error": f"Parent directory does not belong to branch '{branch_id}'"
                            })
                    
                    # Construct new file_path
                    if new_parent_id:
                        parent_dir = directories[new_parent_id]
                        dir_path = parent_dir.get("directory_path")
                        new_file_path = f"{dir_path}/{new_file_name}"
                    else:
                        # Root level file
                        new_file_path = new_file_name
                    
                    # Check if file already exists at new location
                    for existing_file_id, existing_file in files.items():
                        if (existing_file_id != file_id and
                            existing_file.get("repository_id") == repository_id and
                            existing_file.get("branch_id") == branch_id and
                            existing_file.get("file_path") == new_file_path):
                            return json.dumps({
                                "success": False,
                                "error": f"File already exists at path '{new_file_path}'"
                            })
                    
                    # Get the branch's current commit as parent
                    parent_commit_sha = branch.get("commit_sha")
                    parent_commit_id = None
                    
                    if parent_commit_sha:
                        for cid, commit in commits.items():
                            if commit.get("commit_sha") == parent_commit_sha:
                                parent_commit_id = cid
                                break
                    
                    # Create commit for the move
                    commit_author = author_id if author_id else requesting_user_id
                    new_commit_id = generate_id(commits)
                    new_commit_sha = f"commit_{new_commit_id}"
                    
                    old_path = file_obj.get("file_path")
                    new_commit = {
                        "commit_id": new_commit_id,
                        "repository_id": repository_id,
                        "commit_sha": new_commit_sha,
                        "author_id": commit_author,
                        "committer_id": commit_author,
                        "message": commit_message if commit_message else f"Move {new_file_name} from {old_path} to {new_file_path}",
                        "parent_commit_id": parent_commit_id,
                        "committed_at": timestamp,
                        "created_at": timestamp
                    }
                    commits[new_commit_id] = new_commit
                    
                    # Update branch to point to new commit
                    branch["commit_sha"] = new_commit_sha
                    branch["updated_at"] = timestamp
                    
                    # Update file location
                    file_obj["file_path"] = new_file_path
                    file_obj["file_name"] = new_file_name
                    file_obj["directory_id"] = new_parent_id
                    if language is not None:
                        file_obj["language"] = language
                    if is_binary is not None:
                        file_obj["is_binary"] = is_binary
                    file_obj["last_modified_at"] = timestamp
                    file_obj["last_commit_id"] = new_commit_id
                    file_obj["updated_at"] = timestamp
                    
                    # --- UPDATED: Ensure content entry exists for move ---
                    final_content = content
                    final_encoding = encoding if encoding else "utf-8"
                    
                    # If no new content provided, try to carry over previous content
                    if final_content is None:
                        latest_entry = get_latest_content_entry(file_id, file_contents)
                        if latest_entry:
                            final_content = latest_entry["content"]
                            final_encoding = latest_entry["encoding"]
                        else:
                            final_content = "" # Fallback for empty files
                    
                    new_content_id = generate_id(file_contents)
                    new_content = {
                        "content_id": new_content_id,
                        "file_id": file_id,
                        "commit_id": new_commit_id,
                        "content": final_content,
                        "encoding": final_encoding,
                        "created_at": timestamp
                    }
                    file_contents[new_content_id] = new_content
                    # ---------------------------------------------------
                    
                    return json.dumps({
                        "success": True,
                        "action": "move",
                        "item_type": "file",
                        "file_id": file_id,
                        "commit_id": new_commit_id,
                        "old_path": old_path,
                        "new_path": new_file_path,
                        "file_data": file_obj
                    })
                
                # Regular UPDATE operation (content/metadata only, no move)
                # Get the branch's current commit as parent
                parent_commit_sha = branch.get("commit_sha")
                parent_commit_id = None
                
                if parent_commit_sha:
                    for cid, commit in commits.items():
                        if commit.get("commit_sha") == parent_commit_sha:
                            parent_commit_id = cid
                            break
                
                # Create commit for the update
                commit_author = author_id if author_id else requesting_user_id
                new_commit_id = generate_id(commits)
                new_commit_sha = f"commit_{new_commit_id}"
                
                new_commit = {
                    "commit_id": new_commit_id,
                    "repository_id": repository_id,
                    "commit_sha": new_commit_sha,
                    "author_id": commit_author,
                    "committer_id": commit_author,
                    "message": commit_message if commit_message else f"Update {current_file_name}",
                    "parent_commit_id": parent_commit_id,
                    "committed_at": timestamp,
                    "created_at": timestamp
                }
                commits[new_commit_id] = new_commit
                
                # Update branch to point to new commit
                branch["commit_sha"] = new_commit_sha
                branch["updated_at"] = timestamp
                
                # Update file metadata (not location)
                if language is not None:
                    file_obj["language"] = language
                if is_binary is not None:
                    file_obj["is_binary"] = is_binary
                file_obj["last_modified_at"] = timestamp
                file_obj["last_commit_id"] = new_commit_id
                file_obj["updated_at"] = timestamp
                
                # --- UPDATED: Ensure content entry exists for update ---
                final_content = content
                final_encoding = encoding if encoding else "utf-8"
                
                if final_content is None:
                    latest_entry = get_latest_content_entry(file_id, file_contents)
                    if latest_entry:
                        final_content = latest_entry["content"]
                        final_encoding = latest_entry["encoding"]
                    else:
                        final_content = ""
                
                new_content_id = generate_id(file_contents)
                new_content = {
                    "content_id": new_content_id,
                    "file_id": file_id,
                    "commit_id": new_commit_id,
                    "content": final_content,
                    "encoding": final_encoding,
                    "created_at": timestamp
                }
                file_contents[new_content_id] = new_content
                # -----------------------------------------------------
                
                return json.dumps({
                    "success": True,
                    "action": "update",
                    "item_type": "file",
                    "file_id": file_id,
                    "commit_id": new_commit_id,
                    "file_data": file_obj
                })
            
            elif action == "create":
                # Validate parent_directory_id if provided (not null)
                if parent_directory_id:
                    if parent_directory_id not in directories:
                        return json.dumps({
                            "success": False,
                            "error": f"Parent directory with ID '{parent_directory_id}' not found"
                        })
                    
                    parent_dir = directories[parent_directory_id]
                    if parent_dir.get("repository_id") != repository_id:
                        return json.dumps({
                            "success": False,
                            "error": f"Parent directory does not belong to repository '{repository_id}'"
                        })
                    if parent_dir.get("branch_id") != branch_id:
                        return json.dumps({
                            "success": False,
                            "error": f"Parent directory does not belong to branch '{branch_id}'"
                        })
                
                # Construct file_path from parent_directory_id
                if parent_directory_id:
                    parent_dir = directories[parent_directory_id]
                    dir_path = parent_dir.get("directory_path")
                    file_path = f"{dir_path}/{file_name}"
                else:
                    # Root level file (parent_directory_id is None or not provided)
                    file_path = file_name
                
                # Check for duplicate file in same location
                for existing_file in files.values():
                    if (existing_file.get("repository_id") == repository_id and
                        existing_file.get("branch_id") == branch_id and
                        existing_file.get("file_path") == file_path):
                        return json.dumps({
                            "success": False,
                            "error": f"File already exists at path '{file_path}'"
                        })
                
                # Get the branch's current commit as parent
                parent_commit_sha = branch.get("commit_sha")
                parent_commit_id = None
                
                if parent_commit_sha:
                    for cid, commit in commits.items():
                        if commit.get("commit_sha") == parent_commit_sha:
                            parent_commit_id = cid
                            break
                
                # Create commit for the new file
                commit_author = author_id if author_id else requesting_user_id
                new_commit_id = generate_id(commits)
                new_commit_sha = f"commit_{new_commit_id}"
                
                new_commit = {
                    "commit_id": new_commit_id,
                    "repository_id": repository_id,
                    "commit_sha": new_commit_sha,
                    "author_id": commit_author,
                    "committer_id": commit_author,
                    "message": commit_message if commit_message else f"Create {file_name}",
                    "parent_commit_id": parent_commit_id,
                    "committed_at": timestamp,
                    "created_at": timestamp
                }
                commits[new_commit_id] = new_commit
                
                # Update branch to point to new commit
                branch["commit_sha"] = new_commit_sha
                branch["updated_at"] = timestamp
                
                # Create new file
                new_file_id = generate_id(files)
                new_file = {
                    "file_id": new_file_id,
                    "repository_id": repository_id,
                    "branch_id": branch_id,
                    "directory_id": parent_directory_id,
                    "file_path": file_path,
                    "file_name": file_name,
                    "language": language if language else "Unknown",
                    "is_binary": bool(is_binary) if is_binary is not None else False,
                    "last_modified_at": timestamp,
                    "last_commit_id": new_commit_id,
                    "created_at": timestamp,
                    "updated_at": timestamp
                }
                files[new_file_id] = new_file
                
                # Create file content entry
                new_content_id = generate_id(file_contents)
                new_content = {
                    "content_id": new_content_id,
                    "file_id": new_file_id,
                    "commit_id": new_commit_id,
                    "content": content if content is not None else "",
                    "encoding": encoding if encoding else "utf-8",
                    "created_at": timestamp
                }
                file_contents[new_content_id] = new_content
                
                return json.dumps({
                    "success": True,
                    "action": "create",
                    "item_type": "file",
                    "file_id": new_file_id,
                    "commit_id": new_commit_id,
                    "file_data": new_file
                })
        
        # Handle directory operations
        elif item_type == "directory":
            # Validate directory_path is provided for create and update
            if action == "create" and not directory_path:
                return json.dumps({
                    "success": False,
                    "error": "directory_path is required for directory creation"
                })
            
            if action == "update":
                # directory_id is required for update
                if not directory_id:
                    return json.dumps({
                        "success": False,
                        "error": "directory_id is required for update action"
                    })
                
                if directory_id not in directories:
                    return json.dumps({
                        "success": False,
                        "error": f"Directory with ID '{directory_id}' not found"
                    })
                
                dir_obj = directories[directory_id]
                
                # Validate directory belongs to the repository and branch
                if dir_obj.get("repository_id") != repository_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Directory does not belong to repository '{repository_id}'"
                    })
                if dir_obj.get("branch_id") != branch_id:
                    return json.dumps({
                        "success": False,
                        "error": f"Directory does not belong to branch '{branch_id}'"
                    })
                
                # Check if this is a delete operation (directory_path is empty string)
                if directory_path == "":
                    # DELETE operation
                    # Check if directory has any children directories
                    for child_dir in directories.values():
                        if child_dir.get("parent_directory_id") == directory_id:
                            return json.dumps({
                                "success": False,
                                "error": f"Cannot delete directory: it contains subdirectories. Delete child directories first."
                            })
                    
                    # Check if directory has any files
                    for file_obj in files.values():
                        if file_obj.get("directory_id") == directory_id:
                            return json.dumps({
                                "success": False,
                                "error": f"Cannot delete directory: it contains files. Delete or move files first."
                            })
                    
                    # Delete the directory
                    deleted_dir = directories.pop(directory_id)
                    
                    return json.dumps({
                        "success": True,
                        "action": "delete",
                        "item_type": "directory",
                        "directory_id": directory_id,
                        "deleted_directory": deleted_dir
                    })
                
                # MOVE operation (directory_path is provided and not empty)
                if not directory_path:
                    return json.dumps({
                        "success": False,
                        "error": "directory_path is required for directory move operation"
                    })
                
                old_path = dir_obj.get("directory_path")
                
                # Infer parent_directory_id from new directory_path
                inferred_parent_id = None
                if '/' in directory_path:
                    parent_path = '/'.join(directory_path.split('/')[:-1])
                    
                    # Search for parent directory - MUST exist
                    for dir_id, dir_data in directories.items():
                        if (dir_data.get("repository_id") == repository_id and
                            dir_data.get("branch_id") == branch_id and
                            dir_data.get("directory_path") == parent_path):
                            inferred_parent_id = dir_id
                            break
                    
                    # Parent MUST exist
                    if not inferred_parent_id:
                        return json.dumps({
                            "success": False,
                            "error": f"Parent directory path '{parent_path}' does not exist"
                        })
                    
                    # Check if trying to move into itself or its own subdirectory
                    current_check_id = inferred_parent_id
                    while current_check_id:
                        if current_check_id == directory_id:
                            return json.dumps({
                                "success": False,
                                "error": "Cannot move directory into itself or its own subdirectory"
                            })
                        current_check_id = directories.get(current_check_id, {}).get("parent_directory_id")
                
                # Check if directory already exists at new location
                for existing_dir_id, existing_dir in directories.items():
                    if (existing_dir_id != directory_id and
                        existing_dir.get("repository_id") == repository_id and
                        existing_dir.get("branch_id") == branch_id and
                        existing_dir.get("directory_path") == directory_path):
                        return json.dumps({
                            "success": False,
                            "error": f"Directory already exists at path '{directory_path}'"
                        })
                
                # Determine if this is a rename or move
                old_parent_id = dir_obj.get("parent_directory_id")
                if inferred_parent_id == old_parent_id:
                    operation_type = "rename"
                else:
                    operation_type = "move"
                
                # Update directory path and parent
                dir_obj["directory_path"] = directory_path
                dir_obj["parent_directory_id"] = inferred_parent_id
                dir_obj["updated_at"] = timestamp
                
                # Update all child directories and files paths recursively
                def update_child_paths(old_parent_path: str, new_parent_path: str):
                    # Update child directories
                    for child_dir_id, child_dir in directories.items():
                        child_path = child_dir.get("directory_path", "")
                        if child_path.startswith(old_parent_path + "/"):
                            # Replace the old parent path with new parent path
                            new_child_path = child_path.replace(old_parent_path, new_parent_path, 1)
                            child_dir["directory_path"] = new_child_path
                            child_dir["updated_at"] = timestamp
                    
                    # Update files in moved directory and its subdirectories
                    for file_obj in files.values():
                        file_path = file_obj.get("file_path", "")
                        if file_path.startswith(old_parent_path + "/"):
                            new_file_path = file_path.replace(old_parent_path, new_parent_path, 1)
                            file_obj["file_path"] = new_file_path
                            file_obj["updated_at"] = timestamp
                
                update_child_paths(old_path, directory_path)
                
                return json.dumps({
                    "success": True,
                    "action": operation_type,
                    "item_type": "directory",
                    "directory_id": directory_id,
                    "old_path": old_path,
                    "new_path": directory_path,
                    "directory_data": dir_obj
                })
            
            elif action == "create":
                # Infer parent_directory_id from directory_path
                inferred_parent_id = None
                if '/' in directory_path:
                    parent_path = '/'.join(directory_path.split('/')[:-1])
                    
                    # Search for parent directory - MUST exist for non-root directories
                    for dir_id, dir_data in directories.items():
                        if (dir_data.get("repository_id") == repository_id and
                            dir_data.get("branch_id") == branch_id and
                            dir_data.get("directory_path") == parent_path):
                            inferred_parent_id = dir_id
                            break
                    
                    # Parent MUST exist for nested directories
                    if not inferred_parent_id:
                        return json.dumps({
                            "success": False,
                            "error": f"Parent directory path '{parent_path}' does not exist. Create parent directories first."
                        })
                
                # Check for duplicate directory in same location
                for existing_dir in directories.values():
                    if (existing_dir.get("repository_id") == repository_id and
                        existing_dir.get("branch_id") == branch_id and
                        existing_dir.get("directory_path") == directory_path):
                        return json.dumps({
                            "success": False,
                            "error": f"Directory already exists at path '{directory_path}'"
                        })
                
                # Create new directory
                new_dir_id = generate_id(directories)
                new_dir = {
                    "directory_id": new_dir_id,
                    "repository_id": repository_id,
                    "branch_id": branch_id,
                    "directory_path": directory_path,
                    "parent_directory_id": inferred_parent_id,
                    "created_at": timestamp,
                    "updated_at": timestamp
                }
                directories[new_dir_id] = new_dir
                
                return json.dumps({
                    "success": True,
                    "action": "create",
                    "item_type": "directory",
                    "directory_id": new_dir_id,
                    "directory_data": new_dir
                })
        
        return json.dumps({
            "success": False,
            "error": "Unknown error"
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "upsert_file_directory",
                "description": "Creates or updates a file or directory in a repository branch.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform. Allowed values: 'create', 'update' (required)",
                            "enum": ["create", "update"]
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Access token for authentication (will be encoded to base64 UTF-8 and compared with token_encoded) (required)"
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID (required)"
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Branch ID (required)"
                        },
                        "item_type": {
                            "type": "string",
                            "description": "Type of item. Allowed values: 'file', 'directory' (required)",
                            "enum": ["file", "directory"]
                        },
                        "file_name": {
                            "type": "string",
                            "description": "File name only (e.g., 'index.js'). Required for file creation. For move operation, provide new file name. File path will be constructed from parent_directory_id."
                        },
                        "directory_path": {
                            "type": "string",
                            "description": "Full directory path (e.g., 'src/components'). Required for directory creation. For move operation, provide new directory path. For delete operation, provide empty string. Parent directory ID is inferred from this path."
                        },
                        "parent_directory_id": {
                            "type": "string",
                            "description": "Parent directory ID for file operations. Optional - if not provided, file is created at root level. For move operation, provide new parent directory ID."
                        },
                        "content": {
                            "type": "string",
                            "description": "File content (optional, for files only)"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "Content encoding. Allowed values: 'utf-8', 'base64', 'binary' (optional, defaults to 'utf-8')",
                            "enum": ["utf-8", "base64", "binary"]
                        },
                        "commit_message": {
                            "type": "string",
                            "description": "Commit message (optional, for files only). Defaults to 'Update <file_name>' for updates and 'Create <file_name>' for creates in case not provided."
                        },
                        "author_id": {
                            "type": "string",
                            "description": "Author user ID (optional, defaults to authenticated user)"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (optional, for files only)",
                            "enum": [
                                'C', 'C++', 'C#', 'Go', 'Rust', 'Java', 'Kotlin', 'Scala', 'Python', 'Ruby', 'PHP',
                                'JavaScript', 'TypeScript', 'Shell', 'PowerShell', 'Swift', 'Objective-C', 'Dart',
                                'R', 'MATLAB', 'Groovy', 'Perl', 'Lua', 'Haskell', 'Elixir', 'Erlang', 'Julia',
                                'Assembly', 'Fortran', 'COBOL', 'HTML', 'CSS',  'SCSS', 'Less', 'Markdown', 'AsciiDoc',
                                'JSON', 'YAML', 'XML', 'TOML', 'INI', 'CSV', 'Dockerfile', 'Makefile', 'Bash',
                                'Terraform', 'Ansible', 'SQL', 'PLpgSQL', 'Text', 'Binary', 'Unknown'
                            ]
                        },
                        "is_binary": {
                            "type": "boolean",
                            "description": "Whether file is binary. Allowed values: True, False (optional, for files only, defaults to False)"
                        },
                        "file_id": {
                            "type": "string",
                            "description": "File ID (required for update action when item_type='file')"
                        },
                        "directory_id": {
                            "type": "string",
                            "description": "Directory ID (required for update action when item_type='directory')"
                        }
                    },
                    "required": ["action", "access_token", "repository_id", "branch_id", "item_type"]
                }
            }
        }
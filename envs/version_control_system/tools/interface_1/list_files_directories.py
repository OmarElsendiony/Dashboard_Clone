import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListFilesDirectories(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        search_type: str,
        repository_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        parent_directory_id: Optional[str] = None,
        directory_path: Optional[str] = None,
        file_name: Optional[str] = None,
        language: Optional[str] = None,
        file_id: Optional[str] = None,
        directory_id: Optional[str] = None
    ) -> str:
        if not isinstance(data, dict):
            return json.dumps({
                "success": False,
                "error": "Invalid data format"
            })
        
        # Validate search_type
        if search_type not in ["file", "directory"]:
            return json.dumps({
                "success": False,
                "error": f"Invalid search_type '{search_type}'. Must be 'file' or 'directory'"
            })
        
        # Validate language if provided 
        valid_languages = [
            'C', 'C++', 'C#', 'Go', 'Rust', 'Java', 'Kotlin', 'Scala', 'Python', 'Ruby', 'PHP',
            'JavaScript', 'TypeScript', 'Shell', 'PowerShell', 'Swift', 'Objective-C', 'Dart',
            'R', 'MATLAB', 'Groovy', 'Perl', 'Lua', 'Haskell', 'Elixir', 'Erlang', 'Julia',
            'Assembly', 'Fortran', 'COBOL', 'HTML', 'CSS', 'SCSS', 'Less', 'Markdown', 'AsciiDoc',
            'JSON', 'YAML', 'XML', 'TOML', 'INI', 'CSV', 'Dockerfile', 'Makefile', 'Bash',
            'Terraform', 'Ansible', 'SQL', 'PLpgSQL', 'Text', 'Binary', 'Unknown'
        ]
        
        if language and language not in valid_languages:
            return json.dumps({
                "success": False,
                "error": f"Invalid language '{language}'. Must be one of the supported languages"
            })

        def get_results_for_branch(target_branch_id: Optional[str]):
            results = []
            if search_type == "file":
                files = data.get("files", {})
                for f_id, file_data in files.items():
                    if repository_id and file_data.get("repository_id") != repository_id: continue
                    if target_branch_id and file_data.get("branch_id") != target_branch_id: continue
                    if parent_directory_id and file_data.get("directory_id") != parent_directory_id: continue
                    if file_name and file_data.get("file_name") != file_name: continue
                    if language and file_data.get("language") != language: continue
                    if file_id and f_id != file_id: continue
                    results.append({**file_data, "file_id": f_id, "item_type": "file"})
            
            elif search_type == "directory":
                directories = data.get("directories", {})
                for d_id, dir_data in directories.items():
                    if repository_id and dir_data.get("repository_id") != repository_id: continue
                    if target_branch_id and dir_data.get("branch_id") != target_branch_id: continue
                    if parent_directory_id and dir_data.get("parent_directory_id") != parent_directory_id: continue
                    if directory_path and dir_data.get("directory_path") != directory_path: continue
                    if directory_id and d_id != directory_id: continue
                    results.append({**dir_data, "directory_id": d_id, "item_type": "directory"})
            return results

        
        current_branch_search = branch_id
        final_results = []
        
        max_depth = 10 
        attempts = 0

        while attempts < max_depth:
            final_results = get_results_for_branch(current_branch_search)            
            if final_results or not current_branch_search:
                break
            
            branches = data.get("branches", {})
            branch_obj = None
            
            if current_branch_search in branches:
                branch_obj = branches[current_branch_search]
            else:
                for b in branches.values():
                    if b.get("branch_id") == current_branch_search:
                        branch_obj = b
                        break
            
            if branch_obj and branch_obj.get("source_branch"):
                current_branch_search = branch_obj.get("source_branch")
                attempts += 1
            else:
                break

        return json.dumps({
            "success": True,
            "count": len(final_results),
            "search_type": search_type,
            "results": final_results,
            "resolved_branch_id": current_branch_search 
        })
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_files_directories",
                "description": "Lists either files or directories from repositories based on the search_type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_type": {
                            "type": "string",
                            "description": "Type of items to search for. Allowed values: 'file', 'directory' (required)",
                            "enum": ["file", "directory"]
                        },
                        "repository_id": {
                            "type": "string",
                            "description": "Filter by repository_id (exact match) (optional)"
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Filter by branch_id (exact match) (optional)"
                        },
                        "parent_directory_id": {
                            "type": "string",
                            "description": "Filter by parent directory ID (exact match) - for files, this filters by directory_id; for directories, this filters by parent_directory_id (optional)"
                        },
                        "directory_path": {
                            "type": "string",
                            "description": "Filter by directory path (exact match) - only applies when search_type='directory' (optional)"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "Filter by file name (exact match) - only applies when search_type='file' (optional)"
                        },
                        "language": {
                            "type": "string",
                            "description": "Filter by programming language (exact match) - only applies when search_type='file'. Allowed values: 'C', 'C++', 'C#', 'Go', 'Rust', 'Java', 'Kotlin', 'Scala', 'Python', 'Ruby', 'PHP', 'JavaScript', 'TypeScript', 'Shell', 'PowerShell', 'Swift', 'Objective-C', 'Dart', 'R', 'MATLAB', 'Groovy', 'Perl', 'Lua', 'Haskell', 'Elixir', 'Erlang', 'Julia', 'Assembly', 'Fortran', 'COBOL', 'HTML', 'CSS', 'SCSS', 'Less', 'Markdown', 'AsciiDoc', 'JSON', 'YAML', 'XML', 'TOML', 'INI', 'CSV', 'Dockerfile', 'Makefile', 'Bash', 'Terraform', 'Ansible', 'SQL', 'PLpgSQL', 'Text', 'Binary', 'Unknown' (optional)",
                            "enum": [
                                'C', 'C++', 'C#', 'Go', 'Rust', 'Java', 'Kotlin', 'Scala', 'Python', 'Ruby', 'PHP',
                                'JavaScript', 'TypeScript', 'Shell', 'PowerShell', 'Swift', 'Objective-C', 'Dart',
                                'R', 'MATLAB', 'Groovy', 'Perl', 'Lua', 'Haskell', 'Elixir', 'Erlang', 'Julia',
                                'Assembly', 'Fortran', 'COBOL', 'HTML', 'CSS',  'SCSS', 'Less', 'Markdown', 'AsciiDoc',
                                'JSON', 'YAML', 'XML', 'TOML', 'INI', 'CSV', 'Dockerfile', 'Makefile', 'Bash',
                                'Terraform', 'Ansible', 'SQL', 'PLpgSQL', 'Text', 'Binary', 'Unknown'
                            ]
                        },
                        "file_id": {
                            "type": "string",
                            "description": "Filter by file_id (exact match) - only applies when search_type='file' (optional)"
                        },
                        "directory_id": {
                            "type": "string",
                            "description": "Filter by directory_id (exact match) - only applies when search_type='directory' (optional)"
                        }
                    },
                    "required": ["search_type"]
                }
            }
        }
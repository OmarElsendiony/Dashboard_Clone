import json
import math
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool

class ListServices(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        page: Optional[int] = 1,
        limit: Optional[int] = 50,
    ) -> str:

        if not isinstance(data, dict):
            return json.dumps({"success": False, "error": "Invalid data format"})

        repositories = data.get("repositories", {})

        page_num = page if isinstance(page, int) and page > 0 else 1
        limit_num = limit if isinstance(limit, int) and limit > 0 else 50

        all_services = []
        for repo_id, repo in repositories.items():
            r_name = repo.get("repository_name") or repo.get("name") or "Unnamed Service"

            all_services.append({
                "repository_id": repo_id,
                "service_name": r_name,
                "description": repo.get("description", "No description provided"),
                "default_branch": repo.get("default_branch", "main")
            })

        all_services.sort(key=lambda x: (x["service_name"].lower(), x["repository_id"]))

        total_count = len(all_services)
        total_pages = math.ceil(total_count / limit_num) if limit_num > 0 else 0

        start_idx = (page_num - 1) * limit_num
        end_idx = start_idx + limit_num

        paginated_services = all_services[start_idx:end_idx]

        return json.dumps({
            "success": True,
            "page": int(page_num),
            "limit": int(limit_num),
            "total_count": int(total_count),
            "total_pages": int(total_pages),
            "services": paginated_services
        })

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_services",
                "description": (
                    "Lists all engineering services (repositories) in the organization. "
                    "PURPOSE: The primary Service Discovery tool. Maps functional names (e.g. 'Checkout') to technical Repository IDs. "
                    "RETURNS: A paginated catalog of services including their 'repository_id', which is required for tools like 'create_issue' or 'create_branch'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "OPTIONAL. The page number for pagination. Defaults to 1."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "OPTIONAL. The number of results per page. Defaults to 50."
                        }
                    },
                    "required": []
                }
            }
        }

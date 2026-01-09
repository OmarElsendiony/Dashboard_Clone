from .add_branch import AddBranch
from .add_pull_request import AddPullRequest
from .add_pull_request_comment import AddPullRequestComment
from .add_user_to_entity import AddUserToEntity
from .copy_repository import CopyRepository
from .create_file import CreateFile
from .create_project import CreateProject
from .create_repository import CreateRepository
from .create_workspace import CreateWorkspace
from .delete_project import DeleteProject
from .discard_repository import DiscardRepository
from .fetch_pull_request import FetchPullRequest
from .fetch_pull_request_reviews import FetchPullRequestReviews
from .get_branch import GetBranch
from .get_file import GetFile
from .get_project import GetProject
from .get_repository import GetRepository
from .get_user import GetUser
from .list_access_token import ListAccessToken
from .list_workspaces import ListWorkspaces
from .modify_pull_request import ModifyPullRequest
from .remove_branch import RemoveBranch
from .remove_file import RemoveFile
from .remove_user_from_entity import RemoveUserFromEntity
from .submit_pull_request_review import SubmitPullRequestReview
from .switch_to_human import SwitchToHuman
from .update_file import UpdateFile
from .update_project import UpdateProject
from .update_repository import UpdateRepository
from .update_workspace import UpdateWorkspace

ALL_TOOLS_INTERFACE_2 = [
    AddBranch,
    AddPullRequest,
    AddPullRequestComment,
    AddUserToEntity,
    CopyRepository,
    CreateFile,
    CreateProject,
    CreateRepository,
    CreateWorkspace,
    DeleteProject,
    DiscardRepository,
    FetchPullRequest,
    FetchPullRequestReviews,
    GetBranch,
    GetFile,
    GetProject,
    GetRepository,
    GetUser,
    ListAccessToken,
    ListWorkspaces,
    ModifyPullRequest,
    RemoveBranch,
    RemoveFile,
    RemoveUserFromEntity,
    SubmitPullRequestReview,
    SwitchToHuman,
    UpdateFile,
    UpdateProject,
    UpdateRepository,
    UpdateWorkspace
]

from .add_commit import AddCommit
from .add_new_repo import AddNewRepo
from .add_organization import AddOrganization
from .add_project import AddProject
from .add_team_member import AddTeamMember
from .approve_release import ApproveRelease
from .create_feature_branch import CreateFeatureBranch
from .create_new_branch import CreateNewBranch
from .create_pipeline import CreatePipeline
from .create_repo_release import CreateRepoRelease
from .create_work_item import CreateWorkItem
from .delegate_to_human import DelegateToHuman
from .delete_org_project import DeleteOrgProject
from .get_auth_credential import GetAuthCredential
from .get_run_pipeline import GetRunPipeline
from .initiate_pull_request import InitiatePullRequest
from .list_team_members import ListTeamMembers
from .merge_pull_request import MergePullRequest
from .modify_project import ModifyProject
from .modify_repository import ModifyRepository
from .remove_user import RemoveUser
from .resolve_branch import ResolveBranch
from .resolve_organization import ResolveOrganization
from .resolve_project import ResolveProject
from .resolve_pull_request import ResolvePullRequest
from .resolve_releases import ResolveReleases
from .resolve_repository import ResolveRepository
from .resolve_work_item import ResolveWorkItem
from .retrieve_user import RetrieveUser
from .set_permission import SetPermission
from .update_organization import UpdateOrganization
from .update_user_access import UpdateUserAccess
from .update_work_item import UpdateWorkItem

ALL_TOOLS_INTERFACE_4 = [
    AddCommit,
    AddNewRepo,
    AddOrganization,
    AddProject,
    AddTeamMember,
    ApproveRelease,
    CreateFeatureBranch,
    CreateNewBranch,
    CreatePipeline,
    CreateRepoRelease,
    CreateWorkItem,
    DelegateToHuman,
    DeleteOrgProject,
    GetAuthCredential,
    GetRunPipeline,
    InitiatePullRequest,
    ListTeamMembers,
    MergePullRequest,
    ModifyProject,
    ModifyRepository,
    RemoveUser,
    ResolveBranch,
    ResolveOrganization,
    ResolveProject,
    ResolvePullRequest,
    ResolveReleases,
    ResolveRepository,
    ResolveWorkItem,
    RetrieveUser,
    SetPermission,
    UpdateOrganization,
    UpdateUserAccess,
    UpdateWorkItem
]

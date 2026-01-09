from .create_branch import CreateBranch
from .create_organization import CreateOrganization
from .create_pull_request import CreatePullRequest
from .create_workflow import CreateWorkflow
from .delete_comment import DeleteComment
from .delete_file import DeleteFile
from .delete_issue import DeleteIssue
from .delete_release import DeleteRelease
from .delete_workflow import DeleteWorkflow
from .erase_branch import EraseBranch
from .fork_repository import ForkRepository
from .get_repository_permissions import GetRepositoryPermissions
from .invite_org_member import InviteOrgMember
from .list_access_tokens import ListAccessTokens
from .list_branches import ListBranches
from .list_comments import ListComments
from .list_files_directories import ListFilesDirectories
from .list_labels import ListLabels
from .list_org_members import ListOrgMembers
from .list_organizations import ListOrganizations
from .list_pull_requests import ListPullRequests
from .list_releases import ListReleases
from .list_repositories import ListRepositories
from .list_stars import ListStars
from .list_users import ListUsers
from .list_workflows import ListWorkflows
from .remove_org_member import RemoveOrgMember
from .search_issues import SearchIssues
from .star_unstar_repo import StarUnstarRepo
from .submit_pr_review import SubmitPrReview
from .transfer_to_human import TransferToHuman
from .update_issues import UpdateIssues
from .update_pull_request import UpdatePullRequest
from .update_repository_permissions import UpdateRepositoryPermissions
from .update_workflow import UpdateWorkflow
from .upsert_comment import UpsertComment
from .upsert_file_directory import UpsertFileDirectory
from .upsert_label import UpsertLabel
from .upsert_release import UpsertRelease
from .upsert_repository import UpsertRepository

ALL_TOOLS_INTERFACE_1 = [
    CreateBranch,
    CreateOrganization,
    CreatePullRequest,
    CreateWorkflow,
    DeleteComment,
    DeleteFile,
    DeleteIssue,
    DeleteRelease,
    DeleteWorkflow,
    EraseBranch,
    ForkRepository,
    GetRepositoryPermissions,
    InviteOrgMember,
    ListAccessTokens,
    ListBranches,
    ListComments,
    ListFilesDirectories,
    ListLabels,
    ListOrgMembers,
    ListOrganizations,
    ListPullRequests,
    ListReleases,
    ListRepositories,
    ListStars,
    ListUsers,
    ListWorkflows,
    RemoveOrgMember,
    SearchIssues,
    StarUnstarRepo,
    SubmitPrReview,
    TransferToHuman,
    UpdateIssues,
    UpdatePullRequest,
    UpdateRepositoryPermissions,
    UpdateWorkflow,
    UpsertComment,
    UpsertFileDirectory,
    UpsertLabel,
    UpsertRelease,
    UpsertRepository
]

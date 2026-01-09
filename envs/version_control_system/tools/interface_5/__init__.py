from .assign_issue import AssignIssue
from .attach_detach_issue_labels import AttachDetachIssueLabels
from .create_comment import CreateComment
from .create_commit import CreateCommit
from .create_file_content import CreateFileContent
from .create_iam_user import CreateIamUser
from .create_issue import CreateIssue
from .create_label import CreateLabel
from .create_notification import CreateNotification
from .create_or_update_file import CreateOrUpdateFile
from .create_release import CreateRelease
from .create_repo import CreateRepo
from .create_repo_branch import CreateRepoBranch
from .create_repo_pipeline import CreateRepoPipeline
from .create_repo_pull_request import CreateRepoPullRequest
from .delete_branch import DeleteBranch
from .fork_repo import ForkRepo
from .get_commit import GetCommit
from .get_iam_user import GetIamUser
from .get_issue import GetIssue
from .get_label import GetLabel
from .get_pipeline import GetPipeline
from .get_pull_request import GetPullRequest
from .get_release import GetRelease
from .get_repo import GetRepo
from .get_repo_branch import GetRepoBranch
from .get_repo_file import GetRepoFile
from .get_repo_permissions import GetRepoPermissions
from .handoff_to_human import HandoffToHuman
from .list_files_for_commit import ListFilesForCommit
from .merge_repo_pull_request import MergeRepoPullRequest
from .update_branch_head import UpdateBranchHead
from .update_iam_user import UpdateIamUser
from .update_issue import UpdateIssue
from .update_pipeline import UpdatePipeline
from .update_repo_archive_status import UpdateRepoArchiveStatus
from .update_repo_pull_request import UpdateRepoPullRequest
from .write_pull_request_review import WritePullRequestReview
from .write_repo_permissions import WriteRepoPermissions

ALL_TOOLS_INTERFACE_5 = [
    AssignIssue,
    AttachDetachIssueLabels,
    CreateComment,
    CreateCommit,
    CreateFileContent,
    CreateIamUser,
    CreateIssue,
    CreateLabel,
    CreateNotification,
    CreateOrUpdateFile,
    CreateRelease,
    CreateRepo,
    CreateRepoBranch,
    CreateRepoPipeline,
    CreateRepoPullRequest,
    DeleteBranch,
    ForkRepo,
    GetCommit,
    GetIamUser,
    GetIssue,
    GetLabel,
    GetPipeline,
    GetPullRequest,
    GetRelease,
    GetRepo,
    GetRepoBranch,
    GetRepoFile,
    GetRepoPermissions,
    HandoffToHuman,
    ListFilesForCommit,
    MergeRepoPullRequest,
    UpdateBranchHead,
    UpdateIamUser,
    UpdateIssue,
    UpdatePipeline,
    UpdateRepoArchiveStatus,
    UpdateRepoPullRequest,
    WritePullRequestReview,
    WriteRepoPermissions
]

from .add_code_review import AddCodeReview
from .add_new_file import AddNewFile
from .add_new_issue import AddNewIssue
from .add_repository_collaborator import AddRepositoryCollaborator
from .create_branch_in_repo import CreateBranchInRepo
from .create_label_in_repo import CreateLabelInRepo
from .dispatch_notification import DispatchNotification
from .dissolve_organization import DissolveOrganization
from .enroll_organization_member import EnrollOrganizationMember
from .escalate_to_human import EscalateToHuman
from .establish_organization import EstablishOrganization
from .fetch_entity_info import FetchEntityInfo
from .fetch_organization_membership import FetchOrganizationMembership
from .initialize_repository import InitializeRepository
from .list_code_reviews import ListCodeReviews
from .list_repository_collaborators import ListRepositoryCollaborators
from .modify_branch import ModifyBranch
from .modify_collaborator_access import ModifyCollaboratorAccess
from .modify_organization_membership import ModifyOrganizationMembership
from .modify_repository_settings import ModifyRepositorySettings
from .open_pull_request import OpenPullRequest
from .post_comment import PostComment
from .publish_release import PublishRelease
from .record_commit import RecordCommit
from .register_workflow import RegisterWorkflow
from .remove_repository import RemoveRepository
from .resolve_user_identity import ResolveUserIdentity
from .retrieve_organization_details import RetrieveOrganizationDetails
from .retrieve_repository_details import RetrieveRepositoryDetails
from .revise_issue import ReviseIssue
from .search_pull_requests import SearchPullRequests
from .search_releases import SearchReleases
from .submit_review_verdict import SubmitReviewVerdict
from .transition_pull_request import TransitionPullRequest
from .update_label import UpdateLabel
from .verify_user_authentication import VerifyUserAuthentication

ALL_TOOLS_INTERFACE_3 = [
    AddCodeReview,
    AddNewFile,
    AddNewIssue,
    AddRepositoryCollaborator,
    CreateBranchInRepo,
    CreateLabelInRepo,
    DispatchNotification,
    DissolveOrganization,
    EnrollOrganizationMember,
    EscalateToHuman,
    EstablishOrganization,
    FetchEntityInfo,
    FetchOrganizationMembership,
    InitializeRepository,
    ListCodeReviews,
    ListRepositoryCollaborators,
    ModifyBranch,
    ModifyCollaboratorAccess,
    ModifyOrganizationMembership,
    ModifyRepositorySettings,
    OpenPullRequest,
    PostComment,
    PublishRelease,
    RecordCommit,
    RegisterWorkflow,
    RemoveRepository,
    ResolveUserIdentity,
    RetrieveOrganizationDetails,
    RetrieveRepositoryDetails,
    ReviseIssue,
    SearchPullRequests,
    SearchReleases,
    SubmitReviewVerdict,
    TransitionPullRequest,
    UpdateLabel,
    VerifyUserAuthentication
]

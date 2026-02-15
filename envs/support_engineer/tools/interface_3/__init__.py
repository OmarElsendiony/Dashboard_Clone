from .add_tag_to_ticket import AddTagToTicket
from .create_commit import CreateCommit
from .create_documentation_record import CreateDocumentationRecord
from .create_new_branch import CreateNewBranch
from .escalate_to_human import EscalateToHuman
from .fetch_branch_details import FetchBranchDetails
from .fetch_channel_details import FetchChannelDetails
from .fetch_documentation_record import FetchDocumentationRecord
from .fetch_pull_request_details import FetchPullRequestDetails
from .fetch_ticket_details import FetchTicketDetails
from .fetch_ticket_replies import FetchTicketReplies
from .fetch_user_or_customer_details import FetchUserOrCustomerDetails
from .get_repository_details import GetRepositoryDetails
from .merge_pull_request_to_target import MergePullRequestToTarget
from .modify_branch_metadata import ModifyBranchMetadata
from .modify_documentation_record import ModifyDocumentationRecord
from .modify_pull_request import ModifyPullRequest
from .modify_ticket import ModifyTicket
from .open_pull_request import OpenPullRequest
from .post_channel_message import PostChannelMessage
from .send_customer_message import SendCustomerMessage
from .send_ticket_reply import SendTicketReply
from .submit_pull_request_review import SubmitPullRequestReview

ALL_TOOLS_INTERFACE_3 = [
    AddTagToTicket,
    CreateCommit,
    CreateDocumentationRecord,
    CreateNewBranch,
    EscalateToHuman,
    FetchBranchDetails,
    FetchChannelDetails,
    FetchDocumentationRecord,
    FetchPullRequestDetails,
    FetchTicketDetails,
    FetchTicketReplies,
    FetchUserOrCustomerDetails,
    GetRepositoryDetails,
    MergePullRequestToTarget,
    ModifyBranchMetadata,
    ModifyDocumentationRecord,
    ModifyPullRequest,
    ModifyTicket,
    OpenPullRequest,
    PostChannelMessage,
    SendCustomerMessage,
    SendTicketReply,
    SubmitPullRequestReview
]

from .add_bulk_tags import AddBulkTags
from .add_internal_ticket_note import AddInternalTicketNote
from .add_new_branch import AddNewBranch
from .add_new_commit import AddNewCommit
from .add_new_ticket import AddNewTicket
from .add_tag import AddTag
from .assign_ticket_to_member import AssignTicketToMember
from .close_ticket import CloseTicket
from .create_channel_post import CreateChannelPost
from .create_doc import CreateDoc
from .create_new_channel import CreateNewChannel
from .create_new_pull_request import CreateNewPullRequest
from .create_repository import CreateRepository
from .delegate_to_human import DelegateToHuman
from .delete_branch import DeleteBranch
from .fetch_branches import FetchBranches
from .fetch_channels import FetchChannels
from .fetch_repositories import FetchRepositories
from .get_branch_details import GetBranchDetails
from .get_customer_info import GetCustomerInfo
from .get_doc import GetDoc
from .get_groups import GetGroups
from .get_pull_requests import GetPullRequests
from .get_users import GetUsers
from .list_tickets import ListTickets
from .merge_pull_request import MergePullRequest
from .send_ticket_email_reply import SendTicketEmailReply
from .update_repository import UpdateRepository
from .update_ticket_info import UpdateTicketInfo

ALL_TOOLS_INTERFACE_4 = [
    AddBulkTags,
    AddInternalTicketNote,
    AddNewBranch,
    AddNewCommit,
    AddNewTicket,
    AddTag,
    AssignTicketToMember,
    CloseTicket,
    CreateChannelPost,
    CreateDoc,
    CreateNewChannel,
    CreateNewPullRequest,
    CreateRepository,
    DelegateToHuman,
    DeleteBranch,
    FetchBranches,
    FetchChannels,
    FetchRepositories,
    GetBranchDetails,
    GetCustomerInfo,
    GetDoc,
    GetGroups,
    GetPullRequests,
    GetUsers,
    ListTickets,
    MergePullRequest,
    SendTicketEmailReply,
    UpdateRepository,
    UpdateTicketInfo
]

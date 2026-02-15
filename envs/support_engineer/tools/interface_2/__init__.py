from .add_commit import AddCommit
from .add_ticket_comment import AddTicketComment
from .assign_severity_level import AssignSeverityLevel
from .create_branch import CreateBranch
from .create_pr import CreatePr
from .create_pr_comment import CreatePrComment
from .create_thread import CreateThread
from .create_wiki_page import CreateWikiPage
from .edit_ticket import EditTicket
from .escalate_to_expert import EscalateToExpert
from .get_channel import GetChannel
from .get_customer import GetCustomer
from .get_repository import GetRepository
from .get_subscription import GetSubscription
from .get_thread import GetThread
from .get_ticket import GetTicket
from .get_user import GetUser
from .merge_pr import MergePr
from .reopen_ticket import ReopenTicket
from .request_pr_review import RequestPrReview
from .search_branch import SearchBranch
from .search_code import SearchCode
from .send_email import SendEmail
from .send_message_in_channel import SendMessageInChannel
from .switch_to_human import SwitchToHuman

ALL_TOOLS_INTERFACE_2 = [
    AddCommit,
    AddTicketComment,
    AssignSeverityLevel,
    CreateBranch,
    CreatePr,
    CreatePrComment,
    CreateThread,
    CreateWikiPage,
    EditTicket,
    EscalateToExpert,
    GetChannel,
    GetCustomer,
    GetRepository,
    GetSubscription,
    GetThread,
    GetTicket,
    GetUser,
    MergePr,
    ReopenTicket,
    RequestPrReview,
    SearchBranch,
    SearchCode,
    SendEmail,
    SendMessageInChannel,
    SwitchToHuman
]

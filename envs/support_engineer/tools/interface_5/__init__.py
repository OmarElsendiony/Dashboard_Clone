from .add_mail_attachment import AddMailAttachment
from .add_space_member import AddSpaceMember
from .create_draft_mail import CreateDraftMail
from .create_new_issue import CreateNewIssue
from .create_pull_request import CreatePullRequest
from .create_space import CreateSpace
from .create_space_message import CreateSpaceMessage
from .delete_issue import DeleteIssue
from .get_ticket_conversations import GetTicketConversations
from .get_ticket_satisfaction import GetTicketSatisfaction
from .get_tickets_list import GetTicketsList
from .handoff_to_human import HandoffToHuman
from .initiate_branch import InitiateBranch
from .list_pull_requests import ListPullRequests
from .list_repositories import ListRepositories
from .list_space_message import ListSpaceMessage
from .list_users import ListUsers
from .retrieve_ticket import RetrieveTicket
from .search_issues import SearchIssues
from .send_draft_email import SendDraftEmail
from .set_ticket_note import SetTicketNote
from .set_ticket_reply import SetTicketReply
from .set_update_ticket import SetUpdateTicket
from .update_issues import UpdateIssues
from .update_pull_request import UpdatePullRequest

ALL_TOOLS_INTERFACE_5 = [
    AddMailAttachment,
    AddSpaceMember,
    CreateDraftMail,
    CreateNewIssue,
    CreatePullRequest,
    CreateSpace,
    CreateSpaceMessage,
    DeleteIssue,
    GetTicketConversations,
    GetTicketSatisfaction,
    GetTicketsList,
    HandoffToHuman,
    InitiateBranch,
    ListPullRequests,
    ListRepositories,
    ListSpaceMessage,
    ListUsers,
    RetrieveTicket,
    SearchIssues,
    SendDraftEmail,
    SetTicketNote,
    SetTicketReply,
    SetUpdateTicket,
    UpdateIssues,
    UpdatePullRequest
]

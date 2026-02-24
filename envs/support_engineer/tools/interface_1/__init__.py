from .add_channel_member import AddChannelMember
from .add_ticket_note import AddTicketNote
from .create_branches import CreateBranches
from .create_channel import CreateChannel
from .create_customer_message import CreateCustomerMessage
from .create_escalation_record import CreateEscalationRecord
from .create_issue import CreateIssue
from .create_knowledge_article import CreateKnowledgeArticle
from .create_ticket_comment import CreateTicketComment
from .get_branches import GetBranches
from .get_channels import GetChannels
from .get_comments import GetComments
from .get_entity import GetEntity
from .get_issues import GetIssues
from .get_message import GetMessage
from .get_pages import GetPages
from .get_repositories import GetRepositories
from .get_ticket_notes import GetTicketNotes
from .get_tickets import GetTickets
from .make_pull_requests import MakePullRequests
from .sanitize_attachment import SanitizeAttachment
from .send_channel_message import SendChannelMessage
from .transfer_to_human import TransferToHuman
from .update_customer_message import UpdateCustomerMessage
from .update_knowledge_article import UpdateKnowledgeArticle
from .update_pull_requests import UpdatePullRequests
from .update_ticket import UpdateTicket

ALL_TOOLS_INTERFACE_1 = [
    AddChannelMember,
    AddTicketNote,
    CreateBranches,
    CreateChannel,
    CreateCustomerMessage,
    CreateEscalationRecord,
    CreateIssue,
    CreateKnowledgeArticle,
    CreateTicketComment,
    GetBranches,
    GetChannels,
    GetComments,
    GetEntity,
    GetIssues,
    GetMessage,
    GetPages,
    GetRepositories,
    GetTicketNotes,
    GetTickets,
    MakePullRequests,
    SanitizeAttachment,
    SendChannelMessage,
    TransferToHuman,
    UpdateCustomerMessage,
    UpdateKnowledgeArticle,
    UpdatePullRequests,
    UpdateTicket
]

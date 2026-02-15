from .bulk_update_tickets import BulkUpdateTickets
from .create_escalation_record import CreateEscalationRecord
from .create_issue import CreateIssue
from .create_support_ticket import CreateSupportTicket
from .get_comments import GetComments
from .get_entity_status import GetEntityStatus
from .get_message import GetMessage
from .get_page import GetPage
from .inspect_pull_request import InspectPullRequest
from .list_branches import ListBranches
from .list_channels import ListChannels
from .list_groups import ListGroups
from .list_services import ListServices
from .manage_channel import ManageChannel
from .manage_channel_membership import ManageChannelMembership
from .manage_issue_assignees import ManageIssueAssignees
from .manage_kb_page import ManageKbPage
from .manage_message_pin import ManageMessagePin
from .manage_pull_requests import ManagePullRequests
from .manage_reaction import ManageReaction
from .manage_repository import ManageRepository
from .merge_tickets import MergeTickets
from .moderate_issue import ModerateIssue
from .publish_response import PublishResponse
from .read_channel_history import ReadChannelHistory
from .sanitize_attachment import SanitizeAttachment
from .search_object_entities import SearchObjectEntities
from .search_pages import SearchPages
from .search_tickets import SearchTickets
from .send_slack_message import SendSlackMessage
from .start_branch import StartBranch
from .transfer_to_human import TransferToHuman
from .update_issue import UpdateIssue

ALL_TOOLS_INTERFACE_1 = [
    BulkUpdateTickets,
    CreateEscalationRecord,
    CreateIssue,
    CreateSupportTicket,
    GetComments,
    GetEntityStatus,
    GetMessage,
    GetPage,
    InspectPullRequest,
    ListBranches,
    ListChannels,
    ListGroups,
    ListServices,
    ManageChannel,
    ManageChannelMembership,
    ManageIssueAssignees,
    ManageKbPage,
    ManageMessagePin,
    ManagePullRequests,
    ManageReaction,
    ManageRepository,
    MergeTickets,
    ModerateIssue,
    PublishResponse,
    ReadChannelHistory,
    SanitizeAttachment,
    SearchObjectEntities,
    SearchPages,
    SearchTickets,
    SendSlackMessage,
    StartBranch,
    TransferToHuman,
    UpdateIssue
]

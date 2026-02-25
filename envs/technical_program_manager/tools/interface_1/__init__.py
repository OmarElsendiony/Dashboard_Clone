from .get_repository import GetRepository
from .add_incident_note import AddIncidentNote
from .get_risk import GetRisk
from .add_task_comment import AddTaskComment
from .get_scope_change_request import GetScopeChangeRequest
from .create_channel import CreateChannel
from .get_user import GetUser
from .create_doc import CreateDoc
from .list_pull_requests import ListPullRequests
from .create_escalation import CreateEscalation
from .create_page import CreatePage
from .post_message import PostMessage
from .create_risk import CreateRisk
from .search_pages import SearchPages
from .create_scope_change_request import CreateScopeChangeRequest
from .transfer_to_human import TransferToHuman
from .create_subtask import CreateSubtask
from .update_page import UpdatePage
from .edit_incident import EditIncident
from .update_risk import UpdateRisk
from .fetch_incident import FetchIncident
from .update_scope_change_request import UpdateScopeChangeRequest
from .fetch_work_item import FetchWorkItem
from .update_subtask import UpdateSubtask
from .get_channel import GetChannel
from .upsert_program import UpsertProgram
from .get_doc import GetDoc
from .upsert_task import UpsertTask
from .get_program import GetProgram


ALL_TOOLS_INTERFACE_1 = [
    GetRepository,
    AddIncidentNote,
    GetRisk,
    AddTaskComment,
    GetScopeChangeRequest,
    CreateChannel,
    GetUser,
    CreateDoc,
    ListPullRequests,
    CreateEscalation,
    CreatePage,
    PostMessage,
    CreateRisk,
    SearchPages,
    CreateScopeChangeRequest,
    TransferToHuman,
    CreateSubtask,
    UpdatePage,
    EditIncident,
    UpdateRisk,
    FetchIncident,
    UpdateScopeChangeRequest,
    FetchWorkItem,
    UpdateSubtask,
    GetChannel,
    UpsertProgram,
    GetDoc,
    UpsertTask,
    GetProgram,
]
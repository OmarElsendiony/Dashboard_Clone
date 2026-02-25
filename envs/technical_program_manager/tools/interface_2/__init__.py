from .retrieve_user import RetrieveUser
from .send_message_in_channel import SendMessageInChannel
from .construct_channel import ConstructChannel
from .create_document import CreateDocument
from .assign_project_members import AssignProjectMembers
from .create_project import CreateProject
from .fetch_project import FetchProject
from .create_work_item import CreateWorkItem
from .retrieve_work_item import RetrieveWorkItem
from .update_work_item import UpdateWorkItem
from .fetch_channel import FetchChannel
from .fetch_document import FetchDocument
from .update_document import UpdateDocument
from .list_repositories import ListRepositories
from .fetch_pull_request import FetchPullRequest
from .construct_risk import ConstructRisk
from .fetch_risk import FetchRisk
from .modify_risk import ModifyRisk
from .get_incident import GetIncident
from .update_incident import UpdateIncident
from .create_incident_note import CreateIncidentNote
from .create_scope_change import CreateScopeChange
from .modify_project import ModifyProject
from .manage_page import ManagePage
from .switch_to_human import SwitchToHuman
from .create_incident_escalation import CreateIncidentEscalation


ALL_TOOLS_INTERFACE_2 = [
    RetrieveUser,
    SendMessageInChannel,
    ConstructChannel,
    CreateDocument,
    AssignProjectMembers,
    CreateProject,
    FetchProject,
    CreateWorkItem,
    RetrieveWorkItem,
    UpdateWorkItem,
    FetchChannel,
    FetchDocument,
    UpdateDocument,
    ListRepositories,
    FetchPullRequest,
    ConstructRisk,
    FetchRisk,
    ModifyRisk,
    GetIncident,
    UpdateIncident,
    CreateIncidentNote,
    CreateScopeChange,
    ModifyProject,
    ManagePage,
    SwitchToHuman,
    CreateIncidentEscalation,
]

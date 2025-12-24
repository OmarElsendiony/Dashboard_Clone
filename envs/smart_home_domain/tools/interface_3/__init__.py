from .activate_flow import ActivateFlow
from .add_scene_action import AddSceneAction
from .commission_device import CommissionDevice
from .construct_notification import ConstructNotification
from .create_flow_definition import CreateFlowDefinition
from .create_scene_definition import CreateSceneDefinition
from .create_zone import CreateZone
from .define_device_action_attributes_in_flow import DefineDeviceActionAttributesInFlow
from .define_device_action_in_flow import DefineDeviceActionInFlow
from .define_time_schedule import DefineTimeSchedule
from .define_trigger_condition import DefineTriggerCondition
from .discover_household_devices import DiscoverHouseholdDevices
from .enroll_household_member import EnrollHouseholdMember
from .escalate_to_human import EscalateToHuman
from .establish_household import EstablishHousehold
from .fetch_scene_details import FetchSceneDetails
from .generate_energy_insights import GenerateEnergyInsights
from .generate_trigger_for_flow import GenerateTriggerForFlow
from .get_user_home_info import GetUserHomeInfo
from .inspect_household import InspectHousehold
from .mark_as_favorite import MarkAsFavorite
from .modify_household_profile import ModifyHouseholdProfile
from .place_device_in_zone import PlaceDeviceInZone
from .rename_device_identity import RenameDeviceIdentity
from .rename_zone import RenameZone
from .resolve_user_identity import ResolveUserIdentity
from .retrieve_flow_information import RetrieveFlowInformation
from .retrieve_household_zones import RetrieveHouseholdZones
from .set_scene_device_state import SetSceneDeviceState

ALL_TOOLS_INTERFACE_3 = [
    ActivateFlow,
    AddSceneAction,
    CommissionDevice,
    ConstructNotification,
    CreateFlowDefinition,
    CreateSceneDefinition,
    CreateZone,
    DefineDeviceActionAttributesInFlow,
    DefineDeviceActionInFlow,
    DefineTimeSchedule,
    DefineTriggerCondition,
    DiscoverHouseholdDevices,
    EnrollHouseholdMember,
    EscalateToHuman,
    EstablishHousehold,
    FetchSceneDetails,
    GenerateEnergyInsights,
    GenerateTriggerForFlow,
    GetUserHomeInfo,
    InspectHousehold,
    MarkAsFavorite,
    ModifyHouseholdProfile,
    PlaceDeviceInZone,
    RenameDeviceIdentity,
    RenameZone,
    ResolveUserIdentity,
    RetrieveFlowInformation,
    RetrieveHouseholdZones,
    SetSceneDeviceState
]

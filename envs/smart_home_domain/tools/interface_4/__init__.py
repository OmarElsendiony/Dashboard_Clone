from .add_automation import AddAutomation
from .add_automation_action import AddAutomationAction
from .add_device import AddDevice
from .add_new_schedule import AddNewSchedule
from .create_area import CreateArea
from .create_scene import CreateScene
from .create_trigger import CreateTrigger
from .delegate_to_human import DelegateToHuman
from .draft_notification import DraftNotification
from .fetch_area import FetchArea
from .find_household_user import FindHouseholdUser
from .get_device import GetDevice
from .get_device_favorite_preferences import GetDeviceFavoritePreferences
from .get_energy_usage_summary import GetEnergyUsageSummary
from .get_scene_favorite_preferences import GetSceneFavoritePreferences
from .list_scene import ListScene
from .onboard_household_member import OnboardHouseholdMember
from .set_device_favorite_preferences import SetDeviceFavoritePreferences
from .set_scene_favorite_preferences import SetSceneFavoritePreferences
from .update_area import UpdateArea
from .update_automation import UpdateAutomation
from .update_device import UpdateDevice
from .update_device_favorite_preferences import UpdateDeviceFavoritePreferences
from .update_scene import UpdateScene
from .update_scene_favorite_preferences import UpdateSceneFavoritePreferences

ALL_TOOLS_INTERFACE_4 = [
    AddAutomation,
    AddAutomationAction,
    AddDevice,
    AddNewSchedule,
    CreateArea,
    CreateScene,
    CreateTrigger,
    DelegateToHuman,
    DraftNotification,
    FetchArea,
    FindHouseholdUser,
    GetDevice,
    GetDeviceFavoritePreferences,
    GetEnergyUsageSummary,
    GetSceneFavoritePreferences,
    ListScene,
    OnboardHouseholdMember,
    SetDeviceFavoritePreferences,
    SetSceneFavoritePreferences,
    UpdateArea,
    UpdateAutomation,
    UpdateDevice,
    UpdateDeviceFavoritePreferences,
    UpdateScene,
    UpdateSceneFavoritePreferences
]

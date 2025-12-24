from .add_accessory_to_home import AddAccessoryToHome
from .add_action_to_scene import AddActionToScene
from .add_new_home import AddNewHome
from .add_new_room import AddNewRoom
from .add_notification_to_scene import AddNotificationToScene
from .assign_accessory_to_room import AssignAccessoryToRoom
from .create_accessory_control_action import CreateAccessoryControlAction
from .create_automation import CreateAutomation
from .create_automation_trigger import CreateAutomationTrigger
from .create_home_scene import CreateHomeScene
from .create_notification import CreateNotification
from .create_notification_action import CreateNotificationAction
from .create_scene_activation_action import CreateSceneActivationAction
from .delete_home_information import DeleteHomeInformation
from .delete_home_scene import DeleteHomeScene
from .delete_room import DeleteRoom
from .duplicate_home_scene import DuplicateHomeScene
from .edit_room_information import EditRoomInformation
from .edit_scene import EditScene
from .get_accessory import GetAccessory
from .get_accessory_energy_usage import GetAccessoryEnergyUsage
from .get_accessory_reachability import GetAccessoryReachability
from .get_automation import GetAutomation
from .get_home_energy_summary import GetHomeEnergySummary
from .handoff_to_human import HandoffToHuman
from .invite_user import InviteUser
from .list_accessories import ListAccessories
from .list_automations import ListAutomations
from .list_home_scenes import ListHomeScenes
from .list_home_users import ListHomeUsers
from .list_notifications import ListNotifications
from .list_rooms import ListRooms
from .manage_automation import ManageAutomation
from .remove_accessory_from_room import RemoveAccessoryFromRoom
from .remove_user_from_home import RemoveUserFromHome
from .update_automation_trigger import UpdateAutomationTrigger
from .update_home_information import UpdateHomeInformation
from .update_notification import UpdateNotification

ALL_TOOLS_INTERFACE_5 = [
    AddAccessoryToHome,
    AddActionToScene,
    AddNewHome,
    AddNewRoom,
    AddNotificationToScene,
    AssignAccessoryToRoom,
    CreateAccessoryControlAction,
    CreateAutomation,
    CreateAutomationTrigger,
    CreateHomeScene,
    CreateNotification,
    CreateNotificationAction,
    CreateSceneActivationAction,
    DeleteHomeInformation,
    DeleteHomeScene,
    DeleteRoom,
    DuplicateHomeScene,
    EditRoomInformation,
    EditScene,
    GetAccessory,
    GetAccessoryEnergyUsage,
    GetAccessoryReachability,
    GetAutomation,
    GetHomeEnergySummary,
    HandoffToHuman,
    InviteUser,
    ListAccessories,
    ListAutomations,
    ListHomeScenes,
    ListHomeUsers,
    ListNotifications,
    ListRooms,
    ManageAutomation,
    RemoveAccessoryFromRoom,
    RemoveUserFromHome,
    UpdateAutomationTrigger,
    UpdateHomeInformation,
    UpdateNotification
]

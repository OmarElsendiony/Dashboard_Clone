from .add_routine_action import AddRoutineAction
from .add_routine_trigger import AddRoutineTrigger
from .assign_device_to_room import AssignDeviceToRoom
from .compose_notification import ComposeNotification
from .create_home import CreateHome
from .create_room import CreateRoom
from .create_routine import CreateRoutine
from .create_schedule import CreateSchedule
from .delete_home import DeleteHome
from .discover_devices import DiscoverDevices
from .enable_device import EnableDevice
from .enable_routine import EnableRoutine
from .get_device_state import GetDeviceState
from .get_devices import GetDevices
from .get_energy_usage import GetEnergyUsage
from .get_home_users import GetHomeUsers
from .get_user_preferences import GetUserPreferences
from .invite_user_to_home import InviteUserToHome
from .resolve_home import ResolveHome
from .routine_query import RoutineQuery
from .send_notification import SendNotification
from .set_notification_mute import SetNotificationMute
from .set_user_preferences import SetUserPreferences
from .transfer_to_human import TransferToHuman
from .update_device_location import UpdateDeviceLocation
from .update_device_name import UpdateDeviceName
from .update_home import UpdateHome
from .update_room import UpdateRoom
from .update_routine import UpdateRoutine
from .update_routine_action import UpdateRoutineAction
from .update_routine_trigger import UpdateRoutineTrigger
from .update_user_role import UpdateUserRole

ALL_TOOLS_INTERFACE_1 = [
    AddRoutineAction,
    AddRoutineTrigger,
    AssignDeviceToRoom,
    ComposeNotification,
    CreateHome,
    CreateRoom,
    CreateRoutine,
    CreateSchedule,
    DeleteHome,
    DiscoverDevices,
    EnableDevice,
    EnableRoutine,
    GetDeviceState,
    GetDevices,
    GetEnergyUsage,
    GetHomeUsers,
    GetUserPreferences,
    InviteUserToHome,
    ResolveHome,
    RoutineQuery,
    SendNotification,
    SetNotificationMute,
    SetUserPreferences,
    TransferToHuman,
    UpdateDeviceLocation,
    UpdateDeviceName,
    UpdateHome,
    UpdateRoom,
    UpdateRoutine,
    UpdateRoutineAction,
    UpdateRoutineTrigger,
    UpdateUserRole
]

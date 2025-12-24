from .add_new_device import AddNewDevice
from .create_new_room import CreateNewRoom
from .create_new_routine import CreateNewRoutine
from .create_new_scene import CreateNewScene
from .create_new_scene_action import CreateNewSceneAction
from .create_new_schedule import CreateNewSchedule
from .create_routine_action import CreateRoutineAction
from .create_user import CreateUser
from .fetch_devices import FetchDevices
from .get_device_energy_use import GetDeviceEnergyUse
from .get_home_info import GetHomeInfo
from .get_rooms import GetRooms
from .get_routine import GetRoutine
from .get_scene_details import GetSceneDetails
from .get_scenes import GetScenes
from .get_user_info import GetUserInfo
from .switch_to_human import SwitchToHuman
from .toggle_favorite_device import ToggleFavoriteDevice
from .toggle_favorite_scene import ToggleFavoriteScene
from .trigger_notification import TriggerNotification
from .trigger_routine import TriggerRoutine
from .trigger_scene import TriggerScene
from .update_home_device import UpdateHomeDevice
from .update_home_room import UpdateHomeRoom

ALL_TOOLS_INTERFACE_2 = [
    AddNewDevice,
    CreateNewRoom,
    CreateNewRoutine,
    CreateNewScene,
    CreateNewSceneAction,
    CreateNewSchedule,
    CreateRoutineAction,
    CreateUser,
    FetchDevices,
    GetDeviceEnergyUse,
    GetHomeInfo,
    GetRooms,
    GetRoutine,
    GetSceneDetails,
    GetScenes,
    GetUserInfo,
    SwitchToHuman,
    ToggleFavoriteDevice,
    ToggleFavoriteScene,
    TriggerNotification,
    TriggerRoutine,
    TriggerScene,
    UpdateHomeDevice,
    UpdateHomeRoom
]

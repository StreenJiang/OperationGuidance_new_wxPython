import wx
from typing import Type

from models.base import BaseEntity
from utils import CommonUtils
from threads import ToolThread as toolThread
from models.base import ToolBase

# 设备类别
DEVICE_CATEGORY_TOOL = {
    "category_id": 1,
    "icons": {
        "normal": "configs/icons/aneng_screw_gun.png",
        "error": "configs/icons/aneng_screw_gun_error.png"
    }
}
DEVICE_CATEGORY_ARM = {
    "category_id": 2,
    "icons": {
        "normal": "configs/icons/aneng_arm.png",
        "error": "configs/icons/aneng_arm_error.png"
    }
}

# 设备类型
DEVICE_TYPE_TOOL_PF4000 = "PF4000"
DEVICE_TYPE_ARM_CF01 = "CF01"

# 设备状态
DEVICE_STATUS_CONNECTED = {
    "code": 1,
    "icon": "configs/icons/device_connected.png"
}
DEVICE_STATUS_DISCONNECTED = {
    "code": 2,
    "icon": "configs/icons/device_disconnected.png"
}


# 设备实体
class Device(BaseEntity):
    def __init__(self,
                 id,
                 creator,
                 last_updater,
                 device_name: str,
                 device_category: int,
                 device_type: str,
                 device_ip: str,
                 device_port: int,
                 device_status: dict,
                 device_brand: ToolBase = None,
                 create_time = CommonUtils.System_Current_Datetime(),
                 last_update_time = CommonUtils.System_Current_Datetime(),
                 is_deleted = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id                   = id                # 实体id
        self.__device_name          = device_name       # 设备名称
        self.__device_category      = device_category   # 设备类别
        self.__device_type          = device_type       # 设备类型
        self.__device_ip            = device_ip         # 设备ip
        self.__device_port          = device_port       # 设备端口
        self.__device_status        = device_status     # 设备状态
        self.__device_brand         = device_brand      # 设备所属品牌
        self.__device_thread        = None              # 设备连接的线程

    def SetId(self, id: int):
        self.__id = id
    def SetDeviceName(self, device_name: str):
        self.__device_name = device_name
    def SetDeviceCategory(self, device_category: int):
        self.__device_category = device_category
    def SetDeviceType(self, device_type: str):
        self.__device_type = device_type
    def SetDeviceIp(self, device_ip: str):
        self.__device_ip = device_ip
    def SetDevicePort(self, device_port: int):
        self.__device_port = device_port
    def SetDeviceStatus(self, device_status: dict):
        self.__device_status = device_status
    def SetDeviceBrand(self, device_brand: ToolBase):
        self.__device_brand = device_brand

    def GetId(self) -> int:
        return self.__id
    def GetDeviceName(self) -> str:
        return self.__device_name
    def GetDeviceCategory(self) -> int:
        return self.__device_category
    def GetDeviceType(self) -> str:
        return self.__device_type
    def GetDeviceIp(self) -> str:
        return self.__device_ip
    def GetDevicePort(self) -> int:
        return self.__device_port
    def GetDeviceStatus(self) -> dict:
        return self.__device_status
    def GetDeviceBrand(self) -> ToolBase:
        return self.__device_brand
    def GetDeviceThread(self) -> toolThread.ToolThread:
        return self.__device_thread

    def setup_thread(self, window: wx.Window):
        if self.__device_thread is None:
            self.__device_thread = toolThread.ToolThread(window,
                                                         self.__device_brand,
                                                         self.__device_ip,
                                                         self.__device_port),
        return self




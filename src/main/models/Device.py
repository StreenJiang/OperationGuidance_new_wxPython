from src.main.models.base import BaseEntity
from src.main.utils import CommonUtils

# 设备类别
DEVICE_CATEGORY_TOOL = 1
DEVICE_CATEGORY_ARM = 2

# 设备类型
DEVICE_TYPE_TOOL_PF4000 = "PF4000"

DEVICE_TYPE_ARM_CF01 = "CF01"


# 设备实体
class Device(BaseEntity):
    def __init__(self,
                 id,
                 device_name,
                 device_category,
                 device_type,
                 device_ip,
                 device_port,
                 creator,
                 last_updater,
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




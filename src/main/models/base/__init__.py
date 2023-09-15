from abc import ABC, abstractmethod
from typing import Dict

import utils.CommonUtils as CommonUtils


class ToolBase(ABC):
    def __init__(self, brand_name: str = "", operation_commands: Dict[str, str] = None):
        self.__brand_name = brand_name
        self.__operation_commands = operation_commands

    def initiate(self, brand_name: str, operation_commands: Dict[str, str]):
        self.SetBrandName(brand_name)
        self.SetOperationCommands(operation_commands)
        return self

    # --------------------
    # 根据命令CODE获取命令报文
    # --------------------
    def get_command_by_code(self, command_code):
        if self.__operation_commands is not None and command_code in self.__operation_commands.keys():
            return self.__operation_commands[command_code]
        return None

    # --------------------
    # 获取命令中的extra（由每个子类自己实现）
    # --------------------
    @abstractmethod
    def get_command_extra(self, extra_type, *arg):
        pass

    def SetBrandName(self, brand_name: str):
        self.__brand_name = brand_name
    def SetOperationCommands(self, operation_commands: Dict[str, str]):
        self.__operation_commands = operation_commands

    def GetBrandName(self) -> str:
        return self.__brand_name
    def GetOperationCommands(self) -> Dict[str, str]:
        return self.__operation_commands



# 所有数据实体的父类
class BaseEntity:
    def __init__(self,
                 creator: str = None,
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_updater: str = None,
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        self.__creator = creator                    # 创建人
        self.__create_time = create_time            # 创建时间
        self.__last_updater = last_updater          # 最后修改人
        self.__last_update_time = last_update_time  # 最后修改时间
        self.__is_deleted = is_deleted              # 是否删除（使数据实现软删除）

    def SetCreator(self, creator: str):
        self.__creator = creator
    def SetCreateTime(self, create_time: str):
        self.__create_time = create_time
    def SetLastUpdater(self, last_updater: str):
        self.__last_updater = last_updater
    def SetLastUpdateTime(self, last_update_time: str):
        self.__last_update_time = last_update_time
    def Delete(self, flag: bool):
        self.__is_deleted = flag

    def GetCreator(self) -> str:
        return self.__creator
    def GetCreateTime(self) -> str:
        return self.__create_time
    def GetLastUpdater(self) -> str:
        return self.__last_updater
    def GetLastUpdateTime(self) -> str:
        return self.__last_update_time
    def IsDelete(self) -> bool:
        return self.__is_deleted



import encodings
import os
import yaml

from abc import ABC, abstractmethod

from src.main.enums.Notice_Enum import NoticeEnum


class ToolBaseEntity(ABC):

    def __init__(self):
        self.__operation_commands = None
        self.__variables = None
        self.__log_path = None

        self.initialize_log_path()


    # --------------------
    # 初始化命令清单
    # --------------------
    @abstractmethod
    def initialize_commands(self):
        pass

    # --------------------
    # 初始化参数
    # --------------------
    @abstractmethod
    def initialize_variables(self, ip, port):
        pass

    # --------------------
    # 根据命令CODE获取命令报文
    # --------------------
    def get_command_by_code(self, command_code):
        if self.operation_commands is not None and command_code in self.operation_commands.keys():
            return self.operation_commands[command_code]
        return None

    # --------------------
    # 获取命令中的extra（由每个子类自己实现）
    # --------------------
    @abstractmethod
    def get_command_extra(self, extra_type, *arg):
        pass

    @property
    def log_path(self):
        return self.__log_path

    @property
    def operation_commands(self):
        return self.__operation_commands

    @operation_commands.setter
    def operation_commands(self, operation_commands):
        self.__operation_commands = operation_commands

    @property
    def variables(self):
        return self.__variables

    @variables.setter
    def variables(self, variables):
        self.__variables = variables

    # --------------------
    # 初始化日志记录路径
    # --------------------
    def initialize_log_path(self):
        file = None
        # 获取当前系统所在路径
        current_path = os.path.abspath("")
        try:
            # 获取ymal文件路径
            yaml_path = os.path.join(current_path, "configs/application_dev.yml")
            # 打开文件
            file = open(yaml_path, 'r', encoding = encodings.utf_8.getregentry().name)
            # 读取文件内容
            yml_data = file.read()

            # 转换为字典类型
            yml_dict = yaml.full_load(yml_data)
            self.__log_path = [current_path + yml_dict["application"]["file_path_parent"]]
        except Exception as e:
            self.__log_path = [current_path + "/"]
            NoticeEnum.Log(self, None, NoticeEnum.APPLICATION_CONFIG_ERROR, str(e))
        finally:
            if file is not None:
                file.close()


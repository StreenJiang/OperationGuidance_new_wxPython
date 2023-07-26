from abc import ABC, abstractmethod


class ToolBaseEntity(ABC):

    def __init__(self):
        self.__operation_commands = None
        self.__variables = None
        self.__log_path = None

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

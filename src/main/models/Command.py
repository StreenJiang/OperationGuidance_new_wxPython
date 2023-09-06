from enums.Command_Type_Enum import CommandTypeEnum
from enums.Operation_Enum import OperationEnum
from exceptions.Custom_Exception import ArgumentTypeException


class Command:
    def __init__(self,
                 command_type = CommandTypeEnum.DEFAULT,
                 operation = OperationEnum.DEFAULT,
                 extra = None,
                 command = None,
                 ):

        if not isinstance(command_type, CommandTypeEnum):
            raise ArgumentTypeException(command_type, "argument's type of 'command' is incorrect, should be 'CommandEnum'.")
        self.__command_type = command_type

        if not isinstance(operation, OperationEnum):
            raise ArgumentTypeException(operation, "argument's type of 'operation' is incorrect, should be 'OperationEnum'.")
        self.__operation = operation

        if extra is not None and not isinstance(extra, tuple):
            raise ArgumentTypeException(extra, "argument's type of 'extra' is incorrect, should be 'tuple'.")
        self.__extra = extra

        self.__command = command
        self.__send_times = 0


    @property
    def command(self):
        return self.__command

    @command.setter
    def command(self, command):
        if command is not None and isinstance(command, str):
            self.__command = command
            if self.__extra is not None and self.__extra != ():
                self.__command = self.__command % self.__extra

    @property
    def operation(self):
        return self.__operation

    @operation.setter
    def operation(self, operation):
        self.__operation = operation

    @property
    def command_type(self):
        return self.__command_type

    @command_type.setter
    def command_type(self, command_type):
        self.__command_type = command_type

    @property
    def extra(self):
        return self.__extra

    @extra.setter
    def extra(self, extra):
        self.__extra = extra

    @property
    def send_times(self):
        return self.__send_times

    @send_times.setter
    def send_times(self, send_times):
        self.__send_times = send_times



if __name__ == '__main__':
    cmd = Command(CommandTypeEnum.OPERATION, "", None)
    print(cmd)


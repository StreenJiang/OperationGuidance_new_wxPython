from src.main.enums.Notice_Enum import NoticeEnum


class ArgumentTypeException(Exception):
    def __init__(self, argument, error_msg):
        Exception.__init__(self, error_msg)
        NoticeEnum.Log(self, None, NoticeEnum.ARGUMENT_ERROR, argument)



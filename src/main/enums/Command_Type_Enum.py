from enum import Enum, unique


@unique
class CommandTypeEnum(Enum):
    """
        All kinds of commands
    """

    DEFAULT = ""
    OPERATION = "mid"
    SWITCH_PSET = "pset"
    UPDATE_STATION = "station"



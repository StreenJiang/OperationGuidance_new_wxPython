from enum import Enum, unique

@unique
class CacheEnum(Enum):

    # 产品任务数据
    MISSION_DATA    = {"key": "MISSION_DATA",   "timeout": 120}
    # 设备列表数据
    DEVICES         = {"key": "DEVICES",        "timeout": 120}



from enum import Enum, unique


@unique
class OperationEnum(Enum):
    """
        All kinds of operations
    """

    DEFAULT = "0000"          # 默认
    KEEP_ALIVE = "9999"       # 心跳

    UNKNOWN_YET = "0001"      # 目前未知
    UNKNOWN_YET1 = "0003"      # 目前未知
    UNKNOWN_YET2 = "0010"      # 目前未知

    SWITCH_PSET = "0018"      # 下发PSET（切换程序）
    LOCK_DEVICE = "0042"      # 锁枪（禁用工具）
    UNLOCK_DEVICE = "0043"    # 解锁（使能工具）
    UPLOAD_IDENTIFY = "0051"  # 上传条码报文
    READ_DATA = "0060"        # 读数据（读取拧紧结果[无实时拧紧数据]
    RESPOND_DATA = "0062"     # 应答上载数据报文
    WRITE_CODE = "0150"       # 写入条码（或二维码）（阿塔斯里是：下载条码报文）
    UPLOAD_INPUT = "0210"     # <input状态>上传
    RESPOND_INPUT = "0212"    # <input状态>应答报文

    RESPOND_INPUT1 = "0216"    # Relay function subscribe
    RESPOND_INPUT2 = "0218"    # Relay function acknowledge
    RESPOND_INPUT3 = "0224"    # 设置<input>报文
    RESPOND_INPUT4 = "0225"    # 复位<input>报文
    RESPOND_INPUT5 = "0900T"   # 扭矩曲线/=PF6000
    RESPOND_INPUT6 = "0900A"   # 角度曲线/=PF6000
    RESPOND_INPUT7 = "0900"    # 扭矩+角度曲线/=PF6000
    RESPOND_INPUT8 = "0900K"   # 曲线应答/=PF6000

    # 其他的所有命令的类型都可以列在一个地方，其他地方调用即可



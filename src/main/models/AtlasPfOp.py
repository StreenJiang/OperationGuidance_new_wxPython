from enums.Command_Type_Enum import CommandTypeEnum
from enums.Operation_Enum import OperationEnum
from models.Command import Command
from models.base import ToolBase


class AtlasPfOpEntity(ToolBase):

    def __init__(self):
        ToolBase.__init__(self)

        # 设定自己的个性化 extra 类型
        self.SWITCH_PSET = "1"
        self.WRITE_IDENTIFY = "2"

    # --------------------
    # 初始化命令清单
    # --------------------
    def initialize_commands(self):
        self.operation_commands = {
            OperationEnum.KEEP_ALIVE:       '00209999            \x00',    # keep alive[读取控制器当前程序号]
            OperationEnum.LOCK_DEVICE:      '00200042001         \x00',    # 禁用工具
            OperationEnum.UNLOCK_DEVICE:    '00200043001         \x00',    # 使能工具[拧紧结束后上传数据]
            OperationEnum.SWITCH_PSET:      '00230018001         %s\x00',  # 下发PSET[程序号,校验码]
            OperationEnum.READ_DATA:        '002000600010        \x00',    # <上载数据>报文
            OperationEnum.RESPOND_DATA:     '00200062001         \x00',    # <应答上载数据>报文
            OperationEnum.WRITE_CODE:       '%s01500011        %s\x00',    # 下载条码报文
            OperationEnum.UPLOAD_INPUT:     '002002100010        \x00',    # <input状态>上传
            OperationEnum.RESPOND_INPUT:    '00200212001         \x00',    # <input状态>应答报文
            # .
            # .
            # .
        }


    # --------------------
    # 初始化参数
    # --------------------
    def initialize_variables(self, ip, port):
        self.variables = {
            "socket": None,             # socket server对象
            'quit': False,              # 初始化<退出线程>标志
            'stop': False,              # 初始化<断开线程>标志
            'connected': False,         # 初始化<连接状态>标志
            'ip': ip,                   # ip地址
            'port': port,               # 端口号
            'timeout': 3,               # 超时时间
            'version': ['0001', '3'],   # 控制器版本
            'station': [                # 工站信息
                'Tool',
                'OP10',
                '1',
                ip
            ],
            'controllers': 'PF6000',    # 控制器类别
            'commands': [               # 命令队列
                # 心跳命令
                Command(command_type = CommandTypeEnum.OPERATION,
                        operation = OperationEnum.KEEP_ALIVE,
                        extra = None,
                        command = self.get_command_by_code(OperationEnum.KEEP_ALIVE)),
                # 锁枪命令（初始化时先锁枪，保证安全）
                Command(command_type = CommandTypeEnum.OPERATION,
                        operation = OperationEnum.LOCK_DEVICE,
                        extra = None,
                        command = self.get_command_by_code(OperationEnum.LOCK_DEVICE)),
            ],
            'delayA': 0.02,             # 延时：2ms
            'delayB': 0.1,              # 延时：100ms
            'delayC': 0.5,              # 延时：500ms
            'countA': 3,                # 计数量：3
            'countB': 10,               # 计数量：10
            'countC': 100,              # 计数量：100
            'counterA': 0,              # 计数器：A<recv socket time out>
            'counterB': 0,              # 计数器：B<发送命令失败次数>
            'counterC': 0,              # 计数器：C<发送命令-未收到反馈次数>
            'identify': '',             # 条码
            'pset': '0',                # 程序号缓存[下发的程序号,控制器程序号]
            'tightening': {},           #
            'binding': [],              # 拧紧数据类别缓存
            'read': b"",                #
            'screwCount': 0,            # 当前拧紧次数
        }


    # --------------------
    # 获取命令中的extra（根据速动的规则个性化的方法）
    # --------------------
    def get_command_extra(self, extra_type, set_no):
        if extra_type == self.SWITCH_PSET:
            return set_no, self.variables["crc"][set_no]
        elif extra_type == self.WRITE_IDENTIFY:
            return ""
        else:
            return None




from enums.Command_Type_Enum import CommandTypeEnum
from enums.Operation_Enum import OperationEnum
from models.Command import Command
from models.base import ToolBaseEntity


class SudongEntity(ToolBaseEntity):

    def __init__(self):
        ToolBaseEntity.__init__(self)

        # 设定自己的个性化 extra 类型
        self.SWITCH_PSET = "1"
        self.WRITE_IDENTIFY = "2"

    # --------------------
    # 初始化命令清单
    # --------------------
    def initialize_commands(self):
        self.operation_commands = {
            OperationEnum.KEEP_ALIVE:       '55AA06030600E72E0D0A',     # keep alive[读取控制器当前程序号]
            OperationEnum.LOCK_DEVICE:      '55AA070100020000000D0A',   # 禁用工具
            OperationEnum.UNLOCK_DEVICE:    '55AA070100000000000D0A',   # 使能工具[拧紧结束后上传数据]
            OperationEnum.SWITCH_PSET:      '55AA07020500%s%s0D0A',     # 下发PSET[程序号,校验码]
            OperationEnum.READ_DATA:        '55AA070100000000000D0A',   # 读取拧紧结果[无实时拧紧数据]
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
            'station': [                # 工站信息
                'Tool',
                'OP10',
                '1',
                ip
            ],
            'controllers': 'sudong',    # 控制器类别
            'crc': {                    # crc16检验码
                '01': '63B6',               # 1号程序
                '02': '23b7',               # 2号程序
                '03': 'e277',               # 3号程序
                '04': 'a3b5',               # 4号程序
                '05': '6275',               # 5号程序
                '06': '2274',               # 6号程序
                '07': 'e3b4',               # 7号程序
                '08': 'a3b0',               # 8号程序
                '09': '6270',               # 9号程序
                '10': 'a3ba',               # 10号程序
                '11': '627a',               # 11号程序
                '12': '227b',               # 12号程序
                '13': 'e3bb',               # 13号程序
                '14': 'a279',               # 14号程序
                '15': '63b9',               # 15号程序
            },
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
            'binding': [],              # 拧紧数据类别缓存
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




from enums.Command_Type_Enum import CommandTypeEnum
from enums.Operation_Enum import OperationEnum
from models.Command import Command
from models.base import ToolBase


class ToolSudong(ToolBase):
    def __init__(self):
        ToolBase.__init__(self)
        self.crc = {                    # crc16检验码
            '01': '63B6',                   # 1号程序
            '02': '23b7',                   # 2号程序
            '03': 'e277',                   # 3号程序
            '04': 'a3b5',                   # 4号程序
            '05': '6275',                   # 5号程序
            '06': '2274',                   # 6号程序
            '07': 'e3b4',                   # 7号程序
            '08': 'a3b0',                   # 8号程序
            '09': '6270',                   # 9号程序
            '10': 'a3ba',                   # 10号程序
            '11': '627a',                   # 11号程序
            '12': '227b',                   # 12号程序
            '13': 'e3bb',                   # 13号程序
            '14': 'a279',                   # 14号程序
            '15': '63b9',                   # 15号程序
        }
        self.timeout = 3                # 超时时间
        self.station = [                # 工站信息
            'Tool',
            'OP10',
            '1'
        ]
        self.controllers = 'sudong',    # 控制器类别
        self.delayA = 0.02,             # 延时：2ms
        self.delayB = 0.1,              # 延时：100ms
        self.delayC = 0.5,              # 延时：500ms
        self.countA = 3,                # 计数量：3
        self.countB = 10,               # 计数量：10
        self.countC = 100,              # 计数量：100
        self.counterA = 0,              # 计数器：A<recv socket time out>
        self.counterB = 0,              # 计数器：B<发送命令失败次数>
        self.counterC = 0,              # 计数器：C<发送命令-未收到反馈次数>
        self.identify = '',             # 条码
        self.pset = '0',                # 程序号缓存[下发的程序号,控制器程序号]
        self.binding = [],              # 拧紧数据类别缓存
        self.screwCount = 0,            # 当前拧紧次数

        self.initiate(
            brand_name = "速动",
            operation_commands = {
                OperationEnum.KEEP_ALIVE:       '55AA06030600E72E0D0A',     # keep alive[读取控制器当前程序号]
                OperationEnum.LOCK_DEVICE:      '55AA070100020000000D0A',   # 禁用工具
                OperationEnum.UNLOCK_DEVICE:    '55AA070100000000000D0A',   # 使能工具[拧紧结束后上传数据]
                OperationEnum.SWITCH_PSET:      '55AA07020500%s%s0D0A',     # 下发PSET[程序号,校验码]
                OperationEnum.READ_DATA:        '55AA070100000000000D0A',   # 读取拧紧结果[无实时拧紧数据]
            }
        )
    #     self.commands = [  # 命令队列
    #         # 心跳命令
    #         Command(command_type = CommandTypeEnum.OPERATION,
    #                 operation = OperationEnum.KEEP_ALIVE,
    #                 extra = None,
    #                 command = self.get_command_by_code(OperationEnum.KEEP_ALIVE)),
    #         # 锁枪命令（初始化时先锁枪，保证安全）
    #         Command(command_type = CommandTypeEnum.OPERATION,
    #                 operation = OperationEnum.LOCK_DEVICE,
    #                 extra = None,
    #                 command = self.get_command_by_code(OperationEnum.LOCK_DEVICE)),
    #     ],

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


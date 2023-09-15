import wx
import binascii
import threading
import socket
import time
from typing import List

import utils.CommonUtils as CommonUtils
from enums.Command_Type_Enum import CommandTypeEnum
from enums.Notice_Enum import NoticeEnum
from enums.Operation_Enum import OperationEnum
from models.Command import Command
from models.base import ToolBase


# --------------------
# 工具线程类
# --------------------
class ToolThread(threading.Thread):
    def __init__(self,
                 window: wx.Window,
                 entity: ToolBase,
                 ip: str,
                 port: int):
        threading.Thread.__init__(self)
        self.window = window
        self.entity = entity
        self.socket = None
        self.connected = False
        self.working = False
        self.commands_queue = []

        # 初始化数据
        self.entity.initialize_variables(ip, port)

        # 设置socket超时时间
        self.timeout = self.entity.variables["timeout"]
        socket.setdefaulttimeout(self.timeout)

        # 重连次数上限
        self.connect_times = 0
        self.connect_times_max = 5


    # --------------------
    # 组装命令并塞入命令队列中等待命令发送
    # --------------------
    def add_command_into_queue(self, commands):
        for command in commands:
            # self.entity.variables['commands'].append(command)
            self.commands_queue.append(command)


    # --------------------
    # 线程主体
    # --------------------
    def run(self):
        # 线程主循环
        while not self.entity.variables['quit']:
            self.Run_Process()

        # 退出循环时执行
        self.entity.variables['stop'] = True


    # --------------------
    # 循环线程
    # --------------------
    def Run_Process(self):
        # 检查网络是否已连接
        if self.entity.variables['connected']:
            try:
                # 根据命令队列，向服务器发送命令数据
                self.send_msg_to_socket_server()

                # 读取服务器返回数据
                self.Read_Master_Socket()

                # 循环延时
                time.sleep(self.entity.variables['delayA'])

            # 如果异常，则断开连接
            except Exception as e:
                # 断开线程
                self.Disconnect_Network(str(e))
        # 如果没连接则连接网络
        else:
            # 初始化socket server并连接网络
            self.Connect_Socket_Server()


    # --------------------
    # 创建socket server并连接网络
    # --------------------
    def Connect_Socket_Server(self):
        try:
            # 记录连接次数
            self.connect_times += 1
            # 超过最高连接次数则 TODO: 后续需要做什么再优化
            if self.connect_times > self.connect_times_max:
                NoticeEnum.Log(self, NoticeEnum.RECONNECT_TOO_MANY_TIMES)
                # TODO: 暂时先中断线程
                self.stop()
                return

            ip = self.entity.variables["ip"]
            port = self.entity.variables["port"]

            # 连接socket server
            self.entity.variables["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.entity.variables["socket"].connect((ip, port))

            self.entity.variables["connected"] = True
            self.working = True
            self.connected = True
            NoticeEnum.Log(self, NoticeEnum.NETWORK_CONNECTED)
        # 连接socket server失败
        except Exception as e:
            # 断开线程
            self.Disconnect_Network(str(e))


    # --------------------
    # 断开与socket server的连接
    # --------------------
    def Disconnect_Network(self, error_msg):
        # 断开socket server的连接
        if self.entity.variables["socket"] is not None:
            self.entity.variables["socket"].close()
            self.entity.variables["socket"] = None
            NoticeEnum.Log(self, NoticeEnum.NETWORK_DISCONNECTED)
        else:
            NoticeEnum.Log(self, NoticeEnum.CONNECTION_ALREADY_CLOSED)

        if error_msg is not None:
            if error_msg == "timed out":
                NoticeEnum.Log(self, NoticeEnum.CONNECT_TIME_OUT, self.timeout)
            else:
                NoticeEnum.Log(self, NoticeEnum.CONNECT_FAILED, error_msg)

        # 修改连接标志
        self.entity.variables['connected'] = False

        # 修改停止标志
        self.entity.variables['quit'] = True

        # 清空命令队列
        self.entity.variables['commands'] = []

        # 将主线程中的此线程剔除
        self.window.thread['sudong_tool'] = None


    # --------------------
    # 向socket发送数据
    # --------------------
    def send_msg_to_socket_server(self):
        commands = self.entity.variables['commands']

        # 判断是否需要发送命令
        if not self.entity.variables['quit'] and commands:
            # 从队列最前端拿到第一个命令对象
            command = commands[0]

            # 发送次数+1
            send_times = command.send_times + 1

            midNo = command.operation
            command_msg = command.add_command_into_queue

            if command.extra is not None:
                command_msg = command_msg % command.extra

            # 发送数据
            # TODO: 这个判断条件对2取模不太理解，并且为什么‘countA’还需要乘以2，直接设置为2倍会有什么问题吗？
            if send_times % 2 == 1 and send_times <= self.entity.variables['countA'] * 2:
                try:
                    NoticeEnum.Log(self, NoticeEnum.SEND_MSG_TO_SERVER, midNo, command_msg)

                    # 转换报文
                    message = binascii.a2b_hex(command_msg)
                    # 发送报文
                    self.entity.variables["socket"].send(message)

                    # 从队列中删除已经发送的命令
                    del commands[0]
                # 发送数据失败
                except Exception as e:
                    error_msg = str(e)
                    NoticeEnum.Log(self, NoticeEnum.SEND_MSG_FAILED, error_msg, command_msg)
                    
                    # 发送失败，断开连接
                    self.Disconnect_Network(error_msg)
            # 删除发送失败报文
            # TODO: 这个判断条件意味着超出发送次数，但为什么只有elif，没有else的情况？
            elif send_times > self.entity.variables['countA'] * 2:
                del commands[0]


    # --------------------
    # 读取socket server发送过来的数据
    # --------------------
    def Read_Master_Socket(self):
        try:
            # 接收报文
            received_message = self.entity.variables["socket"].recv(10240)  # .decode()#.strip('\x00')

            # 判断返回的数据是否为空数据
            if received_message != b'':
                # 复位<接收超时>次数计数
                self.entity.variables['counterA'] = 0

                # 数据格式转换
                received_message = binascii.b2a_hex(received_message).decode().upper()

                # 数据解析
                try:
                    self.Decode_received_message(received_message)
                except Exception as e:
                    NoticeEnum.Log(self, NoticeEnum.DECODE_MSG_FAILED, str(e), received_message)
            # 如果数据为空
            else:
                NoticeEnum.Log(self, NoticeEnum.READ_MSG_EMPTY, received_message)
                # 向命令队列加入心跳报文
                self.entity.variables["commands"].append(
                    Command(command_type = CommandTypeEnum.OPERATION,
                            operation = OperationEnum.KEEP_ALIVE,
                            extra = None,
                            command = self.entity.get_command_by_code(OperationEnum.KEEP_ALIVE)),
                )
        # 接收数据失败
        except Exception as e:
            # 计数
            self.entity.variables['counterA'] += 1

            # 断开次数未达到上限则继续发送心跳报文
            if self.entity.variables['countA'] <= self.entity.variables['counterA'] < self.entity.variables['countB']:
                self.entity.variables["commands"].append(
                    Command(command_type = CommandTypeEnum.OPERATION,
                            operation = OperationEnum.KEEP_ALIVE,
                            extra = None,
                            command = self.entity.get_command_by_code(OperationEnum.KEEP_ALIVE)),
                )
            # 断开次数过高
            elif self.entity.variables['counterA'] >= self.entity.variables['countB']:
                # 断开线程
                self.Disconnect_Network(str(e))


    # --------------------
    # 解析解析从socket server返回的数据
    # --------------------
    def Decode_received_message(self, received_message):
        head = received_message[:10]

        # 工具运行状态
        if head == '55AA058500':
            pass
        # 拧紧数据
        elif head == '55AA278100':
            # 01-拧紧扭力
            finalTorque = received_message[14:18]
            finalTorque = (finalTorque[2:4] + finalTorque[:2])
            finalTorque = str(round(int(finalTorque, 16) / 1000, 2))

            # 02-拧紧扭力[上限]
            finalTorqueMax = received_message[48:52]
            finalTorqueMax = (finalTorqueMax[2:4] + finalTorqueMax[:2])
            finalTorqueMax = str(round(int(finalTorqueMax, 16) / 1000, 2))

            # 03-拧紧扭力[下限]
            finalTorqueMin = received_message[52:56]
            finalTorqueMin = (finalTorqueMin[2:4] + finalTorqueMin[:2])
            finalTorqueMin = str(round(int(finalTorqueMin, 16) / 1000, 2))

            # 04-拧紧扭力[目标]
            finalTorqueTarget = '0.0'

            # 06-拧紧角度
            finalAngle = received_message[26:30]
            finalAngle = (finalAngle[2:4] + finalAngle[:2])
            finalAngle = str(int(finalAngle, 16))

            # 07-拧紧角度[上限]
            finalAngleMax = received_message[56:60]
            finalAngleMax = (finalAngleMax[2:4] + finalAngleMax[:2])
            finalAngleMax = str(int(finalAngleMax, 16))

            # 08-拧紧角度[下限]
            finalAngleMin = received_message[60:64]
            finalAngleMin = (finalAngleMin[2:4] + finalAngleMin[:2])
            finalAngleMin = str(int(finalAngleMin, 16))

            # 09-拧紧角度[目标]
            finalAngleTarget = '0'

            # 10-锁附（旋入）扭力
            fitTorque = '0.0'
            fitTorqueMax = '0.0'
            fitTorqueTarget = '0.0'
            fitTorqueMin = '0.0'

            # 16-锁附（旋入）角度
            fitAngle = received_message[22:26]
            fitAngle = (fitAngle[2:4] + fitAngle[:2])
            fitAngle = str(int(fitAngle, 16))

            # 17-锁附（旋入）角度[上限]
            fitAngleMax = received_message[64:68]
            fitAngleMax = (fitAngleMax[2:4] + fitAngleMax[:2])
            fitAngleMax = str(int(fitAngleMax, 16))

            # 18-锁附（旋入）角度[下限]
            fitAngleMin = received_message[68:72]
            fitAngleMin = (fitAngleMin[2:4] + fitAngleMin[:2])
            fitAngleMin = str(int(fitAngleMin, 16))

            # 19-锁附（旋入）角度[目标]
            fitAngleTarget = '0'

            # 20-拧紧状态
            finalStatus = received_message[42:44]

            # 21-拧紧状态
            if finalStatus == '01':
                finalStatus = 'OK'
            # 22-拧紧状态
            elif finalStatus == '04':
                finalStatus = 'CCW'
            # 23-拧紧状态
            else:
                finalStatus = 'NG'

            # 24-拧紧状态[torque,angle]
            finalStatusT, finalStatusA = finalStatus, finalStatus

            # 26-拧紧状态/=锁附（旋入）
            fitStatus = 'OK'
            fitStatusT = 'OK'
            fitStatusA = 'OK'

            # 30-拧紧数据[pset number]
            psetNo = self.entity.variables['pset']

            # 31-拧紧数据[pset name]
            psetName = ''

            # 31-拧紧数据[batch]
            batchCount = '0'
            batchSize = '0'
            batchStatus = 'OK'

            # 32-拧紧数据[sequence]
            sequNo = '0'
            sequName = ''
            sequcount = '0'
            sequSize = '0'
            sequStatus = 'OK'

            # 33-拧紧数据/=条码
            identify = self.entity.variables['identify']

            # 34-拧紧数据/=时间戳据
            timeStamp = CommonUtils.System_Current_Datetime('%Y%m%d%H%M%S')

            # 35-拧紧数据/=拧紧Id
            idStamp = '0000000000'

            # 36-拧紧数据/=当前拧紧次数
            self.entity.variables['screwCount'] += 1

            # 40-数据组合
            valueC = [psetNo, psetName,
                      fitStatus, fitStatusT, fitStatusA,
                      fitTorque, fitTorqueMax, fitTorqueTarget, fitTorqueMin,
                      fitAngle, fitAngleMax, fitAngleTarget, fitAngleMin,
                      finalStatus, finalStatusT, finalStatusA,
                      finalTorque, finalTorqueMax, finalTorqueTarget, finalTorqueMin,
                      finalAngle, finalAngleMax, finalAngleTarget, finalAngleMin,
                      batchCount, batchSize, batchStatus,
                      sequNo, sequName, sequcount, sequSize, sequStatus,
                      identify, timeStamp, idStamp]

            # 41-数据组合/=添加工站信息
            valueC = (valueC + self.entity.variables['station'])

            # 23-数据组合/=添加拧紧次数
            valueC.append(str(self.entity.variables['screwCount']))

            # 打印数据 TODO
            print("拧紧数据：%s", valueC)

        # 当前运行程序号
        elif head == '55AA078306':
            pass

        # 程序号下发完成标志
        elif head == '55AA058205':
            pass


    # --------------------
    # 中止线程
    # --------------------
    def stop(self):
        # 退出标志位
        self.entity.variables['quit'] = True
        # 退出标志位
        self.entity.variables['stop'] = True
        # 断开连接
        self.Disconnect_Network(None)


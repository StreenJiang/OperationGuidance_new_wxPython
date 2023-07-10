# -*- coding: utf-8 -*-
__author__ = 'Maple'

# ******************************
# 模块说明
# ******************************
'''
ver = 1.0.0
date= 2021-05-11/creatClass
name= round_static_box
'''

# ******************************
# B01-导入模块
# ******************************
from win32api import GetSystemMetrics  # 获取屏幕分辨率
import wx

# ------------------------------
# B02-导入自建模块
# ------------------------------
from src.main.enums.Command_Type_Enum import CommandTypeEnum
from src.main.enums.Operation_Enum import OperationEnum
from src.main.models.Command import Command
from src.main.models.SudongEntity import SudongEntity
from src.main.threads.ToolThread import ToolThread

# ******************************
# C01-主程序块
# ******************************
class MainProgram(wx.Frame):
    def __init__(self, parent, id, title, frame_size):
        wx.Frame.__init__(self,
                          parent,
                          id,
                          title,
                          size = frame_size,
                          style = wx.MINIMIZE_BOX |  # 最小化
                                  wx.MAXIMIZE_BOX |  # 最大化
                                  wx.RESIZE_BORDER |  # 尺寸可调整
                                  wx.SYSTEM_MENU |  # 系统面板
                                  wx.CAPTION |
                                  wx.CLOSE_BOX |
                                  wx.CLIP_CHILDREN)

        # --------------------
        # 01-初始化
        # --------------------
        # self.Centre()
        self.SetBackgroundColour('#A6A6A6')

        # --------------------
        # 02-设置字体
        # --------------------
        self.SetFont(wx.Font(12,
                             wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL,  # BOLD,
                             False,
                             u'微软雅黑'))

        # --------------------
        # 03-初始化系统参数
        # --------------------
        self.Initial_App_Variate()

        # --------------------
        # 09-总布局
        # --------------------
        mainBox = wx.BoxSizer()
        mainBox.Add(self.Main_Layout(), 2, wx.EXPAND, 0)
        self.SetSizer(mainBox)

    # ------------------------------
    # M01-初始化系统参数
    # ------------------------------
    def Initial_App_Variate(self):

        # --------------------
        # 01-控件
        # --------------------
        self.widget = {}

        # --------------------
        # 03-thread
        # --------------------
        self.thread = {
            "tool": None
        }

    # ------------------------------
    # M10-主窗体布局
    # ------------------------------
    def Main_Layout(self):

        # --------------------
        # 01-布局
        # --------------------
        localBox = wx.GridBagSizer()

        # --------------------
        # 10-IP
        # --------------------
        localBox.Add(wx.StaticText(self, -1, 'IP:'), pos = (0, 0), flag = wx.LEFT | wx.UP | wx.ALIGN_RIGHT, border = 10)
        self.widget['ip'] = wx.TextCtrl(self, -1, '192.168.1.16', size = (200, -1))
        localBox.Add(self.widget['ip'], pos = (0, 1), flag = wx.ALL, border = 5)

        # --------------------
        # 11-PORT
        # --------------------
        localBox.Add(wx.StaticText(self, -1, 'PORT:'), pos = (0, 2), flag = wx.LEFT | wx.UP | wx.ALIGN_RIGHT,
                     border = 10)
        self.widget['port'] = wx.TextCtrl(self, -1, '1200', size = (80, -1))
        localBox.Add(self.widget['port'], pos = (0, 3), flag = wx.ALL, border = 5)

        # --------------------
        # 12-Link button
        # --------------------
        self.widget['linkBtn'] = wx.Button(self, -1, u'连接网络', size = (120, -1), name = 'linkBtn')
        self.widget['linkBtn'].Bind(wx.EVT_BUTTON, self.Thread_Conncent)
        localBox.Add(self.widget['linkBtn'], pos = (0, 4), flag = wx.ALL, border = 5)

        # --------------------
        # 13-Disink button
        # --------------------
        self.widget['dislinkBtn'] = wx.Button(self, -1, u'断开网络', size = (120, -1), name = 'dislinkBtn')
        self.widget['dislinkBtn'].Bind(wx.EVT_BUTTON, self.Thread_Disconncent)
        localBox.Add(self.widget['dislinkBtn'], pos = (0, 5), flag = wx.ALL, border = 5)

        # --------------------
        # 20-PSET
        # --------------------
        localBox.Add(wx.StaticText(self, -1, 'pset:'), pos = (1, 2), flag = wx.LEFT | wx.UP | wx.ALIGN_RIGHT,
                     border = 10)
        self.widget['pset'] = wx.TextCtrl(self, -1, '1', size = (80, -1))
        localBox.Add(self.widget['pset'], pos = (1, 3), flag = wx.ALL, border = 5)

        # --------------------
        # 21-PSET button
        # --------------------
        self.widget['psetBtn'] = wx.Button(self, -1, u'程序写入', size = (120, -1), name = 'psetBtn')
        self.widget['psetBtn'].Bind(wx.EVT_BUTTON, self.Thread_Write_Pset)
        localBox.Add(self.widget['psetBtn'], pos = (1, 4), flag = wx.ALL, border = 5)

        # --------------------
        # 30-lock tightening button
        # --------------------
        # self.widget['cwBtn'] = wx.ToggleButton(self,-1,u'锁住工具-拧紧',size=(120,-1),name='cwBtn')
        # self.widget['cwBtn'].Bind(wx.EVT_TOGGLEBUTTON,self.Button_Bind)
        # localBox.Add(self.widget['cwBtn'],pos=(2,1),flag=wx.ALL|wx.ALIGN_RIGHT,border=5)

        # --------------------
        # 31-lock loosenning button
        # --------------------
        # self.widget['ccwBtn'] = wx.ToggleButton(self,-1,u'锁住工具-反松',size=(120,-1),name='ccwBtn')
        # self.widget['ccwBtn'].Bind(wx.EVT_TOGGLEBUTTON,self.Button_Bind)
        # localBox.Add(self.widget['ccwBtn'],pos=(2,2),span=(1,2),flag=wx.ALL|wx.ALIGN_CENTRE,border=5)

        # --------------------
        # 32-enable tool
        # --------------------
        self.widget['enableTool'] = wx.Button(self, -1, u'使能工具', size = (120, -1), name = 'enableTool')
        self.widget['enableTool'].Bind(wx.EVT_BUTTON, self.Thread_Enable_Tool)
        localBox.Add(self.widget['enableTool'], pos = (2, 4), flag = wx.ALL, border = 5)

        # --------------------
        # 33-enable tool
        # --------------------
        self.widget['disableTool'] = wx.Button(self, -1, u'禁用工具', size = (120, -1), name = 'disableTool')
        self.widget['disableTool'].Bind(wx.EVT_BUTTON, self.Thread_Disable_Tool)
        localBox.Add(self.widget['disableTool'], pos = (2, 5), flag = wx.ALL, border = 5)

        # --------------------
        # 40-条码
        # --------------------
        localBox.Add(wx.StaticText(self, -1, '条码:'), pos = (3, 0), flag = wx.LEFT | wx.UP | wx.ALIGN_RIGHT,
                     border = 10)
        self.widget['identify'] = wx.TextCtrl(self, -1, '1234567890ABCDEFGHIJKLMNOPQRST', size = (200, -1))
        localBox.Add(self.widget['identify'], pos = (3, 1), span = (1, 4), flag = wx.ALL | wx.EXPAND, border = 5)

        # --------------------
        # 41-identify button
        # --------------------
        self.widget['identifyBtn'] = wx.Button(self, -1, u'发送条码', size = (120, -1), name = 'identify')
        self.widget['identifyBtn'].Bind(wx.EVT_BUTTON, self.Thread_Write_Identify)
        localBox.Add(self.widget['identifyBtn'], pos = (3, 5), flag = wx.ALL, border = 5)

        # print (self.widget['disableTool'].GetBestSize())

        # --------------------
        # 99-返回布局
        # --------------------
        return localBox

    # ------------------------------
    # 创建线程对象并启动线程
    # ------------------------------
    def Thread_Conncent(self, event):
        # 获取IP地址和端口号
        ip = self.widget['ip'].GetValue()
        port = self.widget['port'].GetValue()

        # 创建线程对象并启动线程
        if self.thread["tool"] is None:
            self.thread["tool"] = ToolThread(self, SudongEntity, ip, port)
            self.thread["tool"].start()

    # ------------------------------
    # 中断线程并清除线程在本地的引用
    # ------------------------------
    def Thread_Disconncent(self, event):
        self.Thread_Disconncent_network()

    def Thread_Disconncent_network(self):
        if self.thread["tool"] is not None:
            self.thread["tool"].stop()
            self.thread["tool"] = None

    # ------------------------------
    # M32-线程/=写入PSET
    # ------------------------------
    def Thread_Write_Pset(self, event):
        if self.thread["tool"] is not None:
            entity_temp = self.thread["tool"].entity

            self.thread["tool"].command([
                Command(command_type = CommandTypeEnum.OPERATION,
                        operation = OperationEnum.SWITCH_PSET,
                        extra = entity_temp.get_command_extra(entity_temp.SWITCH_PSET, str(int(self.widget['pset'].GetValue())).zfill(2)),
                        command = entity_temp.get_command_by_code(OperationEnum.SWITCH_PSET)),
            ])

    # ------------------------------
    # M33-线程/=disable tool
    # ------------------------------
    def Thread_Disable_Tool(self, event):
        if self.thread["tool"] is not None:
            self.thread["tool"].command([
                Command(command_type = CommandTypeEnum.OPERATION,
                        operation = OperationEnum.LOCK_DEVICE,
                        command = self.thread["tool"].entity.get_command_by_code(OperationEnum.LOCK_DEVICE)),
            ])

    # ------------------------------
    # M34-线程/=enable tool
    # ------------------------------
    def Thread_Enable_Tool(self, event):
        if self.thread["tool"] is not None:
            self.thread["tool"].command([
                Command(command_type = CommandTypeEnum.OPERATION,
                        operation = OperationEnum.UNLOCK_DEVICE,
                        command = self.thread["tool"].entity.get_command_by_code(OperationEnum.UNLOCK_DEVICE)),
            ])

    # ------------------------------
    # M35-线程/=写入条码
    # ------------------------------
    def Thread_Write_Identify(self, event):
        if self.thread["tool"] is not None:
            entity_temp = self.thread["tool"].entity

            self.thread["tool"].command([
                Command(command_type = CommandTypeEnum.OPERATION,
                        operation = OperationEnum.WRITE_CODE,
                        extra = entity_temp.get_command_extra(entity_temp.WRITE_IDENTIFY, 'Virtual Station 2', self.widget['identify'].GetValue()),
                        command = entity_temp.get_command_by_code(OperationEnum.WRITE_CODE)),
            ])

    # ------------------------------
    # M36-线程/=线程反馈
    # ------------------------------
    def Read_SuDong_Return(self, event):

        # --------------------
        # 01-初始化/=网络
        # --------------------
        ip = event[0][0]
        net = event[0][1]

        # --------------------
        # 02-初始化/=值
        # --------------------
        marks = event[1][0]
        value = event[1][1]

        # --------------------
        # 10-网络断开
        # --------------------
        if marks == 'log' and value[9:16] == 'exitoff':
            self.Thread_Disconncent_network()
        else:
            print(marks, value)
            print('-------------')

        # elif marks == 'tightening':
        # self.thread["tool"].command([['0042','']])

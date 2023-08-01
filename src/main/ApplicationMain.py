import wx
import win32api as win32
from wx import Object

import src.main.configs as configs
from src.main.views.MainFrame import MainFrame


class MainApp(wx.App):
    def __init__(self, *args, **kws):
        wx.App.__init__(self, *args, **kws)
        self.frame = None

    def OnInit(self):
        # 1. 程序唯一性检测
        if self.Check_program_is_duplicated():
            return False

        # 2. 初始化系统参数
        variables = {
            "license_data": self.Analyse_license(),         # 解析许可证
        }
        # 初始化保存在磁盘中的系统参数
        self.Initialize_system_config()

        # 3. 开始画界面
        self.frame = MainFrame(parent = None, id = wx.ID_ANY, variables = variables)

        # 设置顶端窗体
        self.SetTopWindow(self.frame)

        # 默认显示在屏幕中间
        self.frame.Center()

        # 显示主窗体
        self.frame.Show()
        return True


    # 检查程序是否重复启动
    def Check_program_is_duplicated(self):

        # import os
        # import sys
        #
        # import psutil
        # import tkinter
        #
        # from tkinter import messagebox
        # from framework.base.BaseConfig import BaseConfig
        # from framework.views.LoginView import LoginView
        #
        # if __name__ == '__main__':
        #     pids = psutil.pids()  # 获取所有进程PID
        #     list = []  # 空列表用来存储PID名称
        #     for pid in pids:  # 遍历所有PID进程
        #         p = psutil.Process(pid)  # 得到每个PID进程信息
        #         list.append(p.name())  # 将PID名称放入列表
        #         s = str(p.name())  # 将PID名称转换成字符串进行判断
        #         if s == "Program.exe":  # “123.exe”你要防多开进程的名称
        #             print(s + "当前程序已经被打开")
        #             pidd = os.getpid()  # 获取当前PID名称
        #             # root = tkinter.Tk().withdraw()
        #             # messagebox.showwarning(title='提示', message='当前程序已经被打开')
        #             # root.mainloop()
        #             sys.exit()
        #             # cmd = 'taskkill /pid ' + "pidd" + ' /f'  # 输入关闭名称命令
        #
        return False


    # 解析许可证内容并返回配置信息
    def Analyse_license(self):

        # 实际上应该从许可证文件内容中解析后返回给main app，现在先手写
        return {
            "MAIN_MENU_LIST": [
                # "00001",
                "00002",
                "00003",
                "00004",
                "00005",
                "00006",
                "00007",
                "00000",
            ]
        }


    # 初始化系统参数
    def Initialize_system_config(self):
        # 从存储在磁盘中的系统参数文件中读取数据，然后修改软件默认的系统参数
        pass


if __name__ == '__main__':
    MainApp().MainLoop()
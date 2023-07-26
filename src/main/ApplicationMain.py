import wx
import win32api as win32
from wx import Object

from src.main.configs.SystemConfigs import *
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
            "sys_config": self.Initialize_system_config(),  # 初始化系统配置
        }

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

        # 实际上应该从配置文件内容中解析后返回给main app，现在先手写
        return {
            # 主窗体初始大小
            "SIZE_MAIN_FRAME_DEFAULT": SIZE_MAIN_FRAME_DEFAULT,
            # 主窗体最小尺寸
            "SIZE_MAIN_FRAME_MINIMUM": SIZE_MAIN_FRAME_MINIMUM,

            # 所有颜色的配置
            "COLOR_SYSTEM_BACKGROUND": COLOR_SYSTEM_BACKGROUND,                 # 系统背景颜色
            "COLOR_MENU_BACKGROUND": COLOR_MENU_BACKGROUND,                     # 菜单栏的背景颜色
            "COLOR_MENU_BUTTON_BACKGROUND": COLOR_MENU_BUTTON_BACKGROUND,       # 菜单按钮的背景颜色
            "COLOR_MENU_BUTTON_TOGGLE": COLOR_MENU_BUTTON_TOGGLE,               # 菜单按钮触发后的颜色
            "COLOR_CONTENT_PANEL_BACKGROUND": COLOR_CONTENT_PANEL_BACKGROUND,   # 内容主体界面的背景颜色
            "COLOR_TEXT_THEME": COLOR_TEXT_THEME,                               # 文本颜色_主题色

            "COLOR_BUTTON_TEXT": COLOR_BUTTON_TEXT,                             # 默认参数 - 颜色 - 按钮文本颜色
            "COLOR_BUTTON_BACKGROUND": COLOR_BUTTON_BACKGROUND,                 # 默认参数 - 颜色 - 按钮背景色
            "COLOR_BUTTON_CLICKED": COLOR_BUTTON_CLICKED,                       # 默认参数 - 颜色 - 按钮按下的颜色
        }


if __name__ == '__main__':
    MainApp().MainLoop()
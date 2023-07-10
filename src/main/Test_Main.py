import wx

from win32api import GetSystemMetrics
from src.main.views.Test_Frame import MainProgram


# ******************************
# 主循环
# ******************************
if __name__ == '__main__':
    app_run = wx.App()
    a = [int(GetSystemMetrics(0) * 0.8), int(GetSystemMetrics(1) * 0.8)]
    b = tuple(a)
    system_run = MainProgram(parent = None,
                             id = -1,
                             title = u'read tool thread',
                             frame_size = (800, 600),
                             )
    system_run.Show(True)
    app_run.MainLoop()

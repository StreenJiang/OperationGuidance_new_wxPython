import wx

from src.main import widgets, configs
from src.main.configs import SystemConfigs
from src.main.views.Content_Workplace import WorkplaceView


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, pos = wx.DefaultPosition, size = (800, 600))
        self.SetMinSize((400, 300))

        # 主窗口panel
        self.main_panel = wx.Panel(self, wx.ID_ANY, pos = (0, 0), size = self.GetClientSize())
        self.main_panel.SetBackgroundColour(wx.WHITE)

        self.p = panel(self.main_panel)

        self.Bind(wx.EVT_SIZE, self.main_frame_on_size)


    # 主窗口大小变化时，所有界面元素都需要调整
    def main_frame_on_size(self, event):
        print("resize")
        self.main_panel.SetSize(self.GetClientSize())
        # self.p.SetSize(self.GetClientSize())





class panel(wx.Panel):
    def __init__(self, parent, size = wx.DefaultSize):
        wx.Panel.__init__(self, parent, -1, size = size)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        print("on_size")

    def on_paint(self, event):
        print("on_paint")



if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame().Show()
    app.MainLoop()
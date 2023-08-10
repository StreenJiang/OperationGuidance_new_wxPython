import wx

from src.main.views.Content_Workplace import WorkplaceView


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, pos = wx.DefaultPosition, size = (800, 600))
        self.SetMinSize((400, 300))

        test = WorkplaceView(self, -1, pos = (0, 0), size = self.GetClientSize(), title = "尼玛")


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame().Show()
    app.MainLoop()
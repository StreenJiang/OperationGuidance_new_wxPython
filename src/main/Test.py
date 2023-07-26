import wx

from src.main.widgets import CustomRadiusButton

if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None, -1, size = (800, 600))
    panel = wx.Panel(frame, -1)
    btn = CustomRadiusButton(panel, -1, "TEST", "#FEFEFE", "#E86C10", "#8D3C00", 3, size = (100, 50), pos = (50, 50))
    frame.Center()
    frame.Show()
    app.MainLoop()


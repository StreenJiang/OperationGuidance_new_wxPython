import sys

import wx


# 测试API方法，这个方法就是前后端的桥梁，前端配置好API，后端在API里调用后端写好的事件处理方法
def API_EVT_BUTTON_TEST(event) -> None:
    event_obj = event.GetEventObject()
    print("test api [API_EVT_BUTTON_TEST], button label: %s" % event_obj.GetLabel())

    # 这里调用后端设定好的事件处理方法
    # TODO

    # 将前端后续处理需要的参数塞入（每个方法都不一样，因此使用字典）
    event_obj.call_back_variables = {}

    # 调用Skip
    event.Skip()


# exit confirmation
def exit_confirmation(event) -> None:
    event_obj = event.GetEventObject()
    dlg = wx.MessageDialog(event_obj, "确定要退出吗？", 'Updater', wx.YES_NO)
    dlg.SetTitle("退出程序")
    result = dlg.ShowModal()
    if result == wx.ID_YES:
        sys.exit()


def API_EVT_MOUSE_EVENTS_TEST(event):
    event_obj = event.GetEventObject()
    print("test api [API_EVT_MOUSE_EVENTS_TEST], button label: %s" % event_obj.GetLabel())




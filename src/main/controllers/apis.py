

# 测试API方法，这个方法就是前后端的桥梁，前端配置好API，后端在API里调用后端写好的事件处理方法
def API_EVT_BUTTON_TEST(obj, event):
    print("test api [API_EVT_BUTTON_TEST], button label: %s" % event.GetEventObject().GetLabel())

    # 这里调用后端设定好的事件处理方法
    # TODO

    # 将前端后续处理需要的参数塞入（每个方法都不一样，因此使用字典）
    obj.call_back_variables = {}

    # 调用Skip
    event.Skip()


def API_EVT_MOUSE_EVENTS_TEST(obj, event):
    print("test api [API_EVT_MOUSE_EVENTS_TEST], button label: %s" % event.GetEventObject().GetLabel())


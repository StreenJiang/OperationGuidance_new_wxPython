# 通用的api调用接口
def call_api(obj, event_obj, event):
    try:
        events_temp = event_obj.events
    except AttributeError:
        return

    event_type = event.GetEventType()
    for event_binder in events_temp.keys():
        if event_type == event_binder._getEvtType():
            for event_each in events_temp[event_binder]:
                # 调用事件方法
                if event_each["api"] is not None:
                    event_each["api"](obj, event)
                # 事件处理后如果有返回值塞到self里面，则可以继续处理（比如数据展示、修改UI界面等）
                if event_each["call_back"] is not None:
                    event_each["call_back"](event_obj)
            break



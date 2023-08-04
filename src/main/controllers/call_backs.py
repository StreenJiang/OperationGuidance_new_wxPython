

# 测试CALL BACK方法，这个方法就是调用后端事件且处理完以后，前段需要再次处理前端相关逻辑时调用的处理方法
def CALL_BACK_TEST(event):
    event_obj = event.GetEventObject()
    print("test call back")

    # 这是从后端返回的call back调用需要用到的参数
    variables = event_obj.call_back_variables


# 工作台：展示所有产品任务
def CALL_BACK_SHOW_PRODUCT_MISSIONS(event):
    event_obj = event.GetEventObject()
    print("workplace call back: CALL_BACK_SHOW_PRODUCT_MISSIONS[menu_obj:%s]" % event_obj)

    # 这是从后端返回的call back调用需要用到的参数
    # variables = event_obj.call_back_variables

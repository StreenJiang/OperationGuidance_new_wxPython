import sys

import wx
from PIL import Image

import src.main.models.ProductMission as productMission
import src.main.models.Device as dvs


# 测试API方法，这个方法就是前后端的桥梁，前端配置好API，后端在API里调用后端写好的事件处理方法
def API_EVT_BUTTON_TEST(event):
    event_obj = event.GetEventObject()
    print("test api [API_EVT_BUTTON_TEST], button label: %s" % event_obj.GetLabel())

    # 这里调用后端设定好的事件处理方法
    # TODO

    # 将前端后续处理需要的参数塞入（每个方法都不一样，因此使用字典）
    event_obj.call_back_variables = {}

    # 调用Skip
    event.Skip()


# exit confirmation
def exit_confirmation(event):
    event_obj = event.GetEventObject()
    dlg = wx.MessageDialog(event_obj, "确定要退出吗？", 'Updater', wx.YES_NO)
    dlg.SetTitle("退出程序")
    result = dlg.ShowModal()
    if result == wx.ID_YES:
        sys.exit()


def API_EVT_MOUSE_EVENTS_TEST(event):
    event_obj = event.GetEventObject()
    print("test api [API_EVT_MOUSE_EVENTS_TEST], button label: %s" % event_obj.GetLabel())


# 工作台：获取任务（产品）列表
def API_GET_PRODUCT_MISSIONS(obj):
    # TODO: get missions data from back-end api(s)
    # 这里先暂时手写，之后要调用后端api，让后端返回
    return [
        productMission.ProductMission(
            id = 1, 
            mission_name = "OP-10机盖装配", 
            mission_pn_code = "12345678",
            mission_status = 1, 
            creator = "创建人", 
            last_updater = "创建人",
            mission_product_sides = [
                productMission.ProductSides(
                    id = 1, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                productMission.ProductSides(
                    id = 2, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        productMission.ProductMission(
            id = 2, 
            mission_name = "任务名称2", 
            mission_pn_code = "555555",
            mission_status = 1, 
            creator = "创建人", 
            last_updater = "创建人",
            mission_product_sides = [
                productMission.ProductSides(
                    id = 1, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                productMission.ProductSides(
                    id = 2, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        productMission.ProductMission(
            id = 3, 
            mission_name = "任务名称3", 
            mission_pn_code = "555555",
            mission_status = 1, 
            creator = "创建人", 
            last_updater = "创建人",
            mission_product_sides = [
                productMission.ProductSides(
                    id = 1, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                productMission.ProductSides(
                    id = 2, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        productMission.ProductMission(
            id = 3, 
            mission_name = "任务名称4", 
            mission_pn_code = "555555",
            mission_status = 1, 
            creator = "创建人", 
            last_updater = "创建人",
            mission_product_sides = [
                productMission.ProductSides(
                    id = 1, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                productMission.ProductSides(
                    id = 2, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        productMission.ProductMission(
            id = 3, 
            mission_name = "任务名称5", 
            mission_pn_code = "555555",
            mission_status = 1, 
            creator = "创建人", 
            last_updater = "创建人",
            mission_product_sides = [
                productMission.ProductSides(
                    id = 1, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                productMission.ProductSides(
                    id = 2, 
                    side_name = "产品正面", 
                    side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
                    creator = "创建人", 
                    last_updater = "创建人",
                    bolts = [
                        productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                        productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
    ]


# 工作台：获取设备列表
def API_GET_DEVICES(obj):
    # TODO: get devices from back-end api(s)
    return [
        dvs.Device(
            id = 1,
            device_name = "设备名称111",
            device_category = dvs.DEVICE_CATEGORY_TOOL,
            device_type = dvs.DEVICE_TYPE_TOOL_PF4000,
            device_ip = "192.168.1.1",
            device_port = 4040,
            device_status = dvs.DEVICE_STATUS_CONNECTED,
            creator = "创建人", 
            last_updater = "创建人"
        ),
        dvs.Device(
            id = 2,
            device_name = "设备名称222222",
            device_category = dvs.DEVICE_CATEGORY_ARM,
            device_type = dvs.DEVICE_TYPE_ARM_CF01,
            device_ip = "192.168.1.2",
            device_port = 4041,
            device_status = dvs.DEVICE_STATUS_DISCONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
        dvs.Device(
            id = 3,
            device_name = "设备名称3333333",
            device_category = dvs.DEVICE_CATEGORY_ARM,
            device_type = dvs.DEVICE_TYPE_ARM_CF01,
            device_ip = "192.168.1.2",
            device_port = 4042,
            device_status = dvs.DEVICE_STATUS_CONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
        dvs.Device(
            id = 4,
            device_name = "设备名称44444444",
            device_category = dvs.DEVICE_CATEGORY_ARM,
            device_type = dvs.DEVICE_TYPE_ARM_CF01,
            device_ip = "192.168.1.2",
            device_port = 4043,
            device_status = dvs.DEVICE_STATUS_CONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
    ]

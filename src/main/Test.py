import time

import wx
import wx.lib.agw.shapedbutton as sb

from src.main.utils import CacheUtil

if __name__ == '__main__':
    app = wx.App()
    # frame = wx.Frame(None, -1, size = (800, 600))
    # panel = wx.Panel(frame, -1)
    # btn = CustomRadiusButton(panel, -1, "TEST", "#FEFEFE", "#E86C10", "#D05900", 75, 3,
    #                          button_type = BUTTON_TYPE_SWITCH, size = (100, 50), pos = (50, 50))
    # frame.Center()
    # frame.Show()
    # app.MainLoop()

    # class test(ToolBaseEntity):
    #
    #     def initialize_commands(self):
    #         pass
    #
    #     def initialize_variables(self, ip, port):
    #         pass
    #
    #     def get_command_extra(self, extra_type, *arg):
    #         pass
    #
    #
    # t = test()
    # t.variables = "aaaaa"
    #
    # print(t.variables)

    # from typing import TypeVar, Generic
    #
    # T = TypeVar("T")
    # print(T)
    #
    #
    # class Test(Generic[T]):
    #     def __init__(self) -> None:
    #         self.param = None
    #
    #     def test(self) -> T:
    #         return self.param
    #
    #     def set(self, param: T):
    #         print(T.__doc__)
    #         print(type(param))
    #         self.param = param
    #
    # t = Test[int]()
    # t.set("1111")
    #
    # print(t.test())

    # class List(list):
    #     pass
    #
    # l = List()
    # l.append("sssss")
    # l[2] = "asdfasdf"
    #
    # print(l)

    # T = TypeVar("T", bound = ProductMission)
    #
    # class ProductMissionSides(list, Generic[T]):
    #     def __init__(self, *args, **kws):
    #         list.__init__(self, *args, **kws)
    #
    #     def append(self, element: T):
    #         if not isinstance(element, T.__bound__):
    #             raise Exception("ERROR!!!!!!!!")
    #         else:
    #             super().append(element)
    #
    # pms = ProductMissionSides[ProductMission]()
    # # pms.append("asdfsadfsdf")
    # pms.append(ProductMission(1, 1, 1, 1, 1, 1, 1))
    # print(pms)

    # clist = CustomList[ProductMission.ProductSides](ProductMission)
    # print(clist)
    #
    # # clist.append("asdfsadfsdf")
    # clist.append(ProductMission(1, 1, 1, 1, ProductMission.ProductSides(1, 1, 1, 1, 1, 1), 1, 1))
    # clist.append(ProductMission(1, 1, 1, 1, 1, 1, 1))
    # clist.append(ProductMission(1, 1, 1, 1, 1, 1, 1))
    # clist.append(ProductMission(1, 1, 1, 1, 1, 1, 1))
    # print(clist)
    #
    # clist.insert(3, 1)
    # print(clist)

    from PIL import Image

    # img = Image.open("产品图片样图 (1).jpg")
    # print(type(img))
    # img_array = np.asarray(img)
    # print(img_array)
    # bitMap = CommonUtils.PILImageToWxBitmap(img)
    # print("type(bitMap): ", type(bitMap))
    # wxImage = CommonUtils.PILImageToWxImage(img)
    # print("type(wxImage): ", type(wxImage))
    # pilImage = CommonUtils.WxBitmapToPILImage(bitMap)
    # print("type(pilImage): ", type(pilImage))

    # wxImage = CommonUtils.PILImageToWxImage(img)
    # print(wxImage)
    # wxBitmap = CommonUtils.PILImageToWxBitmap(img)
    # print(wxBitmap)
    #
    # pilImage = CommonUtils.WxImageToPILImage(wxImage)
    # print(pilImage)
    # pilImage = CommonUtils.WxBitmapToPILImage(wxBitmap)
    # print(pilImage)


    #
    # file = open("test.pkl", "a+b")
    # pm = productMission.ProductMission(
    #             id = 1, mission_name = "OP-10机盖装配", mission_pn_code = "12345678",
    #             mission_status = 1, creator = "创建人", last_updater = "最后修改人",
    #             mission_product_sides = [
    #                 productMission.ProductSides(
    #                     id = 1, side_name = "产品正面", side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
    #                     creator = "创建人", last_updater = "最后修改人",
    #                     bolts = [
    #                         productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "最后修改人"),
    #                         productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "最后修改人"),
    #                     ]
    #                 ),
    #                 productMission.ProductSides(
    #                     id = 2, side_name = "产品正面", side_image = productMission.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (0, 0), "me", "me"),
    #                     creator = "创建人", last_updater = "最后修改人",
    #                     bolts = [
    #                         productMission.ProductBolts(1, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "最后修改人"),
    #                         productMission.ProductBolts(2, "1号螺栓", (20, 50), 0, creator = "创建人", last_updater = "最后修改人"),
    #                     ]
    #                 )
    #             ]
    #         )
    # pickle.dump(pm, file, protocol = pickle.HIGHEST_PROTOCOL)
    # file.close()

    # with open("test.pkl", "a+b") as file:
    #     pm = ProductMission(2, "测试", "123124", 1, [], "me", "me")
    #     pickle.dump(pm, file, protocol = pickle.HIGHEST_PROTOCOL)

    # with open("test.pkl", "rb") as file:
    #     obj = pickle.load(file)
    #     print(obj)
    #     print(type(obj))
    #     print(obj.GetMissionName())
    #     print("obj.GetMissionProductSides(): ", obj.GetMissionProductSides())
    #     print(obj.GetMissionProductSides()[0].GetSideImage().GetImageOriginal())

    # with open("产品图片样图 (1).jpg", "a+b") as file:
    #     img_array = np.array(file)
    #     for pixel in range(img_array.size):
    #         print(pixel)
    #     pm = ProductMission(2, "测试", "123124", 1, [], "me", "me")
    #     pickle.dump(pm, file, protocol = pickle.HIGHEST_PROTOCOL)


    # ProductMission(1, 1, 1, 1, [ProductSides(1, 1, 1, [ProductSides(1, 1, (20, 40), 1, 1, 1)], 1, 1)], 1, 1)
    # ProductMission(1, 1, 1, 1, ProductSides(1, 1, 1, 1, 1, 1), 1, 1)

    # print(math.ceil(7 / 4))
    # print(5 % 4)
    # print(math.floor(4 / 4))

    # app = wx.App()
    # frame = wx.Frame(None, -1, size = (800, 600))
    #
    # customPanel = CustomBorderPanel(frame, -1, pos = (30, 50), size = (300, 200))
    # box_sizer = wx.BoxSizer(wx.HORIZONTAL)
    # frame.SetSizer(box_sizer)
    #
    # btn1 = wx.Button(customPanel, -1, label = "测试按钮")
    # btn1.SetSize(100, 50)
    # btn1.SetPosition((260, 20))
    # content_sizer = customPanel.GetSizer()
    # content_sizer.Add(btn1)
    #
    # frame.Center()
    # frame.Show()
    # app.MainLoop()

    # print(COLOR_BUTTON_FOCUSED)
    # COLOR_BUTTON_FOCUSED = "sadfasdf"
    # print(COLOR_BUTTON_FOCUSED)

    # print(isinstance(4.4, float))


    # CacheUtil.Set("test", 15, timeout = 8)
    #
    # time.sleep(10)
    #
    # data = CacheUtil.Get("test")
    # print(data)

    # grid_sizer = wx.GridSizer(cols = 5)


    # sb.SBitmapButton






















    pass

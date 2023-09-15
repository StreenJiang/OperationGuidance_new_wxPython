import threading

import wx
import math
from typing import List, Type

import configs, widgets
from controllers import DeviceService as deviceService
from models import Device as dvs, ProductMission as pdctmsn
from threads import Workplace_threads as wThread
from utils import CommonUtils, CacheUtil, ThreadPool
from enums.Cache import CacheEnum as cache

# 返回按钮的TEXT
BACK_BUTTON_TEXT        = "返回"
# 条码框的扫码icon图片存储路径
PATH_ICON_BAR_CODE      = "configs/icons/bar_code_icon.png"

# 产品界面的翻页按钮
PATH_ICON_BACKWARD_FAST = [
    "configs/icons/page_btn_backward-fast.png",
    "configs/icons/page_btn_backward-fast_hover.png",
    "configs/icons/page_btn_backward-fast_toggled.png"
]
PATH_ICON_BACKWARD      = [
    "configs/icons/page_btn_backward.png",
    "configs/icons/page_btn_backward_hover.png",
    "configs/icons/page_btn_backward_toggled.png"
]
PATH_ICON_FORWARD       = [
    "configs/icons/page_btn_forward.png",
    "configs/icons/page_btn_forward_hover.png",
    "configs/icons/page_btn_forward_toggled.png"
]
PATH_ICON_FORWARD_FAST  = [
    "configs/icons/page_btn_forward-fast.png",
    "configs/icons/page_btn_forward-fast_hover.png",
    "configs/icons/page_btn_forward-fast_toggled.png"
]


class WorkplaceView(wx.Panel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0,
                 name = "WorkplaceView", title = "WorkplaceView",
                 mission_obj: pdctmsn.ProductMission = None):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.Hide()
        self.top_parent = CommonUtils.GetTopParent(self)
        self.title = mission_obj.GetMissionName()
        self.mission_obj = mission_obj

        # 主要的两个panel，一个顶部菜单条panel、一个下面的内容主体panel
        self.top_menu_bar_panel = None
        self.content_panel = None
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # 菜单条里的组件
        self.back_button = None
        self.menu_text = None
        self.logo_img = None

        # 内容主体panel内的组件
        self.devices_panel = None
        self.bar_code_panel = None
        self.product_image_panel = None
        self.progress_status_panel = None
        self.progress_result_data_panel = None
        self.product_sides_panel = None

        # 线程集合，用来存整个界面需要运行的线程
        self.threads_arr = []

        # 左侧panel需要的参数
        self.devices = None
        self.devices_changed = False

        # 右侧中间panel需要的参数
        self.realtime_data_obj = pdctmsn.RealtimeData(
            mission_obj.GetID(), mission_obj.GetMissionIndexs()
        )

        self.bar_code_text_control = None
        self.product_image = None
        self.progress_status = None
        self.progress_result_data = None
        self.product_sides = None

        # 窗体拖拽标识
        self.mouse_pos = None
        self.window_drag_flag = False

        # 顶部菜单条组件
        self.top_menu_bar_panel = TopMenuBarPanel(parent = self)
        self.sizer.Add(self.top_menu_bar_panel)
        # 绑定事件
        self.bind_dragging_event(self.top_menu_bar_panel)
        # 配置顶部菜单条
        self.set_up_top_menu_bar_panel()

        # 内容panel
        self.content_panel = ContentPanel(parent = self)
        self.sizer.Add(self.content_panel)
        # 配置内容panel
        self.set_up_content_panel()

        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.top_parent.Bind(wx.EVT_SIZE, self.main_frame_resizing)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_SHOW, self.on_show)

        # 刷新布局
        self.Layout()
        self.Show()

    def set_up_top_menu_bar_panel(self):
        # 添加返回按钮
        self.back_button = self.top_menu_bar_panel.add_back_button()
        # 绑定事件
        self.back_button.Bind(wx.EVT_LEFT_UP, self.back_button_toggled)

        # 添加标题
        self.menu_text = self.top_menu_bar_panel.add_menu_title(self.title)
        # 绑定事件
        self.bind_dragging_event(self.menu_text)

        # 添加logo图片
        self.top_menu_bar_panel.set_logo(wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY).ConvertToBitmap())

    def set_up_content_panel(self):
        # 添加设备panel
        self.devices_panel = self.content_panel.add_left()
        self.devices_panel.set_devices(self.get_devices())

        # 添加扫码组件panel
        self.bar_code_panel = self.content_panel.add_middle_top()

        # 添加产品图片panel
        self.product_image_panel = self.content_panel.add_middle_bottom(self.mission_obj)

        # 添加工作状态动态显示panel
        self.progress_status_panel = self.content_panel.add_right_top(self.mission_obj)

        # 添加实时数据显示panel
        self.progress_result_data_panel = self.content_panel.add_right_center(self.realtime_data_obj)

        # 添加产品面显示panel
        self.product_sides_panel = self.content_panel.add_right_bottom(self.mission_obj)

    # 获取缓存数据 - 设备列表
    def get_devices(self) -> List[dvs.Device]:
        # 初始化“数据是否有变化”变量
        self.devices_changed = False

        # 从缓存中读取数据
        devices = CacheUtil.Get(cache.DEVICES.value["key"])

        # 如果缓存中的数据为空，则重新调用API查询数据
        if devices is None:
            # 调用后端API获取数据
            devices = deviceService.get_devices(self)
            # 将数据存入缓存
            CacheUtil.Set(cache.DEVICES.value["key"], devices, timeout = cache.DEVICES.value["timeout"])

        # 如果处理后返回的数据还是空，则需要返回一个空数组，方便判断
        if devices is None:
            devices = []

        # 判断数据是否有变化
        if self.devices is None or len(devices) != len(self.devices):
            self.devices_changed = True
        else:
            for index in range(len(devices)):
                if devices[index] is not self.devices[index]:
                    self.devices_changed = True

        # 将数据存到对象中
        self.devices = devices
        return devices

    # 检查缓存数据（设备列表）是否过期
    def data_has_expired(self):
        return CacheUtil.HasExpired(cache.DEVICES.value["key"])

    # 返回按钮点击事件
    def back_button_toggled(self, event):
        self.Show(False)
        self.top_parent.show_all(True)
        event.Skip()

    # 主窗口大小变化时，所有界面元素都需要调整
    def main_frame_resizing(self, event):
        # wx.CallLater(100, self.resize_after)
        if not self.is_resizing:
            self.is_resizing = True
            top_size = self.top_parent.GetClientSize()
            print("workplace -> Resizing frame, Resolution: ", top_size)
            if top_size == (0, 0):
                return
            self.SetSize(top_size)
            self.is_resizing = False
        event.Skip()

    def resize_after(self):
        top_size = self.top_parent.GetClientSize()
        print("workplace -> Resizing frame, Resolution: ", top_size)
        if top_size == (0, 0):
            return
        self.SetSize(top_size)
        self.is_resizing = False

    def on_size(self, event):
        event.Skip()

    def on_show(self, event):
        if event.IsShown():
            for thread_each in self.threads_arr:
                thread_class: Type[threading.Thread] = thread_each["class"]
                args = thread_each["args"]
                kws = thread_each["kws"]
                t = thread_each["obj"]
                if t is None or not t.is_alive():
                    t = thread_class(*args, **kws)
                    t.start()
                    thread_each["obj"] = t
                # if t is None:
                #     t = thread_class(*args, **kws)
                #     # future = ThreadPool.submit(t)
                #     future = ThreadPool.submit(thread_class, *args, **kws)
                #     print("future.running(): ", future.running())
                #     thread_each["obj"] = t
        else:
            for thread_each in self.threads_arr:
                t = thread_each["obj"]
                if t is not None and t.is_alive():
                    t.stop()

        event.Skip()

    # 向thread_arr中添加线程
    def register_thread(self, thread_class: threading.Thread, *args, **kws):
        thread_dict = {
            "class": thread_class,
            "args": args,
            "kws": kws,
            "obj": None
        }
        self.threads_arr.append(thread_dict)

    # 设置实时数据对象（realtime_data）
    def set_realtime_data_obj(self, realtime_data_obj):
        self.realtime_data_obj = realtime_data_obj

    # 窗体拖拽事件 - 重新定位窗体位置
    def window_dragging(self, event):
        if not self.top_parent.IsMaximized() and self.mouse_pos is not None:
            if event.Dragging():
                pos_changed = event.GetPosition() - self.mouse_pos
                # 判断拖动距离是否大于一定距离，如果太小则可能是点击事件，因此不重新定位，使按钮点击事件能正常触发
                if (abs(pos_changed[0]), abs(pos_changed[1])) > (2, 2):
                    self.window_drag_flag = True
                    self.top_parent.SetPosition(self.top_parent.GetPosition() + pos_changed)
        event.Skip()

    # 窗体拖拽事件 - 鼠标左键按下
    def window_dragging_mouse_l_down(self, event):
        if not self.top_parent.IsMaximized():
            self.mouse_pos = event.GetPosition()
        event.Skip()

    # 窗体拖拽事件 - 鼠标左键松开
    def window_dragging_mouse_l_up(self, event):
        if not self.top_parent.IsMaximized():
            self.mouse_pos = None
        event.Skip()

    # 给组件绑定所有窗体拖拽事件
    def bind_dragging_event(self, widget_obj):
        widget_obj.Bind(wx.EVT_MOTION, self.window_dragging)
        widget_obj.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
        widget_obj.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)

    # 计算顶部菜单条的大小和位置
    def calc_menu_bar(self):
        width, height = self.GetSize()
        bar_w = width
        bar_h = math.ceil(height * 0.05)
        return (bar_w, bar_h), (0, 0)

    # 计算下方内容panel的大小和位置
    def calc_content_panel(self):
        width, height = self.GetSize()
        bar_h = math.ceil(height * 0.05)
        pan_w = width
        pan_h = height - bar_h
        return (pan_w, pan_h), (0, bar_h)


# 顶部菜单条panel
class TopMenuBarPanel(wx.Panel):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "TopMenuBarPanel"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size, style = style, name = name)
        self.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
        self.back_button = None
        self.menu_title = None
        self.logo_bitmap = None
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        # 计算自身size和pos
        size, pos = self.calc_self()
        self.SetSize(size)

        # 重设返回按钮的size和pos
        b_size, b_pos = self.calc_back_button()
        self.back_button.SetSize(b_size)
        self.back_button.SetPosition(b_pos)

        # 重设字体size和pos
        t_pos = self.calc_menu_title()
        self.menu_title.SetPosition(t_pos)

        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))

        # 重设logo的size和pos
        if self.logo_bitmap is not None:
            image = self.logo_bitmap.ConvertToImage()
            # 计算logo的size和pos
            i_size, i_pos = self.calc_logo(image.GetSize())
            # 重新设置图片的尺寸
            image.Rescale(i_size[0], i_size[1], wx.IMAGE_QUALITY_BILINEAR)
            # 重新绘制bitmap
            bitmap = wx.Bitmap(image)
            dc.DrawBitmap(bitmap, i_pos, bitmap.GetMask() is not None)

        # 删除DC
        del dc

    def add_back_button(self):
        self.back_button = widgets.CustomRadiusButton(self, wx.ID_ANY,
                                                      label = BACK_BUTTON_TEXT,
                                                      font_color = configs.COLOR_BUTTON_TEXT,
                                                      background_color = configs.COLOR_BUTTON_BACKGROUND,
                                                      clicked_color = configs.COLOR_BUTTON_FOCUSED,
                                                      button_size_type = widgets.BUTTON_SIZE_TYPE_NORMAL,
                                                      radius = 2)
        return self.back_button

    def add_menu_title(self, title):
        self.menu_title = wx.StaticText(self, wx.ID_ANY,
                                        label = title,
                                        style = wx.ALIGN_CENTRE_HORIZONTAL)
        self.menu_title.SetForegroundColour(configs.COLOR_TEXT_MAIN_MENU)
        return self.menu_title

    def set_logo(self, bitmap):
        self.logo_bitmap = bitmap

    def calc_self(self):
        p_w, p_h = self.GetParent().GetSize()
        return (p_w, math.ceil(0.05 * p_h)), (0, 0)

    def calc_back_button(self):
        w, h = self.GetSize()
        b_h = math.ceil(0.8 * h)
        b_w = b_h * 2.5
        b_x = b_y = math.ceil((h - b_h) / 2)
        return (b_w, b_h), (b_x, b_y)

    def calc_menu_title(self):
        w, h = self.GetSize()

        # 计算font
        size_1 = math.ceil(w / 70) + 2
        size_2 = math.ceil(h / 2 + 0.4)
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        if w < h:
            font_temp.SetPointSize(size_1)
        else:
            font_temp.SetPointSize(size_2)
        self.menu_title.SetFont(font_temp)

        # 计算pos
        tw, th = self.menu_title.GetTextExtent(self.menu_title.GetLabel())
        return math.ceil((w - tw) / 2), math.floor((h - th) / 2) - h / 20

    def calc_logo(self, image_size):
        w, h = self.GetSize()
        i_w, i_h = image_size
        i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), h * 0.7 / i_h)
        return (i_w, i_h), (w - i_w - math.ceil(w / 300), math.ceil((h - i_h) / 2))


# 下方内容的外层panel
class ContentPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        # 设备panel
        self.panel_left = None
        # 条码框panel
        self.panel_middle_top = None
        # 产品图片panel
        self.panel_middle_bottom = None
        # 工作状态panel
        self.panel_right_top = None
        # 工作数据panel
        self.panel_right_center = None
        # 产品面panel
        self.panel_right_bottom = None
        # 每个panel之间的间隙
        self.gap = 0
        self.is_resizing = False

    def on_size(self, event):
        if not self.is_resizing:
            self.is_resizing = True

            # 计算自身size和pos
            size, pos = self.calc_self()
            self.SetSize(size)
            self.SetPosition(pos)

            # 计算间隙
            self.gap = math.ceil(self.GetParent().GetSize()[0] / 300) + 3
            self.SetMargin(self.gap)
            w, h = size

            # 重设左侧设备panel
            left_size, left_pos = self.calc_left(w, h)
            self.panel_left.SetSize(left_size)
            self.panel_left.SetPosition(left_pos)

            # 重设中间上方扫码panel
            middle_top_size, middle_top_pos = self.calc_middle_top(w, h)
            self.panel_middle_top.SetSize(middle_top_size)
            self.panel_middle_top.SetPosition(middle_top_pos)

            # 重设中间下方产品图片、工作流程panel
            middle_bottom_size, middle_bottom_pos = self.calc_middle_bottom(w, h)
            self.panel_middle_bottom.SetSize(middle_bottom_size)
            self.panel_middle_bottom.SetPosition(middle_bottom_pos)

            # 重设右侧上方工作状态panel
            right_top_size, right_top_pos = self.calc_right_top(w, h)
            self.panel_right_top.SetSize(right_top_size)
            self.panel_right_top.SetPosition(right_top_pos)

            # 重设右侧中间产品数据展示panel
            right_center_size, right_center_pos = self.calc_right_center(w, h)
            self.panel_right_center.SetSize(right_center_size)
            self.panel_right_center.SetPosition(right_center_pos)

            # 重设右侧下方产品面panel
            right_bottom_size, right_bottom_pos = self.calc_right_bottom(w, h)
            self.panel_right_bottom.SetSize(right_bottom_size)
            self.panel_right_bottom.SetPosition(right_bottom_pos)

            super().on_size(event)
            self.is_resizing = False

    def add_left(self):
        self.panel_left = LeftPanel(parent = self)
        return self.panel_left

    def add_middle_top(self):
        self.panel_middle_top = MiddleTopPanel(parent = self)
        self.panel_middle_top.set_icon(wx.Image(PATH_ICON_BAR_CODE, wx.BITMAP_TYPE_ANY).ConvertToBitmap())
        self.panel_middle_top.add_text_control()
        return self.panel_middle_top

    def add_middle_bottom(self, mission_obj: pdctmsn.ProductMission):
        self.panel_middle_bottom = MiddleBottomPanel(parent = self, mission_obj = mission_obj)
        return self.panel_middle_bottom

    def add_right_top(self, mission_obj: pdctmsn.ProductMission):
        self.panel_right_top = RightTopPanel(parent = self, mission_obj = mission_obj)
        return self.panel_right_top

    def add_right_center(self, realtime_data_obj: pdctmsn.RealtimeData):
        self.panel_right_center = RightCenterPanel(parent = self, realtime_data_obj = realtime_data_obj)
        return self.panel_right_center

    def add_right_bottom(self, mission_obj: pdctmsn.ProductMission):
        self.panel_right_bottom = RightBottomPanel(parent = self, mission_obj = mission_obj)
        return self.panel_right_bottom

    def calc_self(self):
        p_w, p_h = self.GetParent().GetSize()
        top_menu_bar_h = math.ceil(0.05 * p_h)
        new_h = p_h - top_menu_bar_h
        return (p_w, new_h), (0, top_menu_bar_h)

    def calc_left(self, w, h):
        left_w = math.ceil((w - self.gap * 6 - 2) * 0.045)
        left_h = h - self.gap * 4 - 2
        left_x = 0 + self.gap * 2 + 1
        left_y = 0 + self.gap * 2 + 1
        return (left_w, left_h), (left_x, left_y)

    def calc_middle_top(self, w, h):
        middle_top_w = math.ceil((w - self.gap * 6 - 2) * 0.755)
        middle_top_h = math.ceil((self.panel_left.GetSize()[1] - self.gap) * 0.065)
        middle_top_x = self.panel_left.GetPosition()[0] + self.panel_left.GetSize()[0] + self.gap
        middle_top_y = self.panel_left.GetPosition()[1]
        return (middle_top_w, middle_top_h), (middle_top_x, middle_top_y)

    def calc_middle_bottom(self, w, h):
        middle_top_w = self.panel_middle_top.GetSize()[0]
        middle_top_h = (self.panel_left.GetSize()[1] - self.gap) - self.panel_middle_top.GetSize()[1]
        middle_top_x = self.panel_middle_top.GetPosition()[0]
        middle_top_y = self.panel_middle_top.GetPosition()[1] + self.panel_middle_top.GetSize()[1] + self.gap
        return (middle_top_w, middle_top_h), (middle_top_x, middle_top_y)

    def calc_right_top(self, w, h):
        right_top_w = math.ceil(w - self.gap * 6 - 2) - self.panel_left.GetSize()[0] - self.panel_middle_top.GetSize()[0]
        right_top_h = math.ceil((self.panel_left.GetSize()[1] - self.gap * 2) * 0.4)
        right_top_x = self.panel_middle_top.GetPosition()[0] + self.panel_middle_top.GetSize()[0] + self.gap
        right_top_y = self.panel_left.GetPosition()[1]
        return (right_top_w, right_top_h), (right_top_x, right_top_y)

    def calc_right_center(self, w, h):
        right_center_w = self.panel_right_top.GetSize()[0]
        right_center_h = math.ceil((self.panel_left.GetSize()[1] - self.gap * 2) * 0.3)
        right_center_x = self.panel_right_top.GetPosition()[0]
        right_center_y = self.panel_right_top.GetPosition()[1] + self.panel_right_top.GetSize()[1] + self.gap
        return (right_center_w, right_center_h), (right_center_x, right_center_y)

    def calc_right_bottom(self, w, h):
        right_bottom_w = self.panel_right_top.GetSize()[0]
        right_bottom_h = (self.panel_left.GetSize()[1] - self.gap * 2) - self.panel_right_top.GetSize()[1] - self.panel_right_center.GetSize()[1]
        right_bottom_x = self.panel_right_top.GetPosition()[0]
        right_bottom_y = self.panel_right_center.GetPosition()[1] + self.panel_right_center.GetSize()[1] + self.gap
        return (right_bottom_w, right_bottom_h), (right_bottom_x, right_bottom_y)


# 左侧的设备栏panel组件
class LeftPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.device_blocks = {}
        self.current_block = None

    def on_size(self, event):
        # 计算自身size和pos（在父panel计算过了)
        # 重设设备的size和pos
        index = 0
        for key in self.device_blocks.keys():
            device_block = self.device_blocks[key]
            # 计算当前设备的size和pos
            b_size, b_pos = self.calc_device(index)
            device_block.SetSize(b_size)
            device_block.SetPosition(b_pos)
            index += 1

        super().on_size(event)

    def set_devices(self, devices: List[dvs.Device]):
        for device in devices:
            category_key = device.GetDeviceCategory()["category_id"]
            if category_key not in self.device_blocks.keys():
                device_block = self.DeviceBlock(parent = self)
                device_block.add_device(device)
                self.device_blocks[category_key] = device_block
            else:
                device_block = self.device_blocks[category_key]
                found = False
                for index in range(len(device_block.devices)):
                    device_inner = device_block.devices[index]
                    if device.GetId() == device_inner.GetId():
                        device_block.set_device(index, device)
                        found = True
                        break
                if not found:
                    device_block.add_device(device)
            # 设置icon
            device_block.refresh_icon()
            device_block.Bind(wx.EVT_LEFT_UP, self.on_block_left_up)

    def calc_device(self, index):
        w, h = self.GetSize()
        # 计算设备详情小图标panel的size和pos
        b_w = b_h = w
        b_x = 0
        b_y = index * b_h
        return (b_w, b_h), (b_x, b_y)

    def on_block_left_up(self, event):
        block_temp = event.GetEventObject()

        def trigger_on_size_event(obj):
            event_temp = wx.SizeEvent((0, 0))
            event_temp.SetEventObject(obj)
            obj.GetEventHandler().ProcessEvent(event_temp)

        # 判断当前已激活的block属性是否为空
        if self.current_block is None:
            block_temp.detail_panel = block_temp.set_detail_panel()
            block_temp.detail_panel.Popup()
            block_temp.activate()
            trigger_on_size_event(block_temp)
            self.current_block = block_temp
        else:
            # 判断当前点击的是否是已经激活的block
            if block_temp is not self.current_block:
                # 先将之前激活的block隐藏
                self.current_block.detail_panel.Dismiss()
                self.current_block.deactivate()
                # 如果当前准备激活的block还没有创建detail_panel，则创建一个
                if block_temp.detail_panel is None:
                    block_temp.detail_panel = block_temp.set_detail_panel()
                # 显示当前要激活的block
                trigger_on_size_event(block_temp)
                block_temp.detail_panel.Popup()
                block_temp.activate()
                self.current_block = block_temp
            else:
                # 如果当前点击的是已经激活的block，则什么都不做
                self.current_block.detail_panel.Popup()
                self.current_block.activate()
                pass
        event.Skip()

    # 设备组件内部类
    class DeviceBlock(widgets.CustomBorderPanel):
        def __init__(self, parent, id = -1, border_thickness = 1,
                     border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
            widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                               border_color = border_color, margin = margin, radius = radius)
            self.devices: List[dvs.Device] = []
            self.data_changed = False
            self.icons = None
            self.icon_bitmap = None
            self.detail_panel = None

            self.enter_color = configs.COLOR_DEVICE_BUTTON_HOVER
            self.background_color = self.GetParent().GetBackgroundColour()
            self.leave_color = self.background_color
            self.is_activated = False
            self.activated_color = configs.COLOR_DEVICE_BUTTON_TOGGLED
            self.clicked_color = configs.COLOR_DEVICE_BUTTON_DOWN

            self.Bind(wx.EVT_SIZE, self.on_size)
            self.Bind(wx.EVT_PAINT, self.on_paint)
            # 绑定事件，实现鼠标悬浮时改变背景颜色效果，移出时恢复原背景颜色（针对激活与否有不同的效果）
            self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
            self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
            self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
            self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_down)
            self.Bind(wx.EVT_SHOW, self.on_show)

        def on_size(self, event):
            # 计算自身size和pos（在父panel计算过了)
            # 计算detail_panel的size和pos
            if self.detail_panel is not None:
                dp_size, dp_pos = self.calc_detail_panel(self.detail_panel.count_device_info())
                self.detail_panel.SetSize(dp_size)
                self.detail_panel.SetPosition(dp_pos)
            event.Skip()

        def on_paint(self, event):
            dc = wx.GCDC(wx.PaintDC(self))

            # 根据不同设备状态，刷新icon图标
            self.refresh_icon()

            # 重设icon的size和pos
            image = self.icon_bitmap.ConvertToImage()
            # 计算icon的size和pos
            i_size, i_pos = self.calc_icon(image.GetSize())
            # 重新设置图片的尺寸
            image.Rescale(i_size[0], i_size[1], wx.IMAGE_QUALITY_HIGH)
            # 重新绘制bitmap
            bitmap = wx.Bitmap(image)
            dc.DrawBitmap(bitmap, i_pos, bitmap.GetMask() is not None)

            # 删除DC
            del dc

        def on_show(self, event):
            obj = event.GetEventObject()
            if obj is self.detail_panel:
                if not event.IsShown():
                    self.deactivate()

        def on_left_up(self, event):
            self.SetBackgroundColour(self.activated_color)
            self.Refresh()
            event.Skip()

        def on_left_down(self, event):
            self.SetBackgroundColour(self.clicked_color)
            self.Refresh()
            event.Skip()

        def on_enter(self, event):
            self.leave_color = self.background_color
            if self.is_activated:
                self.leave_color = self.activated_color
            else:
                self.SetBackgroundColour(self.enter_color)
            self.Refresh()
            event.Skip()

        def on_leave(self, event):
            if self.detail_panel and self.detail_panel.IsShown():
                if self.is_activated:
                    self.leave_color = self.activated_color
                else:
                    self.leave_color = self.background_color
            self.SetBackgroundColour(self.leave_color)
            self.Refresh()
            event.Skip()

        def activate(self):
            self.is_activated = True
            self.SetBackgroundColour(self.activated_color)
            self.Refresh()

        def deactivate(self):
            self.is_activated = False
            self.SetBackgroundColour(self.background_color)
            self.Refresh()

        def add_device(self, device: dvs.Device):
            self.devices.append(device)
            self.set_icons(device.GetDeviceCategory()["icons"])
            self.data_changed = True

        def set_device(self, index, device):
            self.devices[index] = device
            self.set_icons(device.GetDeviceCategory()["icons"])
            self.data_changed = True

        def set_icons(self, icons):
            if self.icons is None:
                self.icons = icons

        def refresh_icon(self):
            found_disconnected = False
            for device in self.devices:
                if device.GetDeviceStatus() == dvs.DEVICE_STATUS_DISCONNECTED:
                    found_disconnected = True
                    break

            if not found_disconnected:
                self.icon_bitmap = wx.Image(self.icons["normal"], wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            elif found_disconnected:
                self.icon_bitmap = wx.Image(self.icons["error"], wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        def set_detail_panel(self):
            if self.detail_panel is None:
                self.detail_panel = self.DeviceBlockDetail(self, configs.COLOR_DEVICE_BUTTON_TOGGLED,
                                                           self.border_color)
            found = False
            for device in self.devices:
                for index in range(len(self.detail_panel.device_info_arr)):
                    device_Info = self.detail_panel.device_info_arr[index]
                    if device.GetId() == device_Info["id"]:
                        self.detail_panel.set_device_info(index, device)
                        found = True
                if not found:
                    self.detail_panel.add_device_info(device)
            return self.detail_panel

        def calc_icon(self, image_size):
            w, h = self.GetSize()
            i_w, i_h = image_size
            i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), w * 0.7 / i_w)
            i_x = math.ceil((w - i_w) / 2)
            i_y = math.ceil((h - i_h) / 2)
            return (i_w, i_h), (i_x, i_y)

        def calc_detail_panel(self, count):
            w, h = self.GetSize()
            screen_x, screen_y = self.GetScreenPosition()

            dp_w = w * 5.5
            dp_h = h * count
            dp_x = w + screen_x
            dp_y = screen_y
            return (dp_w, dp_h), (dp_x, dp_y)

        # device小图标组件的详情panel
        class DeviceBlockDetail(wx.PopupTransientWindow):
            def __init__(self, parent, background_color = None, border_color = None):
                wx.PopupTransientWindow.__init__(self, parent)
                self.background_color = background_color
                self.border_color = border_color
                self.shadow_thickness = 4 # 小组件阴影厚度
                self.device_info_arr: List[dict] = []
                self.size_cache = None

                self.Bind(wx.EVT_SIZE, self.on_size)
                self.Bind(wx.EVT_PAINT, self.on_paint)
                self.Bind(wx.EVT_SHOW, self.on_show)
                self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

            def on_show(self, event):
                self.GetParent().GetEventHandler().ProcessEvent(event)

            def on_size(self, event):
                # 计算自身size和pos（在逻辑上的父panel计算过了（实际上的父panel是DeviceBlock的父panel）)
                if self.size_cache is not None and self.size_cache["panel_size"] != self.GetSize():
                    self.size_cache = None
                    for index in range(len(self.device_info_arr)):
                        device_info = self.device_info_arr[index]
                        button = device_info["button"]
                        if button and button.IsEnabled():
                            popup_window = button.popup_window
                            popup_window.SetSize(self.calc_operation_popup())
                event.Skip()

            def on_paint(self, event):
                if self.device_info_arr:
                    dc = wx.GCDC(wx.PaintDC(self))
                    shadow_thickness = self.shadow_thickness

                    info_len = len(self.device_info_arr)
                    if self.size_cache is None:
                        w, h = self.GetSize()
                        self.size_cache = {
                            "panel_size": None,
                            "size_pos_arr": None
                        }

                        if info_len > 0:
                            h_info = math.ceil(h / info_len)
                            v_gap = 0
                            self.size_cache["size_pos_arr"] = []
                            for index in range(info_len):
                                size_pos = {
                                    "font_size":    None,
                                    "icon_size":    None,
                                    "button_size":  None,
                                    "icon_pos":     None,
                                    "text_pos":     None,
                                    "button_pos":   None,
                                }
                                info = self.device_info_arr[index]

                                # 重设device信息的font_size
                                device_info = info["ip"] + "-" + str(info["port"])
                                dc.SetTextForeground(configs.COLOR_TEXT_BLACK)
                                font_temp = self.GetFont()
                                font_size = self.calc_font_size(w, h_info)
                                size_pos["font_size"] = font_size # 存入缓存
                                font_temp.SetPointSize(font_size)
                                dc.SetFont(font_temp)
                                tw, th = dc.GetTextExtent(device_info)

                                # 重设icon的size
                                image = wx.Image(info["status_const"]["icon"], wx.BITMAP_TYPE_ANY)
                                # 计算icon的size和pos
                                bw, bh = self.calc_icon(w, h_info, image.GetSize())
                                # 重新设置图片的尺寸
                                size_pos["icon_size"] = (bw, bh) # 存入缓存
                                image.Rescale(bw, bh, wx.IMAGE_QUALITY_HIGH)

                                # 计算并重设图片和文字的pos
                                # 图标左侧的缩进
                                w_indent = math.ceil(w / 40)
                                # 如果有多个设备，则每个设备之间信息显示的gap
                                v_gap = math.ceil((h_info - bh) / 2)
                                b_x = math.ceil((w - tw - bw - w_indent) / 5.5)
                                b_y = math.ceil((h_info - bh) / 2) + (h_info - v_gap) * index
                                size_pos["icon_pos"] = (b_x, b_y) # 存入缓存
                                t_x = b_x + bw + w_indent
                                t_y = math.ceil((h_info - th) / 2 - math.ceil(th / 20)) + (h_info - v_gap) * index
                                size_pos["text_pos"] = (t_x, t_y) # 存入缓存

                                # 重新计算button的size和pos
                                button: widgets.CustomRadiusButton = info["button"]
                                if button:
                                    button_h = bh * 0.85
                                    button_w = button_h * 1.3 + button_h * 0.5 * len(button.label)
                                    button_x = w - button_w - w_indent
                                    button_y = math.ceil((h_info - button_h) / 2) + (h_info - v_gap) * index
                                    size_pos["button_size"] = (button_w, button_h)  # 存入缓存
                                    size_pos["button_pos"] = (button_x, button_y)  # 存入缓存

                                self.size_cache["size_pos_arr"].append(size_pos)

                            # 将多余的高度去掉
                            panel_size = (w + shadow_thickness, h - v_gap * (info_len - 1) + shadow_thickness)
                            self.size_cache["panel_size"] = panel_size
                            self.SetSize(panel_size)

                    w, h = self.size_cache["panel_size"]
                    # 设置画笔、画刷的颜色
                    pen = wx.Pen(self.border_color, 1)
                    dc.SetPen(pen)
                    brush = wx.Brush(self.background_color)
                    dc.SetBrush(brush)

                    # 画出bitmap的形状
                    dc.DrawRoundedRectangle(0, 0, w - shadow_thickness, h - shadow_thickness, 0)

                    size_pos_arr = self.size_cache["size_pos_arr"]
                    for index in range(info_len):
                        info = self.device_info_arr[index]

                        # 重设device信息的font_size
                        device_info = info["ip"] + "-" + str(info["port"])
                        dc.SetTextForeground(configs.COLOR_TEXT_BLACK)
                        font_temp = self.GetFont()
                        font_temp.SetPointSize(size_pos_arr[index]["font_size"])
                        dc.SetFont(font_temp)

                        # 重设icon的size
                        image = wx.Image(info["status_const"]["icon"], wx.BITMAP_TYPE_ANY)
                        # 计算icon的size和pos
                        bw, bh = size_pos_arr[index]["icon_size"]
                        # 重新设置图片的尺寸
                        image.Rescale(bw, bh, wx.IMAGE_QUALITY_HIGH)
                        # 重新绘制bitmap
                        bitmap = wx.Bitmap(image)

                        # 从缓存中取出icon和text的pos
                        b_x, b_y = size_pos_arr[index]["icon_pos"]
                        t_x, t_y = size_pos_arr[index]["text_pos"]
                        # 重新绘制icon和pos
                        dc.DrawBitmap(bitmap, (b_x, b_y), bitmap.GetMask() is not None)
                        dc.DrawText(device_info, (t_x, t_y))

                        # 重设button的size和pos
                        button: widgets.CustomRadiusButton = info["button"]
                        if button:
                            button_w, button_h = size_pos_arr[index]["button_size"]
                            button_x, button_y = size_pos_arr[index]["button_pos"]
                            button.SetSize(button_w, button_h)
                            button.SetPosition((button_x, button_y))

                    # 绘制阴影
                    w, h = self.size_cache["panel_size"]
                    shadow_w, shadow_h = w - shadow_thickness, h - shadow_thickness
                    for i in range(shadow_thickness):
                        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 255 / 4 + (1 - 255 / 4) * (i + 1) / shadow_thickness), 1))
                        dc.DrawLine((i, shadow_h + i), (shadow_w + i, shadow_h + i))
                        dc.DrawLine((shadow_w + i, i), (shadow_w + i, shadow_h + i - 1))

                    # 删除DC
                    del dc

            def add_device_info(self, device: dvs.Device):
                self.device_info_arr.append({
                    "id": device.GetId(),
                    "ip": device.GetDeviceIp(),
                    "port": device.GetDevicePort(),
                    "status_const": device.GetDeviceStatus(),
                    "brand_const": device.GetDeviceBrand(),
                    "button": self.needs_operation_button(device),
                })

            def set_device_info(self, index, device: dvs.Device):
                self.device_info_arr[index]["button"].Destroy()
                self.device_info_arr[index] = {
                    "id": device.GetId(),
                    "ip": device.GetDeviceIp(),
                    "port": device.GetDevicePort(),
                    "status_const": device.GetDeviceStatus(),
                    "brand_const": device.GetDeviceBrand(),
                    "button": self.needs_operation_button(device),
                }

            def needs_operation_button(self, device: dvs.Device):
                if device.GetDeviceBrand() is not None:
                    button = widgets.CustomRadiusButton(self, wx.ID_ANY,
                                                        label = "操作",
                                                        font_color = configs.COLOR_BUTTON_TEXT,
                                                        background_color = configs.COLOR_BUTTON_BACKGROUND,
                                                        clicked_color = configs.COLOR_BUTTON_FOCUSED,
                                                        radius = 2)
                    if device.GetDeviceStatus() == dvs.DEVICE_STATUS_DISCONNECTED:
                        button.Disable()
                    button.device = device
                    button.popup_window = None
                    button.Bind(wx.EVT_LEFT_UP, self.operation_button_click)
                    return button
                return None

            def operation_button_click(self, event):
                button = event.GetEventObject()
                if button.device.GetDeviceStatus() == dvs.DEVICE_STATUS_CONNECTED:
                    self.show_operation_window(button)
                event.Skip()

            def count_device_info(self):
                return len(self.device_info_arr)

            def calc_font_size(self, w, h):
                return math.floor(math.ceil(h / 3.8))

            def calc_icon(self, w, h, image_size):
                i_w, i_h = image_size
                i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), w * 0.1 / i_w)
                return i_w, i_h

            def calc_operation_popup(self):
                tp_w, tp_h = CommonUtils.GetTopParent(self).GetSize()
                return tp_w // 1.7, tp_h // 6 + tp_w * 0.015

            def show_operation_window(self, button):
                if button.popup_window is None:
                    button.popup_window = self.OperationPopupWindow(self.GetParent(),
                                                                    device = button.device,
                                                                    size = self.calc_operation_popup())
                button.popup_window.Show()

            class OperationPopupWindow(widgets.CustomPopupWindow):
                def __init__(self, parent, device: dvs.Device, size):
                    widgets.CustomPopupWindow.__init__(self, parent, "手动操作工具")
                    self.device = device
                    self.thread = device.GetDeviceThread()
                    self.add_button("禁用", self.lock_device)
                    self.add_button("使能", self.unlock_device)
                    self.add_button("下发", self.switch_pset)
                    self.add_button("关闭", self.close)
                    # 所有detail的数组
                    self.inner_widgets: List[dict] = []
                    # 创建一个垂直存每一行组件的panel数组
                    self.lines: List[wx.Panel] = []

                    # 第一行信息
                    self.panel_1 = wx.Panel(self.content_panel, wx.ID_ANY)
                    self.lines.append(self.panel_1)
                    # 站点
                    self.station_id_txt_ctrl = self.add_widget(self.panel_1, "站点")
                    # 程序
                    self.pset_txt_ctrl = self.add_widget(self.panel_1, "程序")

                    self.SetSize(size)

                def lock_device(self, event):
                    print("禁用设备")
                    # self.Hide()
                    event.Skip()

                def unlock_device(self, event):
                    print("使能设备")
                    # self.Hide()
                    event.Skip()

                def switch_pset(self, event):
                    station_id = int(self.station_id_txt_ctrl.GetValue())
                    pset = int(self.pset_txt_ctrl.GetValue())
                    print(f"pset切换：站点 = {station_id}，程序 = {pset}")
                    # self.Hide()
                    event.Skip()

                def close(self, event):
                    self.Hide()
                    event.Skip()

                def on_size(self, event):
                    super().on_size(event)

                    if self.content_font_pixel_size is None:
                        return
                    # 内容的内、外边距
                    content_gap = self.indent / 2
                    # 循环给所有组件设置字体大小
                    font_temp = self.GetFont()
                    font_temp.SetPixelSize(self.content_font_pixel_size)
                    # 找到所有title中最长的那个，以那个长度为基准设置text_control的起始位置
                    longest_title_width = 0
                    for json_obj in self.inner_widgets:
                        json_obj["text_control"].SetFont(font_temp)
                        title_st: wx.StaticText = json_obj["title"]
                        title_st.SetFont(font_temp)
                        width_of_title = title_st.GetSize()[0]
                        # 找到最长的title的width
                        if width_of_title > longest_title_width:
                            longest_title_width = width_of_title

                    # 重设所有组件的size和pos
                    len_of_lines = len(self.lines)
                    panel_size = self.calc_panel_size(self.content_size, len_of_lines)
                    for index in range(len_of_lines):
                        panel_w, panel_h = panel_size
                        # 重设panel的size和pos
                        panel = self.lines[index]
                        panel.SetSize(panel_size)
                        panel.SetPosition(self.calc_panel_pos(panel_h, index))
                        # 获取每一行panel中的 title + text 对
                        children = panel.GetChildren()
                        len_of_children = len(children)
                        cols = math.ceil(len_of_children / 2)
                        # 循环每一个组件
                        for i in range(len_of_children):
                            if i % 2 == 0:
                                title_st: wx.StaticText = children[i]
                                title_st_x = (i // cols) * (panel_w // cols + content_gap) + (longest_title_width - title_st.GetSize()[0])
                                title_st_y = (panel_h - title_st.GetSize()[1]) // 2
                                title_st.SetPosition((title_st_x, title_st_y))
                            else:
                                text_ctrl = children[i]
                                text_ctrl_w = (panel_w - (cols - 1) * self.indent - cols * longest_title_width) // 2 - content_gap * cols
                                text_ctrl_h = self.content_font_pixel_height * 1.8
                                text_ctrl_x = (i // cols) * (panel_w // cols + content_gap) + longest_title_width + content_gap * cols
                                text_ctrl_y = (panel_h - text_ctrl_h) // 2
                                text_ctrl.SetSize(text_ctrl_w, text_ctrl_h)
                                text_ctrl.SetPosition((text_ctrl_x, text_ctrl_y))
                                if not isinstance(text_ctrl, widgets.CustomTextCtrl):
                                    ts = text_ctrl.GetChildren()
                                    t1: widgets.CustomTextCtrl = ts[0]
                                    t2: wx.StaticText = ts[1]
                                    t3: widgets.CustomTextCtrl = ts[2]
                                    child_w = (text_ctrl_w - self.indent * 2) // 2
                                    # 设置下限
                                    t1.SetSize(child_w, text_ctrl_h)
                                    t1.SetFont(font_temp)
                                    t1.SetPosition((0, 0))
                                    # “~”符号
                                    t2.SetFont(font_temp)
                                    label_w, label_h = t2.GetSize()
                                    t2.SetPosition((child_w + (label_w // 2), (text_ctrl_h - label_h) // 2))
                                    # 设置上限
                                    t3.SetSize(child_w, text_ctrl_h)
                                    t3.SetFont(font_temp)
                                    t3.SetPosition((child_w + self.indent * 2, 0))

                def add_widget(self, parent, title):
                    json_obj = {
                        "title": wx.StaticText(parent, label = title),
                        "text_control": widgets.CustomTextCtrl(parent, value = "1",
                                                               background_color = configs.COLOR_COMMON_WHITE,
                                                               validator = widgets.NumericalValidator())
                    }
                    self.inner_widgets.append(json_obj)
                    return json_obj["text_control"]

                def calc_panel_size(self, content_size, len_of_lines):
                    c_w, c_h = content_size
                    return c_w, c_h // len_of_lines

                def calc_panel_pos(self, panel_h, index):
                    return 0, panel_h * index



# 中间上方的扫码panel
class MiddleTopPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.SetBackgroundColour(configs.COLOR_TEXT_CONTROL_BACKGROUND)
        self.icon_bitmap = None
        self.icon_size = None
        self.icon_pos = None
        self.text_content = "扫描录入或点击输入条码信息"
        self.text_control = None
        self.popup_window = None
        self.default_value = None
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    def on_size(self, event):
        # 计算自身size和pos（在父panel计算过了)
        # 计算logo的size和pos（提前算是因为text_control需要用）
        if self.icon_bitmap is not None:
            image = self.icon_bitmap.ConvertToImage()
            i_size, i_pos = self.calc_icon(image.GetSize())
            self.icon_size = i_size
            self.icon_pos = i_pos

        # 重设text_control的size和pos
        t_size, t_pos = self.calc_text_control(self.icon_size)
        self.text_control.SetSize(t_size)
        self.text_control.SetPosition(t_pos)

        # 重设字体大小
        font_temp = self.calc_font_size(self.GetFont())
        self.text_control.SetFont(font_temp)

        # 重设扫码弹出框size和pos
        if self.popup_window is not None:
            self.popup_window.SetSize(self.calc_popup_window())

        super().on_size(event)

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))

        # 重设扫码icon的size和pos
        image = self.icon_bitmap.ConvertToImage()
        # 重新设置图片的尺寸
        image.Rescale(self.icon_size[0], self.icon_size[1], wx.IMAGE_QUALITY_BILINEAR)
        # 重新绘制bitmap
        bitmap = wx.Bitmap(image)
        dc.DrawBitmap(bitmap, self.icon_pos, bitmap.GetMask() is not None)

        # 删除DC
        del dc

    def set_icon(self, bitmap):
        self.icon_bitmap = bitmap

    def add_text_control(self):
        self.text_control = wx.TextCtrl(self, value = self.text_content,
                                        style = wx.BORDER_NONE | wx.TE_READONLY)
        self.text_control.SetForegroundColour(configs.COLOR_TEXT_CONTROL_FONT)
        self.text_control.SetBackgroundColour(configs.COLOR_TEXT_CONTROL_BACKGROUND)
        self.text_control.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    def on_left_up(self, event):
        if self.popup_window is None:
            self.popup_window = self.InnerPopup(parent = self.GetTopLevelParent(),
                                                title = "录入条码",
                                                size = self.calc_popup_window(),
                                                hint = self.text_content,
                                                out_put_window = self.text_control)
        self.popup_window.Show()
        event.Skip()

    def calc_icon(self, image_size):
        w, h = self.GetSize()
        i_w, i_h = image_size
        i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), h * 0.75 / i_h)
        i_x = i_y = math.ceil((h - i_h) / 2)
        return (i_w, i_h), (i_x, i_y)

    def calc_text_control(self, image_size):
        if image_size is None:
            return (0, 0), (0, 0)
        w, h = self.GetSize()
        i_w, i_h = image_size
        indent = math.ceil((h - i_h) / 2) * 2
        t_w = w - i_w - indent - 1
        t_h = h * 0.75
        t_x = i_h + indent
        t_y = math.ceil((h - t_h) / 2) + t_h / 25
        return (t_w, t_h), (t_x, t_y)

    def calc_font_size(self, font_temp):
        w, h = self.GetSize()
        # 计算font
        size = math.floor(math.ceil(h / 2.7) + 0.4)
        font_temp.SetPointSize(size)
        return font_temp

    def calc_popup_window(self):
        tp_w, tp_h = self.GetTopLevelParent().GetSize()
        return tp_w // 1.7, tp_h // 6 + tp_w * 0.015

    # 弹框组件
    class InnerPopup(widgets.CustomPopupWindow):
        def __init__(self, parent, title, size, hint, out_put_window: wx.TextCtrl):
            widgets.CustomPopupWindow.__init__(self, parent, title)
            self.hint = hint
            self.add_button("确定", self.confirm)
            self.add_button("取消", self.cancel)

            self.text_control = widgets.CustomTextCtrl(self.content_panel, hint = hint, validator = widgets.NumericalValidator())
            self.text_control.SetBackgroundColour(configs.COLOR_COMMON_WHITE)
            # TODO: 得加一个ENTER确定的事件、一个ESC退出事件
            self.out_put_window = out_put_window

            self.SetSize(size)

        def confirm(self, event):
            self.Hide()
            text = self.text_control.GetValue()
            if text is not None and text != "":
                self.out_put_window.SetValue(text)
            else:
                self.out_put_window.SetValue(self.hint)
            event.Skip()

        def cancel(self, event):
            self.Hide()
            event.Skip()

        def on_size(self, event):
            super().on_size(event)
            self.text_control.SetSize(self.content_panel.GetSize())
            if self.content_font_pixel_height:
                font_temp = self.text_control.GetFont()
                font_temp.SetPixelSize(self.content_font_pixel_size)
                self.text_control.SetFont(font_temp)

        def on_show(self, event):
            super().on_show(event)
            if not event.IsShown:
                self.GetParent().Refresh()


# 中间下方的产品展示、工作流程panel
class MiddleBottomPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1, mission_obj: pdctmsn.ProductMission = None,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.mission_obj = mission_obj
        self.mission_indexs = [0, 0]
        self.product_image = wx.Image()
        self.product_bitmap = wx.Bitmap()
        self.product_bitmap_size = (0, 0)
        self.product_bitmap_position = (0, 0)
        self.bolts = []
        self.current_working_bolt = None
        # 用于判断是否需要重新绘制
        self.mission_indexs_cache = None
        self.mission_status_cache = None
        self.bolts_cache = None
        self.bolts_status_cache = None
        self.static_bitmap = wx.StaticBitmap(self)
        # 绑定事件
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def get_variables(self):
        self.mission_indexs = self.mission_obj.GetMissionIndexs()
        mission_side = self.mission_obj.GetMissionProductSides()[self.mission_indexs[0]]
        mission_image = mission_side.GetSideImage().GetImageOriginal()
        bolts = mission_side.GetBolts()

        self.mission_obj.GetMissionProductSides()[0].GetBolts()

        # 1. 判断当前indexs是否与之前一致，如果不一致则直接跳过其他判断直接重新获取数据
        if self.mission_indexs_cache == self.mission_indexs:
            # 2. 判断当前任务状态是否与之前一致，否则同上
            if self.mission_status_cache == self.mission_obj.GetMissionStatus():
                # 3. 判断当前螺丝点位对象数组是否与之前一致，否则同上
                if self.bolts_cache == bolts:
                    # 4. 判断缓存点位状态的长度是否与螺丝点位数组长度一直，否则同上
                    if len(self.bolts_status_cache) == len(bolts):
                        all_matched = True
                        for index in range(len(bolts)):
                            bolt = bolts[index]
                            # 5. 循环判断每一个缓存点位状态是否与对应的对位状态一致，不一致则退出循环，重新获取数据
                            if self.bolts_status_cache[index] != bolt.GetBoltStatus():
                                all_matched = False
                                break
                        if all_matched:
                            return False

        # 重新获取最新数据
        self.mission_indexs_cache = self.mission_indexs
        self.mission_status_cache = self.mission_obj.GetMissionStatus()
        self.bolts_cache = bolts
        # 重新设置缓存数据
        self.product_image = CommonUtils.PILImageToWxImage(mission_image)
        self.product_bitmap = CommonUtils.PILImageToWxImage(mission_image).ConvertToBitmap()

        # 将当前显示的螺丝点位组件隐藏
        for bolt in self.bolts:
            bolt.button.Hide()

        # 循环最新点位设置缓存点位状态及检查点位是否有创建组件
        self.bolts_status_cache = []
        for index in range(len(bolts)):
            bolt = bolts[index]
            # 设置缓存点位状态
            self.bolts_status_cache.append(bolt.GetBoltStatus())
            # 如果没有创建组件则创建组件
            if not hasattr(bolt, "button"):
                bolt.button = self.BoltButton(self, mission_obj = self.mission_obj, bolt_obj = bolt, current_index = index)
                bolt.button.bolt_position = bolt.GetBoltPosition()
                bolt.button.Hide()
                # 绑定点击事件（通过覆盖在staticBitmap上的透明panel触发）
                bolt.button.blank_panel.Bind(wx.EVT_LEFT_UP, self.bolt_button_key_up)
            if self.current_working_bolt is None and index == self.mission_indexs[1]:
                self.current_working_bolt = bolt.button

        # 更新当前点位数组
        self.bolts = bolts
        # 返回True表示数据有更新
        return True

    def bolt_button_key_up(self, event):
        bolt_button = event.GetEventObject()
        bolt_button.real_widget.show_details_window()
        event.Skip()

    def on_size(self, event):
        w, h = self.GetSize()

        # 获取最新的数据
        self.get_variables()

        # 重新计算产品图片的size和pos（提前计算好，绘制的时候就不需要再算了，直接拿到最新的图片绘制即可）
        self.product_bitmap_size = self.calc_product_image_size(w, h, self.product_image.GetSize())
        self.product_bitmap_position = self.calc_product_image_pos(w, h, self.product_bitmap_size)

        # 重新计算螺丝点位组件的size和pos（提前计算好并且要立马设置好，以免在paint事件里绘制时会频繁触发paint事件）
        self.calc_and_set_bolt_size_and_pos()
        wx.CallAfter(self.show_bolt_buttons)

        super().on_size(event)

    def on_paint(self, event):
        # 获取最新的数据
        self.get_variables()

        dc = wx.GCDC(wx.PaintDC(self))
        dc.Clear()
        self.calc_and_set_bolt_size_and_pos()

        # 重新设置图片的尺寸
        image = self.product_image.Copy()
        image.Rescale(self.product_bitmap_size[0], self.product_bitmap_size[1], wx.IMAGE_QUALITY_BILINEAR)
        # 重新绘制bitmap
        self.product_bitmap = wx.Bitmap(image)
        # 绘制产品图片
        self.static_bitmap.SetPosition(self.product_bitmap_position)
        self.static_bitmap.SetBitmap(self.product_bitmap)

        wx.CallAfter(self.show_bolt_buttons)
        event.Skip()

    def show_bolt_buttons(self):
        # 显示螺丝点位
        for bolt in self.bolts:
            bolt.button.Show()

    def calc_product_image_size(self, w, h, image_size):
        # 以高为基准，高一定保持与panel一致（填满），因为没有任何屏幕是高比宽长的除非屏幕竖起来
        # i_w, i_h = image_size
        # ratio = h / i_h
        # if i_h > i_w:
        #     ratio = w / i_w
        # i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), ratio)
        return w, h

    def calc_product_image_pos(self, w, h, image_size):
        # 以高为基准，高一定保持与panel一致（填满），因为没有任何屏幕是高比宽长的除非屏幕竖起来
        # i_w, i_h = image_size
        # ratio = h / i_h
        # if i_h > i_w:
        #     ratio = w / i_w
        # i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), ratio)
        return 0, 0

    def calc_and_set_bolt_size_and_pos(self):
        b_size = self.calc_bolt_size()
        for bolt in self.bolts:
            bolt_pos = bolt.button.bolt_position
            bolt.button.SetSize(b_size)
            bolt.button.SetPosition(self.calc_bolt_pos(bolt_pos))
            bolt.button.blank_panel.SetPosition(self.calc_bolt_pos(bolt_pos))
            bolt.button.Refresh()

    def calc_bolt_size(self):
        i_w, i_h = self.product_bitmap_size
        b_w = b_h = math.ceil(i_w / 40) + math.ceil(i_h / 25)
        return b_w, b_h

    def calc_bolt_pos(self, bolt_position):
        i_w, i_h = self.product_bitmap_size
        i_x, i_y = self.product_bitmap_position
        bolt_x, bolt_y = bolt_position
        return bolt_x // 2, bolt_y // 2

    # 螺丝点位block按钮内部组件
    class BoltButton(wx.Control):
        def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                     size = wx.DefaultSize, validator = wx.DefaultValidator, name = "BoltButton",
                     mission_obj: pdctmsn.ProductMission = None, bolt_obj: pdctmsn.ProductBolt = None, current_index: int = 0):
            wx.Control.__init__(self, parent = parent, id = id, pos = pos, size = size,
                                style = wx.BORDER_NONE, validator = validator, name = name)
            self.mission_obj = mission_obj
            self.bolt_obj = bolt_obj
            self.current_index = current_index
            self.label = str(self.current_index + 1)
            self.status_temp = None
            self.status_temp = self.bolt_obj.GetBoltStatus()

            self.image_size = (0, 0)
            self.image_position = (0, 0)
            self.bolt_position = (0, 0)
            self.border_thickness = 0
            self.current_background_color = self.get_color_by_status()[0]

            # 弄一个parent是产品图片staticBitmap的透明的panel，用来触发此组件本身的事件（因为staticBitmap挡住了）
            self.blank_panel = wx.Panel(parent.static_bitmap, wx.ID_ANY, style = wx.TRANSPARENT_WINDOW)
            self.blank_panel.real_widget = self
            # 螺栓点位详情
            self.details_window = None

            self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
            self.blank_panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
            self.Bind(wx.EVT_SIZE, self.on_size)
            self.Bind(wx.EVT_PAINT, self.on_paint)
            self.Bind(wx.EVT_SHOW, self.on_show)
            self.blank_panel.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
            self.blank_panel.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
            self.blank_panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
            self.blank_panel.Bind(wx.EVT_LEFT_DCLICK, self.on_left_down)
            self.blank_panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)

        def set_status_temp(self, status):
            self.status_temp = status
            self.current_background_color = self.get_color_by_status()[0]

        def on_show(self, event):
            if self.blank_panel:
                self.blank_panel.Show(event.IsShown())

        def on_size(self, event):
            w, h = self.GetSize()
            self.blank_panel.SetSize(w, h)
            self.border_thickness = math.ceil(w / 20)
            # 设置螺栓点位详情窗口的大小
            if self.details_window is not None:
                self.details_window.SetSize(self.calc_details_window())
            event.Skip()

        def on_paint(self, event):
            w, h = self.GetSize()
            bitmap = wx.Bitmap(w, h)
            dc = wx.MemoryDC(bitmap)

            # 让背景全黑，方便后续设置透明色
            dc.SetBackground(wx.Brush(wx.BLACK))
            dc.Clear()

            # 设置画笔、画刷的颜色
            dc.SetPen(wx.Pen(configs.COLOR_WORKPLACE_BOLT_BORDER, self.border_thickness))
            dc.SetBrush(wx.Brush(self.current_background_color))

            # 画出bitmap的形状
            dc.DrawCircle(w // 2, h // 2, (w - self.border_thickness) // 2)

            # 绘制文字
            dc.SetTextForeground(configs.COLOR_WORKPLACE_BOLT_NUMBER)
            font_temp = self.GetFont()
            font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
            font_temp.SetPointSize(int(w / 3) + 2)
            dc.SetFont(font_temp)
            tw, th = dc.GetTextExtent(self.label)
            dc.DrawText(self.label, (w - tw) // 2, (h - th) // 2)

            # 设置透明色
            image = bitmap.ConvertToImage()
            if not image.HasAlpha():
                image.InitAlpha()
            for y in range(image.GetHeight()):
                for x in range(image.GetWidth()):
                    pix = wx.Colour(image.GetRed(x, y),
                                    image.GetGreen(x, y),
                                    image.GetBlue(x, y),
                                    image.GetAlpha(x, y))
                    if pix == wx.BLACK:
                        image.SetAlpha(x, y, 0)

            # 画好了
            bitmap = image.ConvertToBitmap()

            dc = wx.GCDC(wx.PaintDC(self))
            dc.DrawBitmap(bitmap, (0, 0), bitmap.GetMask() is not None)

            # 删除DC
            del dc

        def on_enter(self, event):
            self.current_background_color = self.get_color_by_status()[1]
            self.Refresh()
            event.Skip()

        def on_leave(self, event):
            self.current_background_color = self.get_color_by_status()[0]
            self.Refresh()
            event.Skip()

        def on_left_down(self, event):
            self.current_background_color = self.get_color_by_status()[2]
            self.Refresh()
            event.Skip()

        def on_left_up(self, event):
            self.current_background_color = self.get_color_by_status()[0]
            self.Refresh()
            event.Skip()

        def get_color_by_status(self):
            if self.status_temp == pdctmsn.STATUS_SCREW_GUN_DEFAULT:
                return [
                    configs.COLOR_WORKPLACE_BOLT_BG_WAITING,
                    configs.COLOR_WORKPLACE_BOLT_BG_WAITING_HOVER,
                    configs.COLOR_WORKPLACE_BOLT_BG_WAITING_KEY_DOWN,
                ]
            elif self.status_temp == pdctmsn.STATUS_SCREW_GUN_TIGHTENING \
                    or self.status_temp == pdctmsn.STATUS_SCREW_GUN_LOOSENING:
                return [
                    configs.COLOR_WORKPLACE_BOLT_BG_WORKING,
                    configs.COLOR_WORKPLACE_BOLT_BG_WORKING_HOVER,
                    configs.COLOR_WORKPLACE_BOLT_BG_WORKING_KEY_DOWN,
                ]
            elif self.status_temp == pdctmsn.STATUS_SCREW_GUN_TIGHTENING_COMPLETE \
                    or self.status_temp == pdctmsn.STATUS_SCREW_GUN_LOOSENING_COMPLETE:
                return [
                    configs.COLOR_WORKPLACE_BOLT_BG_DONE,
                    configs.COLOR_WORKPLACE_BOLT_BG_DONE_HOVER,
                    configs.COLOR_WORKPLACE_BOLT_BG_DONE_KEY_DOWN,
                ]
            elif self.status_temp == pdctmsn.STATUS_SCREW_GUN_TIGHTENING_ERROR \
                    or self.status_temp == pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR:
                return [
                    configs.COLOR_WORKPLACE_BOLT_BG_ERROR,
                    configs.COLOR_WORKPLACE_BOLT_BG_ERROR_HOVER,
                    configs.COLOR_WORKPLACE_BOLT_BG_ERROR_KEY_DOWN,
                ]
            else:
                print(f"螺丝孔位状态有有误：current_index = [{self.current_index}], status_temp = [{self.status_temp}]")
                return [
                    configs.COLOR_WORKPLACE_BOLT_BG_WAITING,
                    configs.COLOR_WORKPLACE_BOLT_BG_WAITING_HOVER,
                    configs.COLOR_WORKPLACE_BOLT_BG_WAITING_KEY_DOWN,
                ]

        def calc_details_window(self):
            tp_w, tp_h = self.GetTopLevelParent().GetSize()
            return tp_w // 1.3, tp_h // 2.7 + tp_w * 0.015

        def show_details_window(self):
            if self.details_window is None:
                self.details_window = self.BoltDetailsPopupWindow(self.GetTopLevelParent(),
                                                                  size = self.calc_details_window(),
                                                                  bolt_obj = self.bolt_obj)
            self.details_window.Show()

        # 螺丝孔位详情弹框组件
        class BoltDetailsPopupWindow(widgets.CustomPopupWindow):
            def __init__(self, parent, size, bolt_obj: pdctmsn.ProductBolt):
                widgets.CustomPopupWindow.__init__(self, parent, bolt_obj.GetBoltName())
                self.bolt_obj = bolt_obj
                self.add_button("切换到此点位", self.switch)
                self.add_button("关闭", self.close)
                # 所有detail的数组
                self.detail_widgets: List[dict] = []
                # 创建一个垂直存每一行组件的panel数组
                self.lines: List[wx.Panel] = []

                # 第一行信息
                self.panel_1 = wx.Panel(self.content_panel, wx.ID_ANY)
                self.lines.append(self.panel_1)
                # 螺栓点位描述
                self.add_bolt_detail_widget(self.panel_1, "螺栓点位描述", bolt_obj.GetBoltDescription())
                # 螺栓规格
                self.add_bolt_detail_widget(self.panel_1, "螺栓规格", bolt_obj.GetBoltSpecification())

                # 第二行信息
                self.panel_2 = wx.Panel(self.content_panel, wx.ID_ANY)
                self.lines.append(self.panel_2)
                # 工具id
                self.add_bolt_detail_widget(self.panel_2, "工具id", bolt_obj.GetToolID())
                # 工具描述
                self.add_bolt_detail_widget(self.panel_2, "工具描述", bolt_obj.GetToolDescription())

                # 第三行信息
                self.panel_3 = wx.Panel(self.content_panel, wx.ID_ANY)
                self.lines.append(self.panel_3)
                # 批头规格
                self.add_bolt_detail_widget(self.panel_3, "批头规格", bolt_obj.GetBitSpecification())
                # pset
                self.add_bolt_detail_widget(self.panel_3, "pset", bolt_obj.GetProcedureSet())

                # 第四行信息
                self.panel_4 = wx.Panel(self.content_panel, wx.ID_ANY)
                self.lines.append(self.panel_4)
                # 扭矩上下限
                self.add_bolt_detail_widget(self.panel_4, "扭矩上下限", bolt_obj.GetTorqueLimit())
                # 角度上下限
                self.add_bolt_detail_widget(self.panel_4, "角度上下限", bolt_obj.GetAngleLimit())

                self.SetSize(size)

            def switch(self, event):
                print("切换到此点位")
                self.Hide()
                event.Skip()

            def close(self, event):
                self.Hide()
                event.Skip()

            def on_size(self, event):
                super().on_size(event)

                if self.content_font_pixel_size is None:
                    return
                # 内容的内、外边距
                content_gap = self.indent / 2
                # 循环给所有组件设置字体大小
                font_temp = self.GetFont()
                font_temp.SetPixelSize(self.content_font_pixel_size)
                # 找到所有title中最长的那个，以那个长度为基准设置text_control的起始位置
                longest_title_width = 0
                for json_obj in self.detail_widgets:
                    json_obj["text_control"].SetFont(font_temp)
                    title_st: wx.StaticText = json_obj["title"]
                    title_st.SetFont(font_temp)
                    width_of_title = title_st.GetSize()[0]
                    # 找到最长的title的width
                    if width_of_title > longest_title_width:
                        longest_title_width = width_of_title

                # 重设所有组件的size和pos
                len_of_lines = len(self.lines)
                panel_size = self.calc_panel_size(self.content_size, len_of_lines)
                for index in range(len_of_lines):
                    panel_w, panel_h = panel_size
                    # 重设panel的size和pos
                    panel = self.lines[index]
                    panel.SetSize(panel_size)
                    panel.SetPosition(self.calc_panel_pos(panel_h, index))
                    # 获取每一行panel中的 title + text 对
                    children = panel.GetChildren()
                    len_of_children = len(children)
                    cols = math.ceil(len_of_children / 2)
                    # 循环每一个组件
                    for i in range(len_of_children):
                        if i % 2 == 0:
                            title_st: wx.StaticText = children[i]
                            title_st_x = (i // cols) * (panel_w // cols + content_gap) + (longest_title_width - title_st.GetSize()[0])
                            title_st_y = (panel_h - title_st.GetSize()[1]) // 2
                            title_st.SetPosition((title_st_x, title_st_y))
                        else:
                            text_ctrl = children[i]
                            text_ctrl_w = (panel_w - (cols - 1) * self.indent - cols * longest_title_width) // 2 - content_gap * cols
                            text_ctrl_h = self.content_font_pixel_height * 1.8
                            text_ctrl_x = (i // cols) * (panel_w // cols + content_gap) + longest_title_width + content_gap * cols
                            text_ctrl_y = (panel_h - text_ctrl_h) // 2
                            text_ctrl.SetSize(text_ctrl_w, text_ctrl_h)
                            text_ctrl.SetPosition((text_ctrl_x, text_ctrl_y))
                            if not isinstance(text_ctrl, widgets.CustomTextCtrl):
                                ts = text_ctrl.GetChildren()
                                t1: widgets.CustomTextCtrl = ts[0]
                                t2: wx.StaticText = ts[1]
                                t3: widgets.CustomTextCtrl = ts[2]
                                child_w = (text_ctrl_w - self.indent * 2) // 2
                                # 设置下限
                                t1.SetSize(child_w, text_ctrl_h)
                                t1.SetFont(font_temp)
                                t1.SetPosition((0, 0))
                                # “~”符号
                                t2.SetFont(font_temp)
                                label_w, label_h = t2.GetSize()
                                t2.SetPosition((child_w + (label_w // 2), (text_ctrl_h - label_h) // 2))
                                # 设置上限
                                t3.SetSize(child_w, text_ctrl_h)
                                t3.SetFont(font_temp)
                                t3.SetPosition((child_w + self.indent * 2, 0))

            def add_bolt_detail_widget(self, parent, title, data):
                json_obj = {
                    "title": wx.StaticText(parent, label = title)
                }
                if isinstance(data, tuple):
                    panel_temp = wx.Panel(parent, wx.ID_ANY)
                    json_obj["text_control"] = panel_temp
                    widgets.CustomTextCtrl(panel_temp, value = str(data[0]),
                                           style = wx.TE_READONLY,
                                           background_color = configs.COLOR_COMMON_WHITE)
                    wx.StaticText(panel_temp, label = "~")
                    widgets.CustomTextCtrl(panel_temp, value = str(data[1]),
                                           style = wx.TE_READONLY,
                                           background_color = configs.COLOR_COMMON_WHITE)
                else:
                    json_obj["text_control"] = widgets.CustomTextCtrl(parent, value = str(data),
                                                                      style = wx.TE_READONLY,
                                                                      background_color = configs.COLOR_COMMON_WHITE)
                self.detail_widgets.append(json_obj)

            def calc_panel_size(self, content_size, len_of_lines):
                c_w, c_h = content_size
                return c_w, c_h // len_of_lines

            def calc_panel_pos(self, panel_h, index):
                return 0, panel_h * index



# 右侧上方的工作状态panel
class RightTopPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1, mission_obj: pdctmsn.ProductMission = None,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.mission_obj = mission_obj
        self.GetParent().GetParent().register_thread(
            wThread.WorkplaceWorkingStatusThread, self, mission_obj
        )


# 右侧中间的数据结果展示panel
class RightCenterPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1, realtime_data_obj: pdctmsn.RealtimeData = None,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.realtime_data_obj = realtime_data_obj
        self.w_h_difference = None
        self.horizontal_indent = None
        self.vertical_indent = None
        self.torque_title = "扭矩（N*m)"
        self.angle_title = "角度（°）"
        self.title_font_size = None
        self.title_text_size = None
        self.torque_font_size = None
        self.angle_font_size = None

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.GetParent().GetParent().register_thread(
            wThread.WorkplaceWorkingDataThread, self, realtime_data_obj
        )

    def on_size(self, event):
        w, h = self.GetSize()

        # 水平、垂直缩进
        self.w_h_difference = math.ceil((h - w) / 30)
        self.horizontal_indent = math.ceil(w / 50)
        self.vertical_indent = math.ceil(h / 40) + self.w_h_difference

        # 扭矩标题和扭矩标题的字体大小
        self.title_font_size = int(w / 30 + h / 25) + 1
        # 绘制扭矩实时数据的字体大小
        self.torque_font_size = int(w / 27 + h / 6.3)
        # 绘制角度实时数据的字体大小
        self.angle_font_size = int(w / 50 + h / 8.5)

        super().on_size(event)
        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetSize()
        dc = wx.GCDC(wx.PaintDC(self))

        # 获取字体
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetTextForeground(configs.COLOR_TEXT_BLACK)

        # 标题的字体大小
        font_temp.SetPointSize(self.title_font_size)
        dc.SetFont(font_temp)
        self.title_text_size = dc.GetTextExtent(self.torque_title)
        title_w, title_h = self.title_text_size

        # 标题size、pos、背景颜色
        dc.SetPen(wx.Pen(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
        dc.SetBrush(wx.Brush(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
        dc.DrawRoundedRectangle(0, 0, w, title_h + self.vertical_indent * 2, 0)
        # 绘制完背景再绘制扭矩标题
        dc.DrawText(self.torque_title, self.horizontal_indent, self.vertical_indent)

        # 扭矩标题的字体大小
        # 标题size、pos、背景颜色
        dc.SetPen(wx.Pen(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
        dc.SetBrush(wx.Brush(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
        dc.DrawRoundedRectangle(0, math.ceil(h / 10 * 5.5), w, title_h + self.vertical_indent * 2, 0)
        # 绘制完背景再绘制角度标题
        dc.DrawText(self.angle_title, self.horizontal_indent, math.ceil(h / 10 * 5.5) + self.vertical_indent)

        del dc


# 右侧下方的产品面panel
class RightBottomPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1, mission_obj: pdctmsn.ProductMission = None,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.mission_obj = mission_obj
        self.indexs: list = []
        self.mission_side = None
        self.mission_side_count = None
        self.mission_side_name = None
        self.image = None
        self.bitmap = None
        self.current_page_num = None
        # 初始化参数
        self.get_variables()
        self.get_image()

        self.backward_fast = self.BitmapButton(self, bitmaps_path = PATH_ICON_BACKWARD_FAST, name = "第一个")
        self.backward = self.BitmapButton(self, bitmaps_path = PATH_ICON_BACKWARD, name = "上一个")
        self.forward = self.BitmapButton(self, bitmaps_path = PATH_ICON_FORWARD, name = "下一个")
        self.forward_fast = self.BitmapButton(self, bitmaps_path = PATH_ICON_FORWARD_FAST, name = "最后一个")

        self.backward_fast.Bind(wx.EVT_LEFT_DOWN, self.backward_fast_on_left_down)
        self.backward.Bind(wx.EVT_LEFT_DOWN, self.backward_on_left_down)
        self.forward.Bind(wx.EVT_LEFT_DOWN, self.forward_on_left_down)
        self.forward_fast.Bind(wx.EVT_LEFT_DOWN, self.forward_fast_on_left_down)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def get_variables(self):
        self.indexs = self.mission_obj.GetMissionIndexs()
        self.mission_side = self.mission_obj.GetMissionProductSides()[self.indexs[0]]
        self.mission_side_count = len(self.mission_obj.GetMissionProductSides())
        self.mission_side_name = self.mission_side.GetSideName()
        self.current_page_num = self.indexs[0] + 1

    def get_image(self):
        self.image = CommonUtils.PILImageToWxImage(self.mission_side.GetSideImage().GetImageOriginal())

    def backward_fast_on_left_down(self, event):
        indexs_new = self.indexs.copy()
        indexs_new[0] = 0
        self.mission_obj.SetMissionIndexs(indexs_new)
        self.refresh_Middle_Bottom_panel(indexs_new[0] != self.indexs[0])
        event.Skip()

    def backward_on_left_down(self, event):
        indexs_new = self.indexs.copy()
        indexs_new[0] -= 1
        if indexs_new[0] < 0:
            indexs_new[0] = 0
        self.mission_obj.SetMissionIndexs(indexs_new)
        self.refresh_Middle_Bottom_panel(indexs_new[0] != self.indexs[0])
        event.Skip()

    def forward_on_left_down(self, event):
        indexs_new = self.indexs.copy()
        indexs_new[0] += 1
        if indexs_new[0] + 1 > self.mission_side_count:
            indexs_new[0] = self.mission_side_count - 1
        self.mission_obj.SetMissionIndexs(indexs_new)
        self.refresh_Middle_Bottom_panel(indexs_new[0] != self.indexs[0])
        event.Skip()

    def forward_fast_on_left_down(self, event):
        indexs_new = self.indexs.copy()
        indexs_new[0] = self.mission_side_count - 1
        self.mission_obj.SetMissionIndexs(indexs_new)
        self.refresh_Middle_Bottom_panel(indexs_new[0] != self.indexs[0])
        event.Skip()

    def refresh_Middle_Bottom_panel(self, refresh: bool = False):
        self.get_variables()
        self.get_image()
        if refresh:
            self.GetParent().panel_middle_bottom.Refresh()
            self.Refresh()

    def on_size(self, event):
        w, h = self.GetSize()
        super().on_size(event)

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        w, h = self.GetSize()
        # 重新获取最新的参数
        self.get_variables()
        self.get_image()

        # 水平、垂直缩进
        w_h_difference = math.ceil((h - w) / 50)
        vertical_indent = math.ceil(h / 40) + w_h_difference

        # 获取字体
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        font_temp.SetPointSize(int(w / 30 + h / 25) + 1)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(self.mission_side_name)
        title_bg_h = th + vertical_indent * 2
        # 小标题size、pos、背景颜色
        dc.SetTextForeground(configs.COLOR_COMMON_WHITE)
        dc.SetPen(wx.Pen(configs.COLOR_SYSTEM_LOGO, 1))
        dc.SetBrush(wx.Brush(configs.COLOR_SYSTEM_LOGO))
        dc.DrawRoundedRectangle(0, 0, w, title_bg_h, 0)
        # 绘制完背景再绘制文字
        dc.DrawText(self.mission_side_name, math.ceil((w - tw) / 2), vertical_indent)

        # 重设产品缩略图的size和pos
        # TODO: 后续需要根据图片选定的坐标和窗口的比例进行精准的绘制图片
        top_w, top_h = self.GetTopLevelParent().GetSize()
        i_h = (h - title_bg_h) * 0.7
        i_w = i_h / (top_h / top_w)
        # i_w = w * 0.8
        # i_h = i_w / (top_w / top_h)  # 设置跟主窗体一样的长宽比例
        # 重新设置图片的尺寸
        self.image.Rescale(i_w, i_h, wx.IMAGE_QUALITY_BILINEAR)
        # 重新绘制bitmap
        self.bitmap = self.image.ConvertToBitmap()
        i_w, i_h = self.bitmap.GetSize()
        # 计算图片、按钮的间隙
        content_v_gap = math.ceil((h - i_h) / 9.5)
        i_pos = (math.ceil((w - i_w) / 2), math.ceil(title_bg_h + content_v_gap))
        dc.SetPen(wx.Pen(configs.COLOR_CONTENT_BLOCK_BORDER_2, 1))
        border_pos = (i_pos[0] - 1, i_pos[1] - 1)
        border_size = (i_w + 2, i_h + 2)
        dc.DrawRoundedRectangle(border_pos, border_size, 0)
        dc.DrawBitmap(self.bitmap, i_pos, self.bitmap.GetMask() is not None)

        # 重新计算页码显示文字的字体大小
        font_temp.SetWeight(wx.FONTWEIGHT_NORMAL)
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        font_temp.SetPointSize(int(w / 35 + h / 25) + 1)
        dc.SetTextForeground(configs.COLOR_TEXT_THEME)
        dc.SetFont(font_temp)
        page_text = str(self.current_page_num) + "/" + str(self.mission_side_count)
        tw, th = dc.GetTextExtent(page_text)
        # 按钮盒页码文字的y轴数值
        b_y = title_bg_h + i_h + content_v_gap * 2
        dc.DrawText(page_text, math.ceil((w - tw) / 2), b_y - content_v_gap / 35 - abs(w - h) / 20)
        # 重新计算按钮的size
        b_w, b_h = self.backward_fast.GetSize()
        b_h_new = h - title_bg_h - i_h - content_v_gap * 3
        b_w, b_h = CommonUtils.CalculateNewSizeWithSameRatio((b_w, b_h), b_h_new / b_h)
        # 按钮之间的gap
        w_gap = math.ceil((w / 2 - 2 * b_w - tw / 2) / 3)

        # 重设"第一个"按钮的size和pos
        self.backward_fast.SetSize(b_w, b_h)
        self.backward_fast.SetPosition((w_gap, b_y))
        # 重设"上一个"按钮的size和pos
        self.backward.SetSize(b_w, b_h)
        self.backward.SetPosition((w_gap * 2 + b_w, b_y))
        # 重设"下一个"按钮的size和pos
        self.forward.SetSize(b_w, b_h)
        self.forward.SetPosition((w_gap * 4 + b_w * 2 + tw, b_y))
        # 重设"最后一个"按钮的size和pos
        self.forward_fast.SetSize(b_w, b_h)
        self.forward_fast.SetPosition((w_gap * 5 + b_w * 3 + tw, b_y))

        # 删除DC
        del dc


    # 自定义bitmap按钮
    class BitmapButton(wx.Control):
        def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize,
                     bitmaps_path = None,
                     style = wx.BORDER_NONE, validator = wx.DefaultValidator, name = "BitmapButton"):
            wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
            self.images = []
            for bitmap_path in bitmaps_path:
                self.images.append(wx.Image(bitmap_path, wx.BITMAP_TYPE_ANY))
            self.index = 0
            self.bitmap = None

            self.is_in = False
            self.Bind(wx.EVT_PAINT, self.on_paint)
            self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
            self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
            self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
            self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_down)
            self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

        def on_paint(self, event):
            dc = wx.GCDC(wx.PaintDC(self))
            w, h = self.GetSize()
            image = self.images[self.index].Copy()
            image.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
            self.bitmap = image.ConvertToBitmap()
            dc.DrawBitmap(self.bitmap, (0, 0), self.bitmap.GetMask() is not None)
            del dc
            event.Skip()

        def on_enter(self, event):
            event_obj = event.GetEventObject()
            event_obj.SetToolTip(event_obj.GetName())
            self.index = 1
            self.is_in = True
            self.Refresh()
            event.Skip()

        def on_leave(self, event):
            self.index = 0
            self.is_in = False
            self.Refresh()
            event.Skip()

        def on_left_down(self, event):
            self.index = 2
            self.Refresh()
            event.Skip()

        def on_left_up(self, event):
            if self.is_in:
                self.index = 1
            else:
                self.index = 0
            self.Refresh()
            event.Skip()

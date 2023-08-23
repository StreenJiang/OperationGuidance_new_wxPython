import wx
import math

from src.main import configs, widgets
from src.main.controllers import apis
from src.main.models import Device as dvs
from src.main.utils import CommonUtils, CacheUtil
from src.main.enums.Cache import CacheEnum as cache

# 返回按钮的TEXT
BACK_BUTTON_TEXT = "返回"
# 条码框的扫码icon图片存储路径
PATH_BAR_CODE_ICON = "configs/icons/bar_code_icon.png"


class WorkplaceView(wx.Panel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0,
                 name = "WorkplaceView", title = "WorkplaceView", mission_obj = None):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.top_parent = CommonUtils.GetTopParent(self)
        self.title = title
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

        self.devices = None
        self.devices_changed = False

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


        # self.top_menu_bar_panel = wx.Panel(self, wx.ID_ANY)
        # self.top_menu_bar_panel.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
        # # 窗体拖动逻辑
        # self.top_menu_bar_panel.mouse_pos = None  # 初始化鼠标定位参数
        # self.bind_dragging_event(self.top_menu_bar_panel)
        # # 设置顶部菜单条大小和位置
        # bar_size, bar_pos = self.calc_menu_bar()
        # self.top_menu_bar_panel.SetSize(bar_size)
        # self.top_menu_bar_panel.SetPosition(bar_pos)
        # # 添加顶部菜单条panel子组件
        # self.add_top_menu_bar_child_widgets()
        #
        # # 添加一个灰色框框的内容主体panel
        # self.content_panel = ContentPanel(self, wx.ID_ANY, border_thickness = 1, border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        # self.content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)
        # # 设置内容主体panel大小和位置
        # pan_size, pan_pos = self.calc_content_panel()
        # self.content_panel.SetSize(pan_size)
        # self.content_panel.SetPosition(pan_pos)
        # # 添加下方内容主体panel及其子组件
        # self.add_content_panel_child_widgets()
        #
        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.top_parent.Bind(wx.EVT_SIZE, self.main_frame_resizing)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # 刷新布局
        self.Layout()

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
        mission_image = self.mission_obj.GetMissionProductSides()[0].GetSideImage().GetImageOriginal()
        mission_image = CommonUtils.PILImageToWxImage(mission_image).ConvertToBitmap()
        self.product_image_panel = self.content_panel.add_middle_bottom(mission_image)

        self.progress_status_panel = self.content_panel.add_right_top()

        self.progress_result_data_panel = self.content_panel.add_right_center()

        self.product_sides_panel = self.content_panel.add_right_bottom()

    # 获取缓存数据 - 设备列表
    def get_devices(self):
        # 初始化“数据是否有变化”变量
        self.devices_changed = False

        # 从缓存中读取数据
        devices = CacheUtil.Get(cache.DEVICES.value["key"])

        # 如果缓存中的数据为空，则重新调用API查询数据
        if devices is None:
            # 调用后端API获取数据
            devices = apis.API_GET_DEVICES(self)
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
        if not self.is_resizing:
            self.is_resizing = True
            self.Freeze()
            wx.CallLater(100, self.resize_after)
            event.Skip()

    def resize_after(self):
        print("workplace -> Resizing frame, Resolution: ", self.top_parent.GetClientSize())
        self.SetSize(self.top_parent.GetClientSize())
        self.Thaw()
        self.is_resizing = False

    def on_size(self, event):
        # 设置顶部菜单条大小和位置
        self.top_menu_bar_panel.SetSize(self.GetSize())
        event.Skip()

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
        self.panel_middle_top.set_icon(wx.Image(PATH_BAR_CODE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap())
        self.panel_middle_top.add_text_control("点击或扫描录入条码信息")
        return self.panel_middle_top

    def add_middle_bottom(self, bitmap):
        self.panel_middle_bottom = MiddleBottomPanel(parent = self)
        self.panel_middle_bottom.set_product_image(bitmap)
        return self.panel_middle_bottom

    def add_right_top(self):
        self.panel_right_top = RightTopPanel(parent = self)
        return self.panel_right_top

    def add_right_center(self):
        self.panel_right_center = RightCenterPanel(parent = self)
        return self.panel_right_center

    def add_right_bottom(self):
        self.panel_right_bottom = RightBottomPanel(parent = self)
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

    def set_devices(self, devices):
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
            self.devices = []
            self.data_changed = False
            self.icons = None
            self.icon_bitmap = None
            self.detail_panel = None

            self.enter_color = configs.COLOR_DEVICE_BUTTON_HOVER
            self.background_color = self.GetParent().GetBackgroundColour()
            self.leave_color = self.background_color
            self.is_activated = False
            self.activated_color = configs.COLOR_DEVICE_BUTTON_ACTIVATED
            self.clicked_color = configs.COLOR_DEVICE_BUTTON_CLICKED

            self.Bind(wx.EVT_SIZE, self.on_size)
            self.Bind(wx.EVT_PAINT, self.on_paint)
            # 绑定事件，实现鼠标悬浮时改变背景颜色效果，移出时恢复原背景颜色（针对激活与否有不同的效果）
            self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
            self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
            self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
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

        def add_device(self, device):
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
                self.detail_panel = self.DeviceBlockDetail(self, configs.COLOR_DEVICE_BUTTON_ACTIVATED,
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

            dp_w = w * 5
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
                self.device_info_arr = []

                self.Bind(wx.EVT_SIZE, self.on_size)
                self.Bind(wx.EVT_PAINT, self.on_paint)
                self.Bind(wx.EVT_SHOW, self.on_show)

            def on_show(self, event):
                self.GetParent().GetEventHandler().ProcessEvent(event)

            def on_size(self, event):
                # 计算自身size和pos（在逻辑上的父panel计算过了（实际上的父panel是DeviceBlock的父panel）)
                event.Skip()

            def on_paint(self, event):
                if self.device_info_arr:
                    dc = wx.GCDC(wx.PaintDC(self))
                    w, h = self.GetSize()

                    # 设置画笔、画刷的颜色
                    pen = wx.Pen(self.border_color, 1)
                    dc.SetPen(pen)
                    brush = wx.Brush(self.background_color)
                    dc.SetBrush(brush)

                    # 画出bitmap的形状
                    dc.DrawRoundedRectangle(0, 0, w, h, 0)

                    info_len = len(self.device_info_arr)
                    if info_len > 0:
                        h_info = math.ceil(h / info_len)
                        h_gap = 0
                        for index in range(info_len):
                            info = self.device_info_arr[index]

                            # 重设device信息的font_size
                            device_info = info["ip"] + "-" + str(info["port"])
                            dc.SetTextForeground(configs.COLOR_TEXT_BLACK)
                            font_temp = self.GetFont()
                            font_temp.SetPointSize(self.calc_font_size(w, h_info))
                            dc.SetFont(font_temp)
                            tw, th = dc.GetTextExtent(device_info)

                            # 重设icon的size
                            image = wx.Image(info["status_const"]["icon"], wx.BITMAP_TYPE_ANY)
                            # 计算icon的size和pos
                            bw, bh = self.calc_icon(w, h_info, image.GetSize())
                            # 重新设置图片的尺寸
                            image.Rescale(bw, bh, wx.IMAGE_QUALITY_HIGH)
                            # 重新绘制bitmap
                            bitmap = wx.Bitmap(image)

                            # 计算并重设图片和文字的pos
                            # 图标左侧的缩进
                            w_indent = math.ceil(w / 40)
                            # 如果有多个设备，则每个设备之间信息显示的gap
                            h_gap = math.ceil((h_info - bh) / 2)
                            b_x = math.ceil((w - tw - bw - w_indent) / 4)
                            b_y = math.ceil((h_info - bh) / 2) + (h_info - h_gap) * index
                            dc.DrawBitmap(bitmap, (b_x, b_y), bitmap.GetMask() is not None)
                            t_x = b_x + bw + w_indent
                            t_y = math.ceil((h_info - th) / 2 - math.ceil(th / 20)) + (h_info - h_gap) * index
                            dc.DrawText(device_info, (t_x, t_y))

                        # 将多余的高度去掉
                        self.SetSize(w, h - h_gap * (info_len - 1))

                    # 删除DC
                    del dc

            def add_device_info(self, device):
                self.device_info_arr.append({
                    "id": device.GetId(),
                    "ip": device.GetDeviceIp(),
                    "port": device.GetDevicePort(),
                    "status_const": device.GetDeviceStatus()
                })

            def set_device_info(self, index, device):
                self.device_info_arr[index] = {
                    "id": device.GetId(),
                    "ip": device.GetDeviceIp(),
                    "port": device.GetDevicePort(),
                    "status_const": device.GetDeviceStatus()
                }

            def count_device_info(self):
                return len(self.device_info_arr)

            def calc_font_size(self, w, h):
                return math.floor(math.ceil(h / 3.8))

            def calc_icon(self, w, h, image_size):
                i_w, i_h = image_size
                i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), w * 0.1 / i_w)
                return i_w, i_h



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
        self.text_control = None
        self.default_value = None
        self.Bind(wx.EVT_PAINT, self.on_paint)

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

    def add_text_control(self, default_value):
        self.default_value = default_value
        self.text_control = wx.TextCtrl(self, value = default_value,
                                        style = wx.BORDER_NONE)
        self.text_control.SetForegroundColour(configs.COLOR_TEXT_CONTROL_FONT)
        self.text_control.SetBackgroundColour(configs.COLOR_TEXT_CONTROL_BACKGROUND)

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


# 中间下方的产品展示、工作流程panel
class MiddleBottomPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.product_bitmap = None
        self.bolts = []
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        # 计算自身size和pos（在父panel计算过了)
        super().on_size(event)

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))

        # 重设产品图片的size和pos
        if self.product_bitmap is not None:
            image = self.product_bitmap.ConvertToImage()
            # 计算logo的size和pos
            i_size, i_pos = self.calc_product_image(image.GetSize())
            # 重新设置图片的尺寸
            image.Rescale(i_size[0], i_size[1], wx.IMAGE_QUALITY_BILINEAR)
            # 重新绘制bitmap
            bitmap = wx.Bitmap(image)
            dc.DrawBitmap(bitmap, i_pos, bitmap.GetMask() is not None)

        # 删除DC
        del dc

    def set_product_image(self, bitmap):
        self.product_bitmap = bitmap

    def calc_product_image(self, image_size):
        w, h = self.GetSize()
        # 以高为基准，高一定保持与panel一致（填满），因为没有任何屏幕是高比宽长的除非屏幕竖起来
        # i_w, i_h = image_size
        # ratio = h / i_h
        # if i_h > i_w:
        #     ratio = w / i_w
        # i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), ratio)
        return (w, h), (0, 0)


# 右侧上方的工作状态panel
class RightTopPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.product_image = None
        self.bolts = []


# 右侧中间的数据结果展示panel
class RightCenterPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.product_image = None
        self.bolts = []


# 右侧下方的产品面panel
class RightBottomPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.product_image = None
        self.bolts = []

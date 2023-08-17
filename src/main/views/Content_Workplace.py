import math

import wx

from src.main import configs, widgets
from src.main.models.Device import Device
from src.main.utils import CommonUtils

# 返回按钮的TEXT
BACK_BUTTON_TEXT = "返回"
# 条码框的扫码icon图片存储路径
PATH_BAR_CODE_ICON = "configs/icons/bar_code_icon.png"
# 各种设备的icon图片存储路径
PATH_ARM_ICON = ""


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
        self.logo_img = self.top_menu_bar_panel.add_logo(wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY).ConvertToBitmap())
        # 绑定事件
        self.bind_dragging_event(self.logo_img)

    def set_up_content_panel(self):
        # 添加设备panel
        self.devices_panel = self.content_panel.add_left()

        self.bar_code_panel = self.content_panel.add_middle_top()

        # 添加产品图片panel
        mission_image = self.mission_obj.GetMissionProductSides()[0].GetSideImage().GetImageOriginal()
        mission_image = CommonUtils.PILImageToWxImage(mission_image).ConvertToBitmap()
        self.product_image_panel = self.content_panel.add_middle_bottom(mission_image)

        self.progress_status_panel = self.content_panel.add_right_top()

        self.progress_result_data_panel = self.content_panel.add_right_center()

        self.product_sides_panel = self.content_panel.add_right_bottom()

    # 给下方内容主体panel添加子组件
    def add_content_panel_child_widgets(self):
        content_panel_sizer = self.content_panel.inner_sizer
        content_panel_inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_panel_sizer.Add(content_panel_inner_sizer, 1, flag = wx.EXPAND | wx.ALL, border = self.content_panel.margin * 2)

        # 设备
        self.devices = widgets.CustomBorderPanel(self.content_panel, wx.ID_ANY, border_thickness = 1,
                                                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        content_panel_inner_sizer.Add(self.devices, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = self.content_panel.margin)

        # 条码框+产品图片的sizer
        middle_v_box = wx.BoxSizer(wx.VERTICAL)
        content_panel_inner_sizer.Add(middle_v_box, proportion = 15, flag = wx.EXPAND | wx.RIGHT, border = self.content_panel.margin)
        # 条码框
        self.bar_code_text_control = widgets.CustomBorderPanel(self.content_panel, wx.ID_ANY, border_thickness = 1,
                                                               border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        middle_v_box.Add(self.bar_code_text_control, proportion = 1, flag = wx.EXPAND | wx.BOTTOM, border = self.content_panel.margin)
        # 为条码框创建输入框
        bar_code_text = wx.TextCtrl(self.bar_code_text_control, wx.ID_ANY, value = "请扫描产品条码")
        bar_code_text_font = bar_code_text.GetFont()
        bar_code_text_font.SetWeight(wx.FONTWEIGHT_BOLD)
        bar_code_text.SetFont(bar_code_text_font)
        # 将输入框加到条码框组件的sizer里
        self.bar_code_text_control.inner_sizer.Add(bar_code_text, proportion = 20, flag = wx.EXPAND | wx.ALL, border = 1)
        # 为条码框创建扫码小图标
        bar_code_icon_img = wx.Image(PATH_BAR_CODE_ICON, wx.BITMAP_TYPE_ANY)
        # bar_code_icon = CustomBitmapPanel(self.bar_code_text_control, wx.ID_ANY, size = wx.DefaultSize, image = bar_code_icon_img, style = wx.TRANSPARENT_WINDOW)
        # # 将扫码小图标加到条码框组件的sizer里
        # self.bar_code_text_control.inner_sizer.Insert(0, bar_code_icon, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 1)
        # # 将子组件存到父组件上
        # self.bar_code_text_control.bar_code_text = bar_code_text
        # self.bar_code_text_control.bar_code_icon = bar_code_icon

        # 产品图片
        self.product_image = widgets.CustomBorderPanel(self.content_panel, wx.ID_ANY, border_thickness = 1,
                                                       border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        middle_v_box.Add(self.product_image, proportion = 15, flag = wx.EXPAND)

        # 工作状态+工作数据+产品面的size
        right_v_box = wx.BoxSizer(wx.VERTICAL)
        content_panel_inner_sizer.Add(right_v_box, proportion = 4, flag = wx.EXPAND)
        # 工作状态
        self.progress_status = widgets.CustomBorderPanel(self.content_panel, wx.ID_ANY, border_thickness = 1,
                                                         border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        right_v_box.Add(self.progress_status, proportion = 11, flag = wx.EXPAND | wx.BOTTOM, border = self.content_panel.margin)

        # 工作数据
        self.progress_result_data = widgets.CustomBorderPanel(self.content_panel, wx.ID_ANY, border_thickness = 1,
                                                              border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        right_v_box.Add(self.progress_result_data, proportion = 8, flag = wx.EXPAND | wx.BOTTOM, border = self.content_panel.margin)

        # 产品面
        self.product_sides = widgets.CustomBorderPanel(self.content_panel, wx.ID_ANY, border_thickness = 1,
                                                       border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        right_v_box.Add(self.product_sides, proportion = 7, flag = wx.EXPAND)

        # 调用Layout实时展示效果
        self.content_panel.Layout()

    # 返回按钮点击事件
    def back_button_toggled(self, event):
        self.Show(False)
        self.top_parent.show_all(True)
        event.Skip()

    # 主窗口大小变化时，所有界面元素都需要调整
    def main_frame_resizing(self, event):
        print("workplace -> Resizing frame, Resolution: ", self.top_parent.GetClientSize())
        self.SetSize(self.top_parent.GetClientSize())
        event.Skip()

    def on_size(self, event):
        # 设置顶部菜单条大小和位置
        self.top_menu_bar_panel.SetSize(self.GetSize())
        #
        # # 设置内容主体panel大小和位置
        # pan_size, pan_pos = self.calc_content_panel()
        # self.content_panel.SetSize(pan_size)
        # self.content_panel.SetPosition(pan_pos)
        #
        # self.Refresh()
        # self.top_menu_bar_panel.Layout()
        # self.content_panel.Layout()
        event.Skip()

    # 处理主体panel中的子组件之间的border
    def adjust_children_size(self, content_panel_margin):
        content_panel_sizer = self.content_panel.inner_sizer
        # 内部sizer
        inner_item = content_panel_sizer.GetChildren()[0]
        inner_item.SetBorder(content_panel_margin * 2)
        inner_sizer = inner_item.GetSizer()
        # 设备组件
        devices_item = inner_sizer.GetChildren()[0]
        devices_item.SetBorder(content_panel_margin)
        # 条码框+产品面的sizer
        vbox_1 = inner_sizer.GetChildren()[1]
        vbox_1.SetBorder(content_panel_margin)
        vbox_1_sizer = vbox_1.GetSizer()
        # 条码框组件
        bar_code_item = vbox_1_sizer.GetChildren()[0]
        bar_code_item.SetBorder(content_panel_margin)
        # 工作状态+工作数据+产品面的sizer
        vbox_2_sizer = inner_sizer.GetChildren()[2].GetSizer()
        # 工作状态组件
        progress_status_item = vbox_2_sizer.GetChildren()[0]
        progress_status_item.SetBorder(content_panel_margin)
        # 工作数据组件
        progress_data_item = vbox_2_sizer.GetChildren()[1]
        progress_data_item.SetBorder(content_panel_margin)
        # 重新Layout
        self.content_panel.Layout()

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
        self.logo_static_bitmap = None
        self.Bind(wx.EVT_SIZE, self.on_size)

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

        # 重设logo的size和pos
        if self.logo_bitmap is not None:
            image = self.logo_bitmap.ConvertToImage()
            # 计算logo的size和pos
            i_size, i_pos = self.calc_logo(image.GetSize())
            # 重新设置图片的尺寸
            image.Rescale(i_size[0], i_size[1], wx.IMAGE_QUALITY_BILINEAR)
            # 重新设置bitmap
            self.logo_static_bitmap.SetBitmap(wx.Bitmap(image))
            # 重新设置pos
            self.logo_static_bitmap.SetPosition(i_pos)

        self.Refresh()
        event.Skip()

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
        self.menu_title.SetForegroundColour(configs.COLOR_MAIN_MENU_TEXT)
        return self.menu_title

    def add_logo(self, bitmap):
        self.logo_bitmap = bitmap
        self.logo_static_bitmap = wx.StaticBitmap(self, wx.ID_ANY)
        return self.logo_static_bitmap

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
        l_w, l_h = image_size
        l_w, l_h = CommonUtils.CalculateNewSizeWithSameRatio((l_w, l_h), h * 0.7 / l_h)
        return (l_w, l_h), (w - l_w - math.ceil(w / 300), math.ceil((h - l_h) / 2))


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

    def on_size(self, event):
        print("ContentPanel: ", self.GetParent().GetSize())
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

    def add_left(self):
        self.panel_left = LeftPanel(parent = self)
        return self.panel_left

    def add_middle_top(self):
        self.panel_middle_top = MiddleTopPanel(parent = self)
        return self.panel_middle_top

    def add_middle_bottom(self, bitmap):
        self.panel_middle_bottom = MiddleBottomPanel(parent = self)
        self.panel_middle_bottom.add_product_image(bitmap)
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
        self.devices = []

    def on_size(self, event):
        # 计算自身size和pos（在父panel计算过了)
        # 重设设备的size和pos
        for index in range(len(self.devices)):
            device = self.devices[index]
            # 计算当前设备的size和pos
            d_size, d_pos = self.calc_device(index)
            device.SetSize(d_size)
            device.SetPostion(d_pos)

        super().on_size(event)

    def add_device(self, id, device_name, device_category, device_type, device_ip, device_port, bitmap):
        device = self.DeviceBlock(parent = self)
        device.set_device(id, device_name, device_category, device_type, device_ip, device_port)
        device.add_icon(bitmap)
        device.add_status_panel()
        self.devices.append(device)
        return device

    def calc_device(self, index):
        w, h = self.GetSize()
        d_w = d_h = w
        d_x = 0
        d_y = index * d_h
        return (d_w, d_h), (d_x, d_y)

    # 设备组件
    class DeviceBlock(wx.Panel):
        def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                     size = wx.DefaultSize, style = 0, name = "Device"):
            wx.Panel.__init__(self, parent, id, pos = pos, size = size, style = style, name = name)
            self.device = None
            self.icon_bitmap = None
            self.icon_static_bitmap = None
            self.status_panel = None
            self.Bind(wx.EVT_SIZE, self.on_size)

        def on_size(self, event):
            # 计算自身size和pos（在父panel计算过了)
            # 重设icon的size和pos
            if self.icon_bitmap is not None:
                image = self.icon_bitmap.ConvertToImage()
                # 计算icon的size和pos
                i_size, i_pos = self.calc_icon(image.GetSize())
                # 重新设置图片的尺寸
                image.Rescale(i_size[0], i_size[1], wx.IMAGE_QUALITY_BILINEAR)
                # 重新设置bitmap
                self.icon_static_bitmap.SetBitmap(wx.Bitmap(image))
                # 重新设置pos
                self.icon_static_bitmap.SetPosition(i_pos)

            event.Skip()

        def set_device(self, id, device_name, device_category, device_type, device_ip, device_port):
            self.device = Device(id, device_name, device_category, device_type, device_ip, device_port)

        def add_icon(self, bitmap):
            self.icon_bitmap = bitmap
            self.icon_static_bitmap = wx.StaticBitmap(self, wx.ID_ANY)

        def add_status_panel(self):
            pass

        def calc_icon(self, image_size):
            return (0, 0), (0, 0)

        def calc_status_panel(self):
            return (0, 0), (0, 0)


# 中间上方的扫码panel
class MiddleTopPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.text_control = None
        self.icon_bitmap = None
        self.icon_static_bitmap = None

    def on_size(self, event):
        # 计算自身size和pos（在父panel计算过了)


        super().on_size(event)

    def add_text_control(self, default_value):
        self.text_control = wx.TextCtrl(self, value = default_value)




# 中间下方的产品展示、工作流程panel
class MiddleBottomPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)
        self.product_bitmap = None
        self.product_static_bitmap = None
        self.bolts = []

    def on_size(self, event):
        # 计算自身size和pos（在父panel计算过了)

        # 重设产品图片的size和pos
        if self.product_bitmap is not None:
            image = self.product_bitmap.ConvertToImage()
            # 计算logo的size和pos
            i_size, i_pos = self.calc_product_image(image.GetSize())
            # 重新设置图片的尺寸
            image.Rescale(i_size[0], i_size[1], wx.IMAGE_QUALITY_BILINEAR)
            # 重新设置bitmap
            self.product_static_bitmap.SetBitmap(wx.Bitmap(image))
            # 重新设置pos
            self.product_static_bitmap.SetPosition(i_pos)

        super().on_size(event)

    def add_product_image(self, bitmap):
        self.product_bitmap = bitmap
        self.product_static_bitmap = wx.StaticBitmap(self, wx.ID_ANY)

    def calc_product_image(self, image_size):
        w, h = self.GetSize()
        # 以高为基准，高一定保持与panel一致（填满），因为没有任何屏幕是高比宽长的除非屏幕竖起来
        # l_w, l_h = image_size
        # ratio = h / l_h
        # if l_h > l_w:
        #     ratio = w / l_w
        # l_w, l_h = CommonUtils.CalculateNewSizeWithSameRatio((l_w, l_h), ratio)
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


# 自定义Panel，这个只显示一个会根据Panel大小和比例参数，自适应改变大小并显示在正中央的bitmap图片
class CustomBitmapPanel(wx.Panel):
    def __init__(self, parent, id,
                 image = wx.Image(),                # 这个是wx.Image对象
                 image_ratio = 90,                  # 这个是图片大小的比例，单位%
                 pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "CustomBitmapPanel"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        # bitmap的parent采用跟当前对象的parent同一个，是为了避免bitmap改变大小时会影响到其parent的大小
        # 测试发现bitmap改变大小时，parent的大小如果小于bitmap的尺寸，好像是会跟着变大的
        self.image_ratio = image_ratio
        self.logo_img_png = image
        self.logo_img_static = wx.StaticBitmap(self, wx.ID_ANY, self.logo_img_png.ConvertToBitmap())

        # 添加一个sizer让图片右对齐
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.logo_img_static, 1, wx.ALL | wx.ALIGN_CENTRE, border = 5)
        self.SetSizer(self.sizer)
        self.Layout()

        # 绑定on_size事件
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.logo_img_static.Bind(wx.EVT_MOTION, self.process_parent_event)
        self.logo_img_static.Bind(wx.EVT_LEFT_DOWN, self.process_parent_event)
        self.logo_img_static.Bind(wx.EVT_LEFT_UP, self.process_parent_event)

    # 调用父类对应的事件（因为这个组件其实是真正的自定义组件（一个panel假装的）的内部组件，
    # 正常情况下会在父组件的上方，因此事件触发基本上都是触发此对象，而实际代码逻辑中绑定时都是绑定父对象，因此要向上传递
    def process_parent_event(self, event):
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)
        event.Skip()

    def on_size(self, event):
        print("test 1111111111111111111 self.GetParent().GetSize(): ", self.GetParent().GetSize())
        # 复制一个wx.Image，以免多次Rescale导致图片失真
        log_temp = self.logo_img_png.Copy()

        # 重新根据当前父panel的size计算新的图片size及图片右边的border
        p_width, p_height = self.GetParent().GetSize()
        logo_img_width, logo_img_height, border = self.calc_img_size(p_height)
        log_temp.Rescale(logo_img_width, logo_img_height, wx.IMAGE_QUALITY_BILINEAR)
        self.SetSize(p_height, p_height)

        # 设置新的bitmap
        self.logo_img_static.SetBitmap(log_temp.ConvertToBitmap())
        # 设定新的border
        self.sizer.GetChildren()[0].SetBorder(border)

        # 刷新一下布局
        self.Layout()
        event.Skip()

    # 重新根据当前父panel的size计算新的图片size及图片右边的border
    def calc_img_size(self, p_height):
        img_size = self.logo_img_png.GetSize()
        width, height = CommonUtils.CalculateNewSizeWithSameRatio(img_size, p_height * (self.image_ratio / 100) / img_size[1])
        return width, height, math.floor((p_height - height) / 2)

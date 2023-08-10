import math

import wx

from src.main import configs, widgets
from src.main.utils import CommonUtils

# 返回按钮的TEXT
BACK_BUTTON_TEXT = "返回"
# 条码框的扫码icon图片存储路径
PATH_BAR_CODE_ICON = "configs/icons/bar_code_icon.png"


class WorkplaceView(wx.Panel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "WorkplaceView", title = "WorkplaceView"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.top_parent = CommonUtils.GetTopParent(self)
        self.title = title

        # 主要的两个panel，一个顶部菜单条panel、一个下面的内容主体panel
        self.top_menu_bar_panel = None
        self.content_panel = None

        # 菜单条里的组件
        self.back_button = None
        self.middle_text_panel = None
        self.logo_img_panel = None

        # 内容主体panel内的组件
        self.devices = None
        self.bar_code_text_control = None
        self.product_image = None
        self.progress_status = None
        self.progress_result_data = None
        self.product_sides = None

        # 窗体拖拽标识
        self.window_drag_flag = False

        # 顶部菜单条组件
        self.top_menu_bar_panel = wx.Panel(self, wx.ID_ANY)
        self.top_menu_bar_panel.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
        # 窗体拖动逻辑
        self.top_menu_bar_panel.mouse_pos = None  # 初始化鼠标定位参数
        self.bind_dragging_event(self.top_menu_bar_panel)
        # 设置顶部菜单条大小和位置
        bar_size, bar_pos = self.calc_menu_bar()
        self.top_menu_bar_panel.SetSize(bar_size)
        self.top_menu_bar_panel.SetPosition(bar_pos)
        # 添加顶部菜单条panel子组件
        self.add_top_menu_bar_child_widgets()

        # 添加一个灰色框框的内容主体panel
        self.content_panel = ContentPanel(self, wx.ID_ANY, border_thickness = 1, border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        self.content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)
        # 设置内容主体panel大小和位置
        pan_size, pan_pos = self.calc_content_panel()
        self.content_panel.SetSize(pan_size)
        self.content_panel.SetPosition(pan_pos)
        # 添加下方内容主体panel及其子组件
        self.add_content_panel_child_widgets()

        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.top_parent.Bind(wx.EVT_SIZE, self.main_frame_resizing)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # 刷新布局
        self.Refresh()

    # 给顶部菜单条panel添加子组件
    def add_top_menu_bar_child_widgets(self):
        # 设置sizer
        top_menu_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_menu_bar_panel.SetSizer(top_menu_bar_sizer)

        # 添加返回按钮组件
        self.back_button = BackButton(self.top_menu_bar_panel,
                                      wx.ID_ANY,
                                      label = BACK_BUTTON_TEXT,
                                      font_color = configs.COLOR_BUTTON_TEXT,
                                      background_color = configs.COLOR_BUTTON_BACKGROUND,
                                      clicked_color = configs.COLOR_BUTTON_FOCUSED,
                                      button_size_type = widgets.BUTTON_SIZE_TYPE_NORMAL,
                                      radius = 2)
        # 绑定事件
        self.back_button.Bind(wx.EVT_LEFT_UP, self.back_button_toggled)
        self.bind_dragging_event(self.back_button)
        # 设置sizer
        v_back = wx.BoxSizer(wx.VERTICAL)
        v_back.Add(self.back_button, 1, wx.ALIGN_LEFT)
        top_menu_bar_sizer.Add(v_back, 1, wx.EXPAND | wx.TOP | wx.LEFT, 3)

        # 添加菜单名称显示组件
        self.middle_text_panel = MiddleTextPanel(self.top_menu_bar_panel, wx.ID_ANY, label = self.title, style = wx.ALIGN_CENTRE_HORIZONTAL)
        # 绑定事件
        self.bind_dragging_event(self.middle_text_panel)
        # 设置sizer
        top_menu_bar_sizer.Add(self.middle_text_panel, 1, wx.EXPAND)

        # 添加logo图片（用的是MainFrame里的组件）
        self.logo_img_panel = widgets.LogoPanel(self.top_menu_bar_panel, wx.ID_ANY, image_ratio = 90)
        top_menu_bar_sizer.Add(self.logo_img_panel, 1, wx.EXPAND)

        # 刷新布局
        self.top_menu_bar_panel.Layout()

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
        if self.window_drag_flag:
            self.window_drag_flag = False
            return

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
        bar_size, bar_pos = self.calc_menu_bar()
        self.top_menu_bar_panel.SetSize(bar_size)
        self.top_menu_bar_panel.SetPosition(bar_pos)

        # 设置内容主体panel大小和位置
        pan_size, pan_pos = self.calc_content_panel()
        self.content_panel.SetSize(pan_size)
        self.content_panel.SetPosition(pan_pos)

        self.Refresh()
        self.top_menu_bar_panel.Layout()
        self.content_panel.Layout()
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
        if not self.top_parent.IsMaximized() and self.top_menu_bar_panel.mouse_pos is not None:
            if event.Dragging():
                pos_changed = event.GetPosition() - self.top_menu_bar_panel.mouse_pos
                # 判断拖动距离是否大于一定距离，如果太小则可能是点击事件，因此不重新定位，使按钮点击事件能正常触发
                if (abs(pos_changed[0]), abs(pos_changed[1])) > (2, 2):
                    self.window_drag_flag = True
                    self.top_parent.SetPosition(self.top_parent.GetPosition() + pos_changed)
        event.Skip()

    # 窗体拖拽事件 - 鼠标左键按下
    def window_dragging_mouse_l_down(self, event):
        if not self.top_parent.IsMaximized():
            self.top_menu_bar_panel.mouse_pos = event.GetPosition()
        event.Skip()

    # 窗体拖拽事件 - 鼠标左键松开
    def window_dragging_mouse_l_up(self, event):
        if not self.top_parent.IsMaximized():
            self.top_menu_bar_panel.mouse_pos = None
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


# 顶部菜单条返回按钮
class BackButton(widgets.CustomRadiusButton):
    def __init__(self, parent, id = -1, label = "", font_color = "#FFFFFF", background_color = "#000000",
                 clicked_color = "#000000", button_size_type = widgets.BUTTON_SIZE_TYPE_NORMAL, radius = 0):
        widgets.CustomRadiusButton.__init__(self, parent, id, label = label, font_color = font_color,
                                            background_color = background_color, clicked_color = clicked_color,
                                            button_size_type = button_size_type, radius = radius)
    def OnSize(self, event):
        print("BackButton: ", self.GetParent().GetSize())
        # 计算按钮大小
        p_height = self.GetParent().GetSize()[1]
        height = math.ceil(0.8 * p_height)
        width = height * 2.5
        self.SetSize(width, height)
        super().OnSize(event)


# 顶部菜单条中间文字的panel
class MiddleTextPanel(wx.Panel):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "MiddleTextPanel", label = "MiddleTextPanel"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.text = wx.StaticText(parent, id, pos = pos, size = size, label = label, style = style, name = name)
        # 设置字体颜色
        self.text.SetForegroundColour(configs.COLOR_MAIN_MENU_TEXT)
        # 绑定事件
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        print("MiddleTextPanel: ", self.GetParent().GetSize())
        # 计算字体大小
        p_width, p_height = self.GetParent().GetSize()
        size_1 = math.ceil(p_width / 70) + 2
        size_2 = math.ceil(p_height / 2 + 0.4)

        # 设置字体
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        if p_width < p_height:
            font_temp.SetPointSize(size_1)
        else:
            font_temp.SetPointSize(size_2)
        self.text.SetFont(font_temp)
        # 设置文字位置
        s_width, s_height = self.GetSize()
        x, y = self.GetPosition()
        tw, th = self.text.GetTextExtent(self.text.GetLabel())
        self.text.SetPosition((x + (s_width - tw) // 2, y + (s_height - th) // 2))
        event.Skip()


# 下方内容的外层panel
class ContentPanel(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, border_thickness = 1,
                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER, margin = 0, radius = 0):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_thickness = border_thickness,
                                           border_color = border_color, margin = margin, radius = radius)

    def on_size(self, event):
        print("ContentPanel: ", self.GetParent().GetSize())
        margin = int(self.GetParent().GetSize()[0] / 300) + 3
        self.SetMargin(margin)
        super().on_size(event)

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

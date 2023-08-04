import math

import wx

from src.main import configs, widgets
from src.main.utils import CommonUtils


# 返回按钮的TEXT
BACK_BUTTON_TEXT = "返回"
# 条码框的icon图片存储路径
PATH_BAR_CODE_ICON = "configs/icons/bar_code_icon.png"


class WorkplaceView(wx.Panel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "WorkplaceView", title = "WorkplaceView"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.top_parent = CommonUtils.GetTopParent(self)
        self.title = title
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 主要的两个panel，一个顶部菜单条panel、一个下面的内容主体panel
        self.top_menu_bar_panel = None
        self.content_panel = None

        # 菜单条里的组件
        self.back_button = None
        self.main_menu_name = None
        self.logo_img_static = None

        # 内容主体panel内的组件
        self.devices = None
        self.bar_code_text_control = None
        self.product_image = None
        self.progress_status = None
        self.progress_result_data = None
        self.product_sides = None

        # 窗体拖拽标识
        self.window_drag_flag = False

        # 添加顶部菜单条panel及其子组件
        self.add_top_menu_bar()

        # 添加下方内容主体panel及其子组件
        self.add_content_panel()

        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.top_parent.Bind(wx.EVT_SIZE, self.main_frame_resizing)

        main_sizer.Add(self.top_menu_bar_panel)
        main_sizer.Add(self.content_panel)
        # 设置sizer
        self.SetSizerAndFit(main_sizer)

    # 添加顶部菜单条及其子组件
    def add_top_menu_bar(self):
        # 顶部菜单条组件
        top_menu_bar_panel_pos, top_menu_bar_panel_size = calculate_top_menu_bar_panel_size(self.GetClientSize())
        self.top_menu_bar_panel = wx.Panel(self, wx.ID_ANY, pos = top_menu_bar_panel_pos, size = top_menu_bar_panel_size)
        self.top_menu_bar_panel.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
        # 窗体拖动逻辑
        self.top_menu_bar_panel.mouse_pos = None  # 初始化鼠标定位参数
        self.bind_dragging_event(self.top_menu_bar_panel)

        # 给顶部菜单条panel添加子组件
        self.add_top_menu_bar_child_widgets(top_menu_bar_panel_size)

    # 给顶部菜单条panel添加子组件
    def add_top_menu_bar_child_widgets(self, top_menu_bar_panel_size):
        # 添加返回按钮组件
        back_button_pos, back_button_size = calculate_top_menu_bar_button_size(top_menu_bar_panel_size)
        self.back_button = widgets.CustomRadiusButton(
            self.top_menu_bar_panel,
            wx.ID_ANY,
            label = BACK_BUTTON_TEXT,
            font_color = configs.COLOR_BUTTON_TEXT,
            background_color = configs.COLOR_BUTTON_BACKGROUND,
            clicked_color = configs.COLOR_BUTTON_FOCUSED,
            button_size_type = widgets.BUTTON_SIZE_TYPE_NORMAL,
            pos = back_button_pos,
            size = back_button_size
        )
        # 绑定返回按钮事件
        self.back_button.Bind(wx.EVT_LEFT_UP, self.back_button_toggled)
        self.bind_dragging_event(self.back_button)

        # 添加菜单名称显示组件
        self.main_menu_name = wx.StaticText(self.top_menu_bar_panel, wx.ID_ANY, label = self.title, style = wx.ALIGN_CENTRE_HORIZONTAL)
        self.main_menu_name.SetForegroundColour(configs.COLOR_MAIN_MENU_TEXT)
        font_temp = self.main_menu_name.GetFont()
        font_size = calculate_top_menu_bar_title_font_size(top_menu_bar_panel_size)
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        font_temp.SetPointSize(font_size)
        self.main_menu_name.SetFont(font_temp)
        main_menu_name_pos = calculate_top_menu_bar_title_pos(top_menu_bar_panel_size, self.main_menu_name.GetSize())
        self.main_menu_name.SetPosition(main_menu_name_pos)
        # 绑定菜单名称事件
        self.bind_dragging_event(self.main_menu_name)

        # 添加logo图片
        logo_img_png = wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY)
        logo_img_pos, logo_img_size = calculate_logo_img_size(self.top_menu_bar_panel.GetSize(),
                                                              logo_img_png.GetSize())
        logo_img_png.Rescale(logo_img_size[0], logo_img_size[1], wx.IMAGE_QUALITY_BILINEAR)
        self.logo_img_static = wx.StaticBitmap(self.top_menu_bar_panel, -1, logo_img_png.ConvertToBitmap())
        self.logo_img_static.SetPosition(logo_img_pos)
        # 绑定logo图片事件
        self.bind_dragging_event(self.logo_img_static)

    # 添加下方内容主体panel及其子组件
    def add_content_panel(self):
        # 添加一个灰色框框的内容主体panel
        content_panel_pos, content_panel_size, content_panel_margin = calculate_content_panel_size(self.GetClientSize())
        self.content_panel = widgets.CustomBorderPanel(self, wx.ID_ANY, pos = content_panel_pos, size = content_panel_size,
                                                       border_thickness = 1, border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER,
                                                       margin = content_panel_margin, radius = 0)
        self.content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)

        # 给下方内容主体panel添加子组件
        self.add_content_panel_child_widgets(self.content_panel)

    # 给下方内容主体panel添加子组件
    def add_content_panel_child_widgets(self, content_panel):
        content_panel_sizer = content_panel.GetSizer()
        content_panel_inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_panel_sizer.Add(content_panel_inner_sizer, 1, flag = wx.EXPAND | wx.ALL, border = content_panel.margin * 2)

        # 设备
        self.devices = widgets.CustomBorderPanel(content_panel, wx.ID_ANY, border_thickness = 1,
                                                 border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        content_panel_inner_sizer.Add(self.devices, proportion = 1, flag = wx.EXPAND | wx.RIGHT, border = content_panel.margin)

        # 条码框+产品图片的sizer
        middle_v_box = wx.BoxSizer(wx.VERTICAL)
        content_panel_inner_sizer.Add(middle_v_box, proportion = 15, flag = wx.EXPAND | wx.RIGHT, border = content_panel.margin)
        # 条码框
        self.bar_code_text_control = widgets.CustomBorderPanel(content_panel, wx.ID_ANY, border_thickness = 1,
                                                               border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        middle_v_box.Add(self.bar_code_text_control, proportion = 1, flag = wx.EXPAND | wx.BOTTOM, border = content_panel.margin)
        # 为条码框创建输入框
        bar_code_text = wx.TextCtrl(self.bar_code_text_control, wx.ID_ANY, value = "请扫描产品条码")
        bar_code_text_font = bar_code_text.GetFont()
        bar_code_text_font.SetWeight(wx.FONTWEIGHT_BOLD)
        bar_code_text.SetFont(bar_code_text_font)
        # 将输入框加到条码框组件的sizer里
        self.bar_code_text_control.GetSizer().Add(bar_code_text, proportion = 20, flag = wx.EXPAND | wx.ALL, border = 1)
        # 为条码框创建扫码小图标
        bar_code_icon_img = wx.Image(PATH_BAR_CODE_ICON, wx.BITMAP_TYPE_ANY)
        bar_code_icon = widgets.CustomBitmapPanel(self.bar_code_text_control, wx.ID_ANY, size = wx.DefaultSize, image = bar_code_icon_img, style = wx.TRANSPARENT_WINDOW)
        # 将扫码小图标加到条码框组件的sizer里
        self.bar_code_text_control.GetSizer().Insert(0, bar_code_icon, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 1)
        # 将子组件存到父组件上
        self.bar_code_text_control.bar_code_text = bar_code_text
        self.bar_code_text_control.bar_code_icon = bar_code_icon

        # 产品图片
        self.product_image = widgets.CustomBorderPanel(content_panel, wx.ID_ANY, border_thickness = 1,
                                                       border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        middle_v_box.Add(self.product_image, proportion = 15, flag = wx.EXPAND)

        # 工作状态+工作数据+产品面的sizer
        right_v_box = wx.BoxSizer(wx.VERTICAL)
        content_panel_inner_sizer.Add(right_v_box, proportion = 4, flag = wx.EXPAND)
        # 工作状态
        self.progress_status = widgets.CustomBorderPanel(content_panel, wx.ID_ANY, border_thickness = 1,
                                                         border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        right_v_box.Add(self.progress_status, proportion = 11, flag = wx.EXPAND | wx.BOTTOM, border = content_panel.margin)

        # 工作数据
        self.progress_result_data = widgets.CustomBorderPanel(content_panel, wx.ID_ANY, border_thickness = 1,
                                                              border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        right_v_box.Add(self.progress_result_data, proportion = 8, flag = wx.EXPAND | wx.BOTTOM, border = content_panel.margin)

        # 产品面
        self.product_sides = widgets.CustomBorderPanel(content_panel, wx.ID_ANY, border_thickness = 1,
                                                       border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
        right_v_box.Add(self.product_sides, proportion = 7, flag = wx.EXPAND)

        # 调用Layout实时展示效果
        content_panel.Layout()

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
        # 使用异步调用可以保证所有元素在画（paint）的过程中，一定在正确的位置
        if not self.is_resizing:
            print("workplace -> Resizing frame, Resolution: ", self.top_parent.GetClientSize())
            self.is_resizing = True
            wx.CallLater(200, self.resize_everything)
        event.Skip()

    # 所有组件自适应
    def resize_everything(self):
        # 顶部菜单条panel自适应大小及位置
        self.SetSize(self.top_parent.GetClientSize())
        top_menu_bar_panel_pos, top_menu_bar_panel_size = calculate_top_menu_bar_panel_size(self.GetClientSize())
        self.top_menu_bar_panel.SetSize(top_menu_bar_panel_size)

        # 返回按钮自适应大小及位置
        back_button_pos, back_button_size = calculate_top_menu_bar_button_size(top_menu_bar_panel_size)
        self.back_button.SetPosition(back_button_pos)
        self.back_button.SetSize(back_button_size)

        # 主菜单名称 - 标题 自适应大小及位置
        font_temp = self.main_menu_name.GetFont()
        font_size = calculate_top_menu_bar_title_font_size(top_menu_bar_panel_size)
        font_temp.SetPointSize(font_size)
        self.main_menu_name.SetFont(font_temp)
        main_menu_name_pos = calculate_top_menu_bar_title_pos(top_menu_bar_panel_size, self.main_menu_name.GetSize())
        self.main_menu_name.SetPosition(main_menu_name_pos)

        # logo图片自适应调整大小和位置
        logo_img_png = wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY)
        logo_img_pos, logo_img_size = calculate_logo_img_size(self.top_menu_bar_panel.GetSize(),
                                                              logo_img_png.GetSize())
        logo_img_png.Rescale(logo_img_size[0], logo_img_size[1], wx.IMAGE_QUALITY_BILINEAR)
        self.logo_img_static.SetBitmap(logo_img_png.ConvertToBitmap())
        self.logo_img_static.SetPosition(logo_img_pos)

        # 内容主体panel自适应调整大小和位置
        content_panel_pos, content_panel_size, content_panel_margin = calculate_content_panel_size(self.GetClientSize())
        self.content_panel.SetSize(content_panel_size)
        self.content_panel.SetPosition(content_panel_pos)
        self.content_panel.SetMargin(content_panel_margin)

        # 处理主体panel中的子组件之间的border
        self.adjust_children_size(content_panel_margin)

        # 刷新界面
        self.Refresh()
        # 重置标识参数
        self.is_resizing = False

    # 处理主体panel中的子组件之间的border
    def adjust_children_size(self, content_panel_margin):
        content_panel_sizer = self.content_panel.GetSizer()
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


# 计算顶部菜单条的尺寸和位置
def calculate_top_menu_bar_panel_size(panel_size):
    pos_x = 0
    pos_y = 0
    width = panel_size[0]
    height = int(panel_size[1] * 0.05)
    return (pos_x, pos_y), (width, height)

# 计算顶部菜单条返回按钮的尺寸和位置
def calculate_top_menu_bar_button_size(panel_size):
    height = int(0.8 * panel_size[1])
    width = height * 2.5
    pos_y = math.ceil((panel_size[1] - height) / 2)
    pos_x = pos_y
    return (pos_x, pos_y), (width, height)

# 计算顶部菜单条主菜单名称字体大小
def calculate_top_menu_bar_title_font_size(panel_size):
    size_1 = math.ceil(panel_size[0] / 70) + 2
    size_2 = math.ceil(panel_size[1] / 2 + 0.4)
    if panel_size[0] < panel_size[1]:
        return size_1
    return size_2

# 计算顶部菜单条主菜单名称的位置
def calculate_top_menu_bar_title_pos(panel_size, self_size):
    return int((panel_size[0] - self_size[0]) / 2), int((panel_size[1] - self_size[1]) / 2)


# 计算logo图片的尺寸和位置
def calculate_logo_img_size(panel_size, logo_img_size):
    width, height = CommonUtils.CalculateNewSizeWithSameRatio(logo_img_size, panel_size[1] * 0.8 / logo_img_size[1])
    pos_x = panel_size[0] - width - 2
    pos_y = (panel_size[1] - height) / 2
    return (pos_x, pos_y), (width, height)


# 计算内容panel的尺寸和位置
def calculate_content_panel_size(panel_size):
    pos_x = 0
    pos_y = int(panel_size[1] * 0.05)
    width = panel_size[0]
    height = panel_size[1] - int(panel_size[1] * 0.05)
    margin = int(width / 300) + 3
    return (pos_x, pos_y), (width, height), margin

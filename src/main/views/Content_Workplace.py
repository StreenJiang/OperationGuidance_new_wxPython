import wx

from src.main import configs, widgets
from src.main.utils import CommonUtils


# 返回按钮icon路径
BACK_BUTTON_TEXT = "返回"


class WorkplaceView(wx.Panel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "WorkplaceView", title = "WorkplaceView"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.top_parent = CommonUtils.GetTopParent(self)
        self.title = title
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        top_menu_bar_panel_pos, top_menu_bar_panel_size = calculate_top_menu_bar_panel_size(self.GetClientSize())
        self.top_menu_bar_panel = wx.Panel(self, wx.ID_ANY, pos = top_menu_bar_panel_pos, size = top_menu_bar_panel_size)
        self.top_menu_bar_panel.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)

        back_button_pos, back_button_size = calculate_top_menu_bar_button_size(top_menu_bar_panel_size)
        print(back_button_size)
        self.back_button = widgets.CustomRadiusButton(
            self.top_menu_bar_panel,
            wx.ID_ANY,
            label = BACK_BUTTON_TEXT,
            font_color = configs.COLOR_BUTTON_TEXT,
            background_color = configs.COLOR_BUTTON_BACKGROUND,
            clicked_color = configs.COLOR_BUTTON_FOCUSED,
            pos = back_button_pos,
            size = back_button_size
        )
        font_temp = self.back_button.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        font_temp.SetPointSize(int(back_button_size[0] / 12 + back_button_size[1] / 5) + 1)
        self.back_button.set_custom_font(font_temp)

        # 绑定事件
        # self.back_button.Bind(wx.EVT_LEFT_UP, self.top_menu_bar_toggled)
        self.back_button.Bind(wx.EVT_MOTION, self.window_dragging)
        self.back_button.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
        self.back_button.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)


        main_sizer.Add(self.top_menu_bar_panel)
        # 设置sizer
        self.SetSizerAndFit(main_sizer)

        # 窗体拖动逻辑
        self.top_menu_bar_panel.mouse_pos = None  # 初始化鼠标定位参数
        self.window_drag_flag = False
        self.Bind(wx.EVT_MOTION, self.window_dragging)
        self.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
        self.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)

    # 窗体拖拽事件 - 重新定位窗体位置
    def window_dragging(self, event):
        if not self.top_parent.IsMaximized() and self.top_menu_bar_panel.mouse_pos is not None:
            if event.Dragging():
                pos_changed = event.GetPosition() - self.top_menu_bar_panel.mouse_pos
                # 判断拖动距离是否大于一定距离，如果太小则可能是点击事件，因此不重新定位，使按钮点击事件能正常触发
                if (abs(pos_changed[0]), abs(pos_changed[1])) > (1, 1):
                    self.window_drag_flag = True
                    self.top_parent.SetPosition(self.GetPosition() + pos_changed)
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

# 计算工作台panel的尺寸和位置
def calculate_top_menu_bar_panel_size(panel_size):
    pos_x = 0
    pos_y = 0
    width = panel_size[0]
    height = int(panel_size[1] * 0.05)
    return (pos_x, pos_y), (width, height)

# 计算工作台菜单按钮的尺寸和位置
def calculate_top_menu_bar_button_size(parent_panel_size):
    height = int(0.8 * parent_panel_size[1])
    width = height * 3
    pos_x = int(0.002 * parent_panel_size[0])
    pos_y = int((parent_panel_size[1] - height) / 2)
    return (pos_x, pos_y), (width, height)

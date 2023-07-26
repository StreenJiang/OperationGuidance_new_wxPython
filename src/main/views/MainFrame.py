import wx

from src.main import widgets
from src.main.configs import SystemConfigs
from src.main.controllers import call_api


# 主窗体类
class MainFrame(wx.Frame):
    def __init__(self, parent = None, id = None, variables = None):
        wx.Frame.__init__(self, parent = parent, id = id, style = wx.DEFAULT_FRAME_STYLE)
        # 系统参数
        self.sys_variables = variables

        # 根据参数配置修改窗体属性
        self.SetSize(self.sys_variables["sys_config"]["SIZE_MAIN_FRAME_DEFAULT"])
        self.SetMinSize(self.sys_variables["sys_config"]["SIZE_MAIN_FRAME_MINIMUM"])

        # 状态参数
        self.current_main_menu = None
        self.current_child_menu = None
        self.main_menus = []

        # 设置系统最底层背景颜色（这里按应该用一些本地配置文件里的参数，因为这些参数通过用户修改是可以持久化到本地的）
        self.SetBackgroundColour(SystemConfigs.COLOR_SYSTEM_BACKGROUND)

        # 给主窗口设置主布局sizer - 垂直线性布局
        #   共有2个子布局，分别是上方主菜单，下方主界面
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 主窗口panel
        self.main_panel = wx.Panel(self, wx.ID_ANY, pos = (0, 0), size = self.GetSize())

        # 主菜单panel
        main_menu_panel_pos, main_menu_panel_size = calculate_main_menu_panel_size(self.GetSize())
        self.main_menu_panel = wx.Panel(self.main_panel, wx.ID_ANY, pos = main_menu_panel_pos, size = main_menu_panel_size)
        self.main_menu_panel.SetBackgroundColour(SystemConfigs.COLOR_MENU_BACKGROUND)

        # 窗体拖动逻辑
        self.main_menu_panel.mouse_pos = None # 初始化鼠标定位参数
        self.window_drag_flag = False
        self.main_menu_panel.Bind(wx.EVT_MOTION, self.window_dragging)
        self.main_menu_panel.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
        self.main_menu_panel.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)

        # 子菜单panel
        self.child_menu_panel = None

        # 添加主菜单
        self.add_main_menus()

        # 添加logo
        self.logo_img_png = wx.Image("configs/icons/logo.png")
        logo_img_pos, logo_img_size = calculate_logo_img_size(self.main_menu_panel.GetSize(), self.logo_img_png.GetSize())
        self.logo_img_png.Rescale(logo_img_size[0], logo_img_size[1], wx.IMAGE_QUALITY_HIGH)
        self.logo_img_static = wx.StaticBitmap(self.main_menu_panel, -1, self.logo_img_png.ConvertToBitmap())
        self.logo_img_static.SetPosition(logo_img_pos)

        # 添加到主sizer
        main_sizer.Add(self.main_menu_panel)
        if self.current_main_menu is not None:
            main_sizer.Add(self.current_main_menu.content_panel)

        # 设置主sizer
        self.main_panel.SetSizer(main_sizer)

        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.Bind(wx.EVT_SIZE, self.main_frame_resizing)


    # 添加主菜单
    def add_main_menus(self):
        index = 0
        for menu_config in SystemConfigs.main_menus_config:
            if menu_config["enabled"] and menu_config["id"] in self.sys_variables["license_data"]["MAIN_MENU_LIST"]:
                main_menu_panel_pos, main_menu_panel_size = calculate_main_menu_button_size(self.GetSize(), index)
                btn_temp = widgets.CustomGenBitmapTextToggleButton(
                    self.main_menu_panel,
                    wx.ID_ANY,
                    wx.Image(menu_config["icon"]).ConvertToBitmap(),
                    label = menu_config["name"],
                    custom_style = widgets.BUTTON_STYLE_VERTICAL,
                    background_color = SystemConfigs.COLOR_MENU_BUTTON_BACKGROUND,
                    pos = main_menu_panel_pos,
                    size = main_menu_panel_size
                )

                # 绑定事件
                btn_temp.Bind(wx.EVT_BUTTON, self.main_menu_toggled)
                btn_temp.Bind(wx.EVT_MOUSE_EVENTS, self.window_dragging)
                btn_temp.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
                btn_temp.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)

                # 将后续需要用的配置信息存到对象上
                btn_temp.bgColor = SystemConfigs.COLOR_MENU_BUTTON_BACKGROUND
                btn_temp.toggledColor = SystemConfigs.COLOR_MENU_BUTTON_TOGGLE
                btn_temp.events = menu_config["events"]
                btn_temp.childrenMenus = menu_config["children"]

                # 将每个菜单的内容页容器绑定到菜单按钮上
                content_panel_pos, content_panel_size = calculate_content_panel_size(self.GetSize(), len(btn_temp.childrenMenus) > 0)
                btn_temp.content_panel = wx.Panel(self.main_panel, wx.ID_ANY, pos = content_panel_pos, size = content_panel_size)
                btn_temp.content_panel.SetBackgroundColour(SystemConfigs.COLOR_CONTENT_PANEL_BACKGROUND)

                # 初始化子菜单
                btn_temp.child_menu_panel = None
                btn_temp.child_menus = []

                # 将主菜单的子菜单添加到子菜单panel中
                self.add_child_menus(btn_temp)

                # 如果是第一个按钮，则程序启动时默认是触发状态
                if index == 0:
                    self.current_main_menu = btn_temp
                    btn_temp.SetToggle(True)
                    btn_temp.SetBackgroundColour(btn_temp.toggledColor)

                    # 展示当前的内容页
                    btn_temp.content_panel.Show(True)

                    # 当前第一个按钮默认触发
                    if len(btn_temp.child_menus) > 0:
                        btn_temp.child_menu_panel.Show(True)
                        self.current_child_menu = btn_temp.child_menus[0]
                        self.current_child_menu.SetToggle(True)
                        self.current_child_menu.SetBackgroundColour(self.current_child_menu.toggledColor)
                else:
                    btn_temp.content_panel.Show(False)

                # 将按钮对象加入到list中以方便后续操作
                self.main_menus.append(btn_temp)
                index += 1



    # 添加子菜单（如果有的话）
    def add_child_menus(self, main_menu_btn):
        child_menus_arr = main_menu_btn.childrenMenus

        # 如果指定主菜单有子菜单配置的话
        if len(child_menus_arr) > 0:
            child_menu_panel_pos, child_menu_panel_size = calculate_child_menu_panel_size(self.GetSize())
            child_menu_panel = wx.Panel(self.main_panel, wx.ID_ANY, pos = child_menu_panel_pos, size = child_menu_panel_size)
            main_menu_btn.child_menu_panel = child_menu_panel
            main_menu_btn.child_menu_panel.Show(False)
            main_menu_btn.child_menu_panel.SetBackgroundColour(SystemConfigs.COLOR_MENU_BACKGROUND)

            # 遍历所有子菜单的配置
            for index_2 in range(len(child_menus_arr)):
                child_menu = child_menus_arr[index_2]
                child_btn_temp_pos, child_btn_temp_size = calculate_child_menu_button_size(self.GetSize(), index_2)
                child_btn_temp = widgets.CustomGenBitmapTextToggleButton(
                    child_menu_panel,
                    wx.ID_ANY,
                    wx.Image(child_menu["icon"]).ConvertToBitmap(),
                    label = child_menu["name"],
                    custom_style = widgets.BUTTON_STYLE_HORIZONTAL,
                    background_color = SystemConfigs.COLOR_MENU_BUTTON_BACKGROUND,
                    pos = child_btn_temp_pos,
                    size = child_btn_temp_size
                )

                # 绑定事件
                child_btn_temp.Bind(wx.EVT_BUTTON, self.child_menu_toggled)

                # 将后续需要用的配置信息存到对象上
                child_btn_temp.bgColor = SystemConfigs.COLOR_MENU_BUTTON_BACKGROUND
                child_btn_temp.toggledColor = SystemConfigs.COLOR_MENU_BUTTON_TOGGLE
                child_btn_temp.events = child_menu["events"]

                # 将按钮对象加入到list中以方便后续操作
                main_menu_btn.child_menus.append(child_btn_temp)


    # 主菜单点击事件
    def main_menu_toggled(self, event):
        btn_temp = event.GetEventObject()

        # 判断是否在拖拽主窗体，是的话本次点击事件不触发
        if self.window_drag_flag:
            self.window_drag_flag = False
            btn_temp.SetToggle(False)
            return

        # 如果点击的主菜单按钮不是当前已经激活的，则清空content_panel的内容
        if btn_temp is not self.current_main_menu:
            self.current_main_menu.content_panel.Show(False)
            if self.current_main_menu.child_menu_panel is not None:
                self.current_main_menu.child_menu_panel.Show(False)

            # 先把当前激活的按钮重置
            self.current_main_menu.SetToggle(False)
            self.current_main_menu.SetBackgroundColour(self.current_main_menu.bgColor)

            # 激活新的按钮
            btn_temp.SetToggle(True)
            btn_temp.SetBackgroundColour(btn_temp.toggledColor)

            # 激活按钮关联的内容容器
            btn_temp.content_panel.Show(True)
            if btn_temp.child_menu_panel is not None:
                btn_temp.child_menu_panel.Show(True)

            # 如果有子菜单，则激活首个子菜单
            if len(btn_temp.child_menus) > 0:
                # 先把当前激活的按钮重置
                if self.current_child_menu is not None:
                    self.current_child_menu.SetToggle(False)
                    self.current_child_menu.SetBackgroundColour(self.current_child_menu.bgColor)

                # 然后再激活新的按钮
                btn_temp.child_menus[0].SetToggle(True)
                btn_temp.child_menus[0].SetBackgroundColour(btn_temp.child_menus[0].toggledColor)
                self.current_child_menu = btn_temp.child_menus[0]

            # 触发事件对象所绑定的事件
            call_api(self, btn_temp, event)

            # 将不显示的panel从主sizer中移除并将显示的加进去
            self.main_panel.GetSizer().Detach(self.current_main_menu.content_panel)
            self.main_panel.GetSizer().Add(btn_temp.content_panel)

            # 更新当前主菜单按钮对象
            self.current_main_menu = btn_temp

        # 不管是啥菜单，只要点了就一定是激活状态（防止重复点击同一个菜单时，按钮组件会在激活和未激活的样式上变来变去）
        self.current_main_menu.SetToggle(True)
        event.Skip()


    # 子菜单点击事件
    def child_menu_toggled(self, event):
        btn_temp = event.GetEventObject()
        if btn_temp is not self.current_child_menu:
            # 先把当前激活的按钮重置
            self.current_child_menu.SetToggle(False)
            self.current_child_menu.SetBackgroundColour(self.current_child_menu.bgColor)

            # 激活新的按钮
            btn_temp.SetToggle(True)
            btn_temp.SetBackgroundColour(btn_temp.toggledColor)

            # 触发事件对象所绑定的事件
            call_api(self, btn_temp, event)

            # 更新当前按钮对象
            self.current_child_menu = btn_temp

        # 不管是啥菜单，只要点了就一定是激活状态（防止重复点击同一个菜单时，按钮组件会在激活和未激活的样式上变来变去）
        self.current_child_menu.SetToggle(True)
        event.Skip()


    # 主窗口大小变化时，所有界面元素都需要调整
    def main_frame_resizing(self, event):
        # 使用异步调用可以保证所有元素在画（paint）的过程中，一定在正确的位置
        if not self.is_resizing:
            print("Resizing frame, Resolution: ", self.GetSize())
            self.is_resizing = True
            wx.CallLater(200, self.resize_everything)

    # 异步画界面
    def resize_everything(self):
        # 主菜单panel根据主窗口变化，自适应调整panel大小和位置
        self.main_panel.SetSize(self.GetSize())
        main_menu_panel_pos, main_menu_panel_size = calculate_main_menu_panel_size(self.GetSize())
        self.main_menu_panel.SetSize(main_menu_panel_size)

        # logo图片自适应调整大小和位置
        self.logo_img_png = wx.Image("configs/icons/logo.png")
        logo_img_pos, logo_img_size = calculate_logo_img_size(self.main_menu_panel.GetSize(),
                                                              self.logo_img_png.GetSize())
        self.logo_img_png.Rescale(logo_img_size[0], logo_img_size[1], wx.IMAGE_QUALITY_HIGH)
        self.logo_img_static.SetBitmap(self.logo_img_png.ConvertToBitmap())
        self.logo_img_static.SetPosition(logo_img_pos)

        # 刷新主菜单panel
        self.main_menu_panel.Refresh()

        # 主菜单panel中的所有按钮也要跟着改
        for main_menu in self.main_menu_panel.GetChildren():
            if isinstance(main_menu, widgets.CustomGenBitmapTextToggleButton):
                index = self.main_menus.index(main_menu)
                main_menu_button_pos, main_menu_button_size = calculate_main_menu_button_size(self.GetSize(), index)
                # 更改按钮的位置
                main_menu.SetPosition(main_menu_button_pos)
                # 更改按钮的大小
                main_menu.SetSize(main_menu_button_size)

                # 调整每个主菜单下的内容panel的size和位置
                content_panel_pos, content_panel_size = calculate_content_panel_size(self.GetSize(),
                                                                                     main_menu.child_menu_panel is not None)
                main_menu.content_panel.SetPosition(content_panel_pos)
                main_menu.content_panel.SetSize(content_panel_size)
                main_menu.content_panel.Refresh()

                if main_menu.child_menu_panel is not None:
                    child_menu_panel_pos, child_menu_panel_size = calculate_child_menu_panel_size(self.GetSize())
                    main_menu.child_menu_panel.SetPosition(child_menu_panel_pos)
                    main_menu.child_menu_panel.SetSize(child_menu_panel_size)

                    # 子菜单panel中的所有按钮也要跟着改
                    for child_menu in main_menu.child_menu_panel.GetChildren():
                        if isinstance(child_menu, widgets.CustomGenBitmapTextToggleButton):
                            index = main_menu.child_menus.index(child_menu)
                            child_btn_temp_pos, child_btn_temp_size = calculate_child_menu_button_size(self.GetSize(),
                                                                                                       index)
                            # 更改按钮的位置
                            child_menu.SetPosition(child_btn_temp_pos)
                            # 更改按钮的大小
                            child_menu.SetSize(child_btn_temp_size)

                    # 刷新子菜单panel
                    main_menu.child_menu_panel.Refresh()
        self.Refresh()
        self.is_resizing = False


    # 窗体拖拽事件 - 重新定位窗体位置
    def window_dragging(self, event):
        if not self.IsMaximized() and self.main_menu_panel.mouse_pos is not None:
            if event.Dragging():
                pos_changed = event.GetPosition() - self.main_menu_panel.mouse_pos
                # 判断拖动距离是否大于一定距离，如果太小则可能是点击事件，因此不重新定位，使按钮点击事件能正常触发
                if (abs(pos_changed[0]), abs(pos_changed[1])) > (1, 1):
                    self.window_drag_flag = True
                    self.SetPosition(self.GetPosition() + pos_changed)

        # 触发事件对象所绑定的事件
        call_api(self, event.GetEventObject(), event)
        event.Skip()


    # 窗体拖拽事件 - 鼠标左键按下
    def window_dragging_mouse_l_down(self, event):
        if not self.IsMaximized():
            self.main_menu_panel.mouse_pos = event.GetPosition()
        event.Skip()


    # 窗体拖拽事件 - 鼠标左键松开
    def window_dragging_mouse_l_up(self, event):
        if not self.IsMaximized():
            self.main_menu_panel.mouse_pos = None
        event.Skip()


# 计算主菜单panel的尺寸和位置
def calculate_main_menu_panel_size(panel_size):
    return (0, 0), (panel_size[0], panel_size[1] * 0.12)

# 计算主菜单按钮的尺寸和位置
def calculate_main_menu_button_size(panel_size, btn_index):
    return (btn_index * 0.12 * panel_size[1], 0), (0.12 * panel_size[1], 0.12 * panel_size[1])

# 计算内容panel的尺寸和位置
def calculate_content_panel_size(panel_size, has_children):
    if has_children:
        return (0.11 * panel_size[0], panel_size[1] * 0.12), (panel_size[0], panel_size[1] * (1 - 0.12))
    return (0, panel_size[1] * 0.12), (panel_size[0], panel_size[1] * (1 - 0.12))

# 计算子菜单panel的尺寸和位置
def calculate_child_menu_panel_size(panel_size):
    # 这里的position是(0, 0)的原因是，这个panel是在content_panel里面的，所以是一个相对坐标
    return (0, 0.12 * panel_size[1]), (0.11 * panel_size[0], panel_size[1] * (1 - 0.12))

# 计算子菜单按钮的尺寸和位置
def calculate_child_menu_button_size(panel_size, btn_index):
    return (0, btn_index * 0.07 * panel_size[1]), (0.11 * panel_size[0], 0.07 * panel_size[1])

# 计算logo图片的尺寸和位置
def calculate_logo_img_size(panel_size, logo_img_size):
    logo_img_new_height = panel_size[1] * 0.6
    logo_img_new_width = logo_img_size[0] * (logo_img_new_height / logo_img_size[1])
    logo_img_new_x = panel_size[0] - logo_img_new_width - 20
    logo_img_new_y = (panel_size[1] - logo_img_new_height) / 2
    return (logo_img_new_x, logo_img_new_y), (logo_img_new_width, logo_img_new_height)



if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, -1)
    frame.Show()
    app.MainLoop()

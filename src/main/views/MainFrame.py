import wx

from src.main import widgets
import src.main.configs as configs
import src.main.controllers as controller
from src.main.configs import SystemConfigs
from src.main.utils import CommonUtils


# 主窗体类
class MainFrame(wx.Frame):
    def __init__(self, parent = None, id = None, variables = None):
        wx.Frame.__init__(self, parent = parent, id = id, style = wx.DEFAULT_FRAME_STYLE)
        # 系统参数
        self.sys_variables = variables

        # 根据参数配置修改窗体属性
        self.SetSize(configs.SIZE_MAIN_FRAME_DEFAULT)
        self.SetClientSize(configs.SIZE_MAIN_FRAME_DEFAULT)
        self.SetMinSize(configs.SIZE_MAIN_FRAME_MINIMUM)

        # 状态参数
        self.current_main_menu = None
        self.current_child_menu = None
        self.main_menus = []

        # 设置系统最底层背景颜色（这里按应该用一些本地配置文件里的参数，因为这些参数通过用户修改是可以持久化到本地的）
        self.SetBackgroundColour(configs.COLOR_SYSTEM_BACKGROUND)

        # 主窗口panel
        self.main_panel = wx.Panel(self, wx.ID_ANY, pos = (0, 0), size = self.GetClientSize())

        # 给主窗口设置主布局sizer - 垂直线性布局
        # 共有2个子布局，分别是上方主菜单，下方内容
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 主菜单panel
        self.main_menu_panel = wx.Panel(self.main_panel, wx.ID_ANY)
        self.main_menu_panel.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
        # 添加到主sizer
        main_sizer.Add(self.main_menu_panel, 3, wx.EXPAND)
        # 初始化主菜单panel
        self.set_up_main_menu_panel()
        # 主菜单panel窗体拖动逻辑
        self.main_menu_panel.mouse_pos = None  # 初始化鼠标定位参数
        self.window_drag_flag = False
        self.main_menu_panel.Bind(wx.EVT_MOTION, self.window_dragging)
        self.main_menu_panel.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
        self.main_menu_panel.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)

        # 主体内容panel
        self.content_outer_panel = wx.Panel(self.main_panel, wx.ID_ANY)
        self.content_outer_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)
        # 添加到主sizer
        main_sizer.Add(self.content_outer_panel, 22, wx.EXPAND)
        # 初始化主体内容panel
        self.set_up_content_panel()

        # 子菜单panel
        self.child_menu_panel = None

        # 添加logo
        # logo_img_png = wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY)
        # logo_img_pos, logo_img_size = calculate_logo_img_size(self.main_menu_panel.GetSize(),
        #                                                       logo_img_png.GetSize())
        # logo_img_png.Rescale(logo_img_size[0], logo_img_size[1], wx.IMAGE_QUALITY_BOX_AVERAGE)
        # self.logo_img_static = wx.StaticBitmap(self.main_menu_panel, -1, logo_img_png.ConvertToBitmap())
        # self.logo_img_static.SetPosition(logo_img_pos)

        # 设置主sizer
        self.main_panel.SetSizer(main_sizer)
        self.main_panel.Layout()

        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.Bind(wx.EVT_SIZE, self.main_frame_resizing)

        # 给主窗口及其所有的子组件添加鼠标点击及松开事件
        self.mouse_down = False
        self.main_frame_release_mouse(self)

    def main_frame_release_mouse(self, obj):
        if len(obj.GetChildren()) > 0:
            for child in obj.GetChildren():
                self.main_frame_release_mouse(child)
        else:
            obj.Bind(wx.EVT_LEFT_DOWN, self.press_mouse)
            obj.Bind(wx.EVT_LEFT_UP, self.release_mouse)

    def press_mouse(self, event):
        self.mouse_down = True
        event.Skip()

    def release_mouse(self, event):
        self.mouse_down = False
        event.Skip()

    # 初始化主菜单panel
    def set_up_main_menu_panel(self):
        main_menu_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_menu_panel.SetSizer(main_menu_panel_sizer)

        button_panel = widgets.MainMenuPanel(self.main_menu_panel, wx.ID_ANY, configs.COLOR_MENU_BUTTON_BACKGROUND)
        main_menu_panel_sizer.Add(button_panel)
        button_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_panel.SetSizer(button_panel_sizer)

        index = 0 # index放外面主要是因为配置里有些菜单不一定是enabled，而index需要保持0开始并且是连续的
        for menu_config in SystemConfigs.main_menus_config:
            if menu_config["enabled"] and menu_config["id"] in self.sys_variables["license_data"]["MAIN_MENU_LIST"]:
                btn_temp = widgets.CustomMenuButton(
                    button_panel,
                    wx.ID_ANY,
                    wx.Image(menu_config["icon"], wx.BITMAP_TYPE_ANY).ConvertToBitmap(),
                    label = menu_config["name"],
                    label_color = configs.COLOR_TEXT_THEME,
                    custom_style = widgets.BUTTON_STYLE_VERTICAL,
                    background_color = configs.COLOR_MENU_BUTTON_BACKGROUND,
                    toggle_color = configs.COLOR_MENU_BUTTON_TOGGLE,
                    is_toggled = index == 0,
                )
                button_panel.buttons.append(btn_temp)
                button_panel_sizer.Add(btn_temp, 1, wx.EXPAND)

                # 设置当前被激活的主菜单按钮
                if index == 0:
                    self.current_main_menu = btn_temp

                # 绑定事件
                btn_temp.Bind(wx.EVT_LEFT_UP, self.main_menu_toggled)
                btn_temp.Bind(wx.EVT_MOTION, self.window_dragging)
                btn_temp.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
                btn_temp.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)

                # 将后续需要用的配置信息存到对象上
                btn_temp.bgColor = configs.COLOR_MENU_BUTTON_BACKGROUND
                btn_temp.toggledColor = configs.COLOR_MENU_BUTTON_TOGGLE
                btn_temp.menu_name = menu_config["name"]
                btn_temp.events = menu_config["events"]
                btn_temp.childrenMenus = menu_config["children"]
                btn_temp.view = menu_config["view"]
                # 设置
                btn_temp.is_functional_button = False
                if btn_temp.view is None and len(btn_temp.childrenMenus) == 0:
                    btn_temp.is_functional_button = True


                #
                # if btn_temp.view is not None or len(btn_temp.childrenMenus) > 0:
                #     # 将每个菜单的内容页容器绑定到菜单按钮上
                #     content_panel_pos, content_panel_size, content_panel_margin = calculate_content_panel_size(self.GetClientSize(), len(btn_temp.childrenMenus) > 0)
                #     btn_temp.content_panel = widgets.CustomBorderPanel(self.main_panel, wx.ID_ANY, pos = content_panel_pos, size = content_panel_size,
                #                                                        border_thickness = 1, border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER,
                #                                                        margin = content_panel_margin, radius = 0)
                #     btn_temp.content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)
                #
                #     # 绘制内容页panel的内容
                #     self.draw_content_panel(btn_temp, content_panel_size)
                #
                #     # 初始化子菜单
                #     btn_temp.child_menu_panel = None
                #     btn_temp.child_menus = []
                #
                #     # 将主菜单的子菜单添加到子菜单panel中
                #     self.add_child_menus(btn_temp)
                #
                #     # 如果是第一个按钮，则程序启动时默认是触发状态
                #     if index == 0:
                #         self.current_main_menu = btn_temp
                #         btn_temp.SetToggle(True)
                #         btn_temp.SetBackgroundColour(btn_temp.toggledColor)
                #
                #         # 展示当前的内容页
                #         btn_temp.content_panel.Show(True)
                #
                #         # 当前第一个按钮默认触发
                #         if len(btn_temp.child_menus) > 0:
                #             btn_temp.child_menu_panel.Show(True)
                #             self.current_child_menu = btn_temp.child_menus[0]
                #             self.current_child_menu.SetToggle(True)
                #             self.current_child_menu.SetBackgroundColour(self.current_child_menu.toggledColor)
                #     else:
                #         btn_temp.content_panel.Show(False)
                index += 1
                # 将按钮对象加入到list中以方便后续操作
                self.main_menus.append(btn_temp)
        self.main_menu_panel.Layout()
        self.main_menu_panel.button_panel = button_panel

    # 初始化主体内容panel
    def set_up_content_panel(self):
        content_outer_panel = self.content_outer_panel
        content_outer_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_outer_panel.SetSizer(content_outer_panel_sizer)

        for main_menu_btn in self.main_menus:
            # 初始化一个list用于存放当前主菜单的子菜单按钮
            main_menu_btn.child_menus = []

            # 给每个主菜单按钮再加一个panel，方便主菜单切换的时候显示和隐藏
            main_menu_btn_content_panel = wx.Panel(content_outer_panel, wx.ID_ANY)
            content_outer_panel_sizer.Add(main_menu_btn_content_panel, 1, wx.EXPAND)
            main_menu_btn_content_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
            main_menu_btn_content_panel.SetSizer(main_menu_btn_content_panel_sizer)
            # 将子菜单的content_panel存入主菜单按钮对象
            main_menu_btn.content_panel = main_menu_btn_content_panel

            if len(main_menu_btn.childrenMenus) > 0:
                # 子菜单按钮panel
                child_menus_arr = main_menu_btn.childrenMenus
                child_menu_panel = wx.Panel(main_menu_btn_content_panel, wx.ID_ANY)
                main_menu_btn_content_panel_sizer.Add(child_menu_panel, 12, wx.EXPAND)
                # 子菜单按钮panel的sizer
                child_menu_panel_sizer = wx.BoxSizer(wx.VERTICAL)
                child_menu_panel.SetSizer(child_menu_panel_sizer)
                # 给当前panel设置它对应的主菜单按钮
                child_menu_panel.main_menu_btn = main_menu_btn
                child_menu_panel.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
                # 给所有子菜单按钮再加一个框，跟主菜单一样
                button_panel = widgets.ChildMenuPanel(child_menu_panel, wx.ID_ANY, configs.COLOR_MENU_BUTTON_BACKGROUND)
                child_menu_panel_sizer.Add(button_panel)
                button_panel_sizer = wx.BoxSizer(wx.VERTICAL)
                button_panel.SetSizer(button_panel_sizer)

                # 主体内容需要一个新的panel，里面会放不同子菜单对应的不同的content_panel
                child_content_outer_panel = wx.Panel(main_menu_btn_content_panel, wx.ID_ANY)
                main_menu_btn_content_panel_sizer.Add(child_content_outer_panel, 88, wx.EXPAND)
                child_content_outer_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
                child_content_outer_panel.SetSizer(child_content_outer_panel_sizer)

                # 遍历所有子菜单的配置
                for index in range(len(child_menus_arr)):
                    child_menu = child_menus_arr[index]
                    child_btn_temp = widgets.CustomMenuButton(
                        button_panel,
                        wx.ID_ANY,
                        wx.Image(child_menu["icon"], wx.BITMAP_TYPE_ANY).ConvertToBitmap(),
                        label = child_menu["name"],
                        label_color = configs.COLOR_TEXT_THEME,
                        custom_style = widgets.BUTTON_STYLE_HORIZONTAL,
                        background_color = configs.COLOR_MENU_BUTTON_BACKGROUND,
                        toggle_color = configs.COLOR_MENU_BUTTON_TOGGLE,
                        need_trigger_bar = True,
                        is_toggled = index == 0,
                    )
                    button_panel.buttons.append(child_btn_temp)
                    button_panel_sizer.Add(child_btn_temp, 1, wx.EXPAND)

                    # 绑定事件
                    child_btn_temp.Bind(wx.EVT_LEFT_UP, self.child_menu_toggled)

                    # 将后续需要用的配置信息存到对象上
                    child_btn_temp.bgColor = configs.COLOR_MENU_BUTTON_BACKGROUND
                    child_btn_temp.toggledColor = configs.COLOR_MENU_BUTTON_TOGGLE
                    child_btn_temp.events = child_menu["events"]

                    # 将按钮对象加入到list中以方便后续操作
                    main_menu_btn.child_menus.append(child_btn_temp)

                    # 给每个子菜单创建对应的content_panel
                    child_content_panel = widgets.CustomBorderPanel(child_content_outer_panel, wx.ID_ANY, border_thickness = 1,
                                                                    border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
                    child_content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)
                    child_content_outer_panel_sizer.Add(child_content_panel, 1, wx.EXPAND)

                    # 如果不是当前被激活的按钮的子菜单，则不展示
                    if index != 0:
                        child_content_panel.Show(False)
                    else:
                        self.current_child_menu = child_btn_temp

                    # 存入到对应子菜单的对象里
                    child_btn_temp.child_content_panel = child_content_panel

                child_menu_panel.Layout()
                main_menu_btn.child_menu_panel = child_menu_panel
            elif main_menu_btn.view is not None:
                # 给主菜单创建对应的content_panel
                main_content_panel = widgets.CustomBorderPanel(main_menu_btn_content_panel, wx.ID_ANY, border_thickness = 1,
                                                               border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER)
                main_content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)
                main_menu_btn_content_panel_sizer.Add(main_content_panel, 1, wx.EXPAND)

                # 存入到对应子菜单的对象里
                main_menu_btn.main_content_panel = main_content_panel

            if main_menu_btn is not self.current_main_menu:
                main_menu_btn_content_panel.Show(False)
            main_menu_btn_content_panel.Layout()

        # 刷新一下整体布局
        self.content_outer_panel.Layout()

    # 绘制content_panel的内容
    def draw_content_panel(self, main_menu_btn, size):
        content_panel = main_menu_btn.content_panel
        content_panel.menu_name = main_menu_btn.menu_name

        # 实例化视图
        if main_menu_btn.view is None:
            # TODO: children views show here
            pass
        elif main_menu_btn.view is wx.Panel:
            content_panel.view = wx.Panel(content_panel, wx.ID_ANY)
        else:
            content_panel.view = main_menu_btn.view(content_panel, wx.ID_ANY, size = size)

    # 添加子菜单（如果有的话）
    def add_child_menus(self, main_menu_btn):
        child_menus_arr = main_menu_btn.childrenMenus

        # 如果指定主菜单有子菜单配置的话
        if len(child_menus_arr) > 0:
            child_menu_panel_pos, child_menu_panel_size = calculate_child_menu_panel_size(self.GetClientSize())
            child_menu_panel = wx.Panel(self.main_panel, wx.ID_ANY, pos = child_menu_panel_pos,
                                        size = child_menu_panel_size)
            main_menu_btn.child_menu_panel = child_menu_panel
            main_menu_btn.child_menu_panel.Show(False)
            main_menu_btn.child_menu_panel.SetBackgroundColour(
                configs.COLOR_MENU_BACKGROUND)

            # 遍历所有子菜单的配置
            for index_2 in range(len(child_menus_arr)):
                child_menu = child_menus_arr[index_2]
                child_btn_temp_pos, child_btn_temp_size = calculate_child_menu_button_size(self.GetClientSize(), index_2)
                child_btn_temp = widgets.CustomMenuButton(
                    child_menu_panel,
                    wx.ID_ANY,
                    wx.Image(child_menu["icon"], wx.BITMAP_TYPE_ANY).ConvertToBitmap(),
                    label = child_menu["name"],
                    label_color = configs.COLOR_TEXT_THEME,
                    custom_style = widgets.BUTTON_STYLE_HORIZONTAL,
                    background_color = configs.COLOR_MENU_BUTTON_BACKGROUND,
                    need_trigger_bar = True,
                    pos = child_btn_temp_pos,
                    size = child_btn_temp_size
                )

                # 绑定事件
                child_btn_temp.Bind(wx.EVT_LEFT_UP, self.child_menu_toggled)

                # 将后续需要用的配置信息存到对象上
                child_btn_temp.bgColor = configs.COLOR_MENU_BUTTON_BACKGROUND
                child_btn_temp.toggledColor = configs.COLOR_MENU_BUTTON_TOGGLE
                child_btn_temp.events = child_menu["events"]

                # 将按钮对象加入到list中以方便后续操作
                main_menu_btn.child_menus.append(child_btn_temp)

    # 主菜单点击事件 - 释放
    def main_menu_toggled(self, event):
        btn_panel_temp = event.GetEventObject()

        # 判断是否在拖拽主窗体，是的话本次点击事件不触发
        if self.window_drag_flag:
            self.window_drag_flag = False
            # 只要触发了evt_left_up事件，按钮的激活状态一定会被反置，这个目前暂时不知道怎么重写去解决，只能暂时这样处理
            # 简单解释这行代码的意思就是：如果是拖拽的情况下，让按钮保持原本的状态
            btn_panel_temp.SetToggle(btn_panel_temp is self.current_main_menu)
            return

        # 判断当前点击的按钮是否是当前已经激活的主菜单按钮
        if btn_panel_temp is not self.current_main_menu:
            # 判断是否是功能性按钮
            if not btn_panel_temp.is_functional_button:
                current = self.current_main_menu

                # 如果不是则说明要换一个界面了，因此先隐藏当前的界面
                current.content_panel.Show(False)
                # 把当前激活的按钮重置
                current.SetToggle(False)
                # 激活新的按钮
                btn_panel_temp.SetToggle(True)

                # 激活按钮关联的内容容器
                btn_panel_temp.content_panel.Show(True)

                # 更新当前主菜单按钮对象
                self.current_main_menu = btn_panel_temp
        else:
            # 如果点的是已经激活的菜单，也要重新激活一下，因为toggle按钮组件底层SetToggle一定会被调用，toggle会被设置会False，所以要手动激活一下
            # 尝试过重写，SetToggle方法，但是会出现更奇怪的问题，所以就这样解决吧
            self.current_main_menu.SetToggle(True)

        # 触发事件对象所绑定的事件
        controller.call_api(event)

        self.content_outer_panel.Layout()
        event.Skip()

    # 子菜单点击事件 - 释放
    def child_menu_toggled(self, event):
        btn_panel_temp = event.GetEventObject()

        if btn_panel_temp is not self.current_child_menu:
            current = self.current_child_menu

            # 把当前激活的按钮重置
            current.SetToggle(False)
            # 隐藏当前子菜单的内容
            current.child_content_panel.Show(False)

            # 激活新的按钮
            btn_panel_temp.SetToggle(True)
            # 显示新激活的菜单的内容
            btn_panel_temp.child_content_panel.Show(True)
            btn_panel_temp.child_content_panel.GetParent().Layout()

            # # 触发事件对象所绑定的事件
            # controller.call_api(event)

            # 更新当前按钮对象
            self.current_child_menu = btn_panel_temp

        # 不管是啥菜单，只要点了就一定是激活状态（防止重复点击同一个菜单时，按钮组件会在激活和未激活的样式上变来变去）
        self.current_child_menu.SetToggle(True)
        event.Skip()

    # 主窗口大小变化时，所有界面元素都需要调整
    def main_frame_resizing(self, event):
        # 使用异步调用可以保证所有元素在画（paint）的过程中，一定在正确的位置
        if not self.is_resizing:
            print("Resizing frame, Resolution: ", self.GetClientSize())
            self.is_resizing = True
            wx.CallLater(100, self.resize_everything)
        event.Skip()

    # 异步画界面
    def resize_everything(self):
        # 主菜单panel根据主窗口变化，自适应调整panel大小和位置
        self.main_panel.SetSize(self.GetClientSize())
        main_menu_panel_pos, main_menu_panel_size = calculate_main_menu_panel_size(self.GetClientSize())
        self.main_menu_panel.SetSize(main_menu_panel_size)

        # # logo图片自适应调整大小和位置
        # logo_img_png = wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY)
        # logo_img_pos, logo_img_size = calculate_logo_img_size(self.main_menu_panel.GetSize(),
        #                                                       logo_img_png.GetSize())
        # logo_img_png.Rescale(logo_img_size[0], logo_img_size[1], wx.IMAGE_QUALITY_BOX_AVERAGE)
        # self.logo_img_static.SetBitmap(logo_img_png.ConvertToBitmap())
        # self.logo_img_static.SetPosition(logo_img_pos)
        #
        # # 刷新主菜单panel
        # self.main_menu_panel.Refresh()

        # 主菜单panel中的所有按钮也要跟着改
        # for main_menu in self.main_menu_panel.GetChildren():
        #     if isinstance(main_menu, widgets.CustomMenuButton):
        #         index = self.main_menus.index(main_menu)
                # main_menu_button_pos, main_menu_button_size = calculate_main_menu_button_size(self.GetClientSize(), index)
                # # 更改按钮的大小
                # main_menu.SetSize(main_menu_button_size)
                # # 更改按钮的位置
                # main_menu.SetPosition(main_menu_button_pos)

                # if main_menu.view is not None or len(main_menu.childrenMenus) > 0:
                #     # 调整每个主菜单下的内容panel的size和位置
                #     content_panel_pos, content_panel_size, content_panel_margin = calculate_content_panel_size(self.GetClientSize(), main_menu.child_menu_panel is not None)
                #     main_menu.content_panel.SetSize(content_panel_size)
                #     main_menu.content_panel.SetPosition(content_panel_pos)
                #     main_menu.content_panel.SetMargin(content_panel_margin)
                #     main_menu.content_panel.Refresh()
                #     if main_menu.view is not None:
                #         main_menu.content_panel.view.SetSize(content_panel_size)
                #         main_menu.content_panel.view.SetPosition(content_panel_pos)
                #
                #     if main_menu.child_menu_panel is not None:
                #         child_menu_panel_pos, child_menu_panel_size = calculate_child_menu_panel_size(self.GetClientSize())
                #         main_menu.child_menu_panel.SetSize(child_menu_panel_size)
                #         main_menu.child_menu_panel.SetPosition(child_menu_panel_pos)
                #
                #         # 子菜单panel中的所有按钮也要跟着改
                #         for child_menu in main_menu.child_menu_panel.GetChildren():
                #             if isinstance(child_menu, widgets.CustomMenuButton):
                #                 index = main_menu.child_menus.index(child_menu)
                #                 child_btn_temp_pos, child_btn_temp_size = calculate_child_menu_button_size(self.GetClientSize(), index)
                #                 # 更改按钮的大小
                #                 child_menu.SetSize(child_btn_temp_size)
                #                 # 更改按钮的位置
                #                 child_menu.SetPosition(child_btn_temp_pos)
                #
                #         # 刷新子菜单panel
                #         main_menu.child_menu_panel.Refresh()
        self.Refresh()
        self.is_resizing = False

    # 窗体拖拽事件 - 重新定位窗体位置
    def window_dragging(self, event):
        if not self.IsMaximized() and self.main_menu_panel.mouse_pos is not None:
            if event.Dragging():
                pos_changed = event.GetPosition() - self.main_menu_panel.mouse_pos
                # 判断拖动距离是否大于一定距离，如果太小则可能是点击事件，因此不重新定位，使按钮点击事件能正常触发
                if (abs(pos_changed[0]), abs(pos_changed[1])) > (2, 2):
                    self.window_drag_flag = True
                    self.SetPosition(self.GetPosition() + pos_changed)

                # 触发事件对象所绑定的事件
                controller.call_api(event)
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

    # 主窗体显示或隐藏
    def show_all(self, flag: bool = True):
        self.main_panel.Show(flag)

# 计算主菜单panel的尺寸和位置
def calculate_main_menu_panel_size(panel_size):
    pos_x = 0
    pos_y = 0
    width = panel_size[0]
    height = int(panel_size[1] * 0.12)
    return (pos_x, pos_y), (width, height)


# 计算主菜单按钮的尺寸和位置
def calculate_main_menu_button_size(panel_size, btn_index):
    pos_x = btn_index * int(0.12 * panel_size[1])
    pos_y = 0
    width = int(0.12 * panel_size[1])
    height = int(0.12 * panel_size[1])
    return (pos_x, pos_y), (width, height)


# 计算内容panel的尺寸和位置
def calculate_content_panel_size(panel_size, has_children):
    pos_x = 0
    pos_y = int(panel_size[1] * 0.12)
    width = panel_size[0]
    height = panel_size[1] - int(0.12 * panel_size[1])

    if has_children:
        pos_x = int(0.11 * panel_size[0])
        width = panel_size[0] - int(0.11 * panel_size[0])

    margin = int(width / 300) + 3
    return (pos_x, pos_y), (width, height), margin


# 计算子菜单panel的尺寸和位置
def calculate_child_menu_panel_size(panel_size):
    # 这里的x是0的原因是，这个panel是在content_panel里面的，所以是一个相对坐标
    pos_x = 0
    pos_y = int(0.12 * panel_size[1])
    width = int(0.11 * panel_size[0])
    height = panel_size[1] - int(0.12 * panel_size[1])
    return (pos_x, pos_y), (width, height)


# 计算子菜单按钮的尺寸和位置
def calculate_child_menu_button_size(panel_size, btn_index):
    pos_x = 0
    pos_y = btn_index * int(0.07 * panel_size[1])
    width = int(0.11 * panel_size[0])
    height = int(0.07 * panel_size[1])
    return (pos_x, pos_y), (width, height)


# 计算logo图片的尺寸和位置
def calculate_logo_img_size(panel_size, logo_img_size):
    width, height = CommonUtils.CalculateNewSizeWithSameRatio(logo_img_size, panel_size[1] * 0.6 / logo_img_size[1])
    pos_x = panel_size[0] - width - 5
    pos_y = (panel_size[1] - height) / 2
    return (pos_x, pos_y), (width, height)


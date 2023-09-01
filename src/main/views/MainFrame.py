import math

import wx

from src.main import widgets
import src.main.configs as configs
import src.main.controllers as controller
from src.main.configs import SystemConfigs
from src.main.utils import CommonUtils


# 主窗体类
class MainFrame(wx.Frame):
    def __init__(self, parent = None, id = None, variables = None):
        wx.Frame.__init__(
            self, parent = parent, id = id,
            # style = wx.SYSTEM_MENU,
            style = wx.DEFAULT_FRAME_STYLE,
        )
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
        sizer = wx.BoxSizer()
        self.main_panel.SetSizer(sizer)

        # 主菜单panel
        self.main_menu_panel = MainMenuPanel(parent = self.main_panel)
        sizer.Add(self.main_menu_panel)

        # 初始化主菜单panel（包含一个logo）
        self.set_up_main_menu_panel()

        # 主菜单panel窗体拖动逻辑
        self.main_menu_panel.mouse_pos = None  # 初始化鼠标定位参数
        self.window_drag_flag = False
        self.bind_dragging_event(self.main_menu_panel)

        # 主体内容panel
        for main_menu in self.main_menu_panel.menu_buttons:
            main_menu.menu_content_panel = MenuContentPanel(self.main_panel, parent_menu = main_menu)
            main_menu.menu_content_panel.set_self_calculation(self.main_menu_panel.calc_content)

            # 初始化主体内容panel
            self.set_up_main_content_panel(main_menu.menu_content_panel)

            # 如果不是当前激活的panel，则隐藏起来
            if main_menu is not self.current_main_menu:
                main_menu.menu_content_panel.Hide()

            # 根据每个菜单的view配置，绘制对应的view
            self.draw_view(main_menu)

        # 给主窗口绑定【窗口大小变化】事件，确保不同分辨率下，系统UI始终保持最佳比例
        self.is_resizing = False
        self.Bind(wx.EVT_SIZE, self.main_frame_on_size)

        # 给主窗口及其所有的子组件添加鼠标点击及松开事件
        self.mouse_down = False
        self.main_frame_release_mouse(self)

        # 主动触发size事件，使界面自动调整布局
        event_temp = wx.SizeEvent((0, 0))
        event_temp.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event_temp)

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
        index = 0 # index放外面主要是因为配置里有些菜单不一定是enabled，而index需要保持0开始并且是连续的
        for menu_config in SystemConfigs.main_menus_config:
            if menu_config["enabled"] and menu_config["id"] in self.sys_variables["license_data"]["MAIN_MENU_LIST"]:
                btn_temp = self.main_menu_panel.add_menu_button(
                    icon = wx.Image(menu_config["icon"], wx.BITMAP_TYPE_ANY).ConvertToBitmap(),
                    label = menu_config["name"], is_toggled = index == 0
                )
                # 设置当前被激活的主菜单按钮
                if index == 0:
                    self.current_main_menu = btn_temp

                # 绑定事件
                btn_temp.Bind(wx.EVT_LEFT_UP, self.main_menu_toggled)
                self.bind_dragging_event(btn_temp)

                # 将后续需要用的配置信息存到对象上
                btn_temp.bgColor = configs.COLOR_MAIN_MENU_BUTTON_BACKGROUND
                btn_temp.toggledColor = configs.COLOR_MENU_BUTTON_TOGGLE
                btn_temp.menu_name = menu_config["name"]
                btn_temp.events = menu_config["events"]
                btn_temp.childrenMenus = menu_config["children"]
                btn_temp.viewPanel = menu_config["view"]
                # 设置
                btn_temp.is_functional_button = False
                if btn_temp.viewPanel is None and len(btn_temp.childrenMenus) == 0:
                    btn_temp.is_functional_button = True

                index += 1
                # 将按钮对象加入到list中以方便后续操作
                self.main_menus.append(btn_temp)

        # 添加logo图片
        self.main_menu_panel.set_logo(wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY).ConvertToBitmap())

    # 初始化主体内容panel
    def set_up_main_content_panel(self, menu_content_panel):
        main_menu = menu_content_panel.parent_menu

        if len(main_menu.childrenMenus) == 0:
            # 如果没有子菜单，则初始化content_panel
            menu_content_panel.set_up_content_panel()
        else:
            main_menu.menu_buttons = []
            child_menu_panel = ChildMenuPanel(menu_content_panel)
            menu_content_panel.add_child_button_panel(child_menu_panel)

            child_menus_arr = main_menu.childrenMenus
            # 遍历所有子菜单的配置
            for index in range(len(child_menus_arr)):
                child_menu = child_menus_arr[index]
                child_btn_temp = child_menu_panel.add_menu_button(
                    icon = wx.Image(child_menu["icon"], wx.BITMAP_TYPE_ANY).ConvertToBitmap(),
                    label = child_menu["name"], is_toggled = index == 0
                )
                # 绑定事件
                child_btn_temp.Bind(wx.EVT_LEFT_UP, self.child_menu_toggled)

                # 将后续需要用的配置信息存到对象上
                child_btn_temp.bgColor = configs.COLOR_MAIN_MENU_BUTTON_BACKGROUND
                child_btn_temp.toggledColor = configs.COLOR_MENU_BUTTON_TOGGLE
                child_btn_temp.menu_name = child_menu["name"]
                child_btn_temp.events = child_menu["events"]
                child_btn_temp.viewPanel = child_menu["view"]

                # 创建子菜单对应的content_panel
                child_btn_temp.menu_content_panel = MenuContentPanel(menu_content_panel, parent_menu = child_btn_temp)
                child_btn_temp.menu_content_panel.set_self_calculation(child_menu_panel.calc_content)
                child_btn_temp.menu_content_panel.set_up_content_panel()

                # 如果不是当前被激活的按钮的子菜单，则不展示
                if index != 0:
                    child_btn_temp.menu_content_panel.Show(False)
                else:
                    main_menu.current_child_menu = child_btn_temp

                    # 将子菜单按钮对象加入到对应主菜单按钮的list中以方便后续操作
                    main_menu.menu_buttons.append(child_btn_temp)

                    # 根据每个菜单的view配置，绘制对应的view
                    self.draw_view(child_btn_temp)

    # 绘制view
    def draw_view(self, menu_button):
        view_parent_panel = menu_button.menu_content_panel.content_panel
        if view_parent_panel is None:
            return

        # 给view_parent_panel设置一个sizer
        sizer = wx.BoxSizer()
        view_parent_panel.SetSizer(sizer)

        # 实例化视图
        if menu_button.viewPanel is not None:
            # 创建视图并绑定专属的on_size事件
            view = menu_button.viewPanel(view_parent_panel,
                                         wx.ID_ANY,
                                         menu_name = menu_button.menu_name)
            # 添加到布局中让view保持跟父panel一致的大小
            sizer.Add(view, 1, wx.EXPAND)
            # 将view存到按钮对象中
            menu_button.view = view

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
                current.menu_content_panel.Hide()
                # 把当前激活的按钮重置
                current.SetToggle(False)
                # 激活新的按钮
                btn_panel_temp.SetToggle(True)

                # 激活按钮关联的内容容器
                btn_panel_temp.menu_content_panel.Show()

                # 更新当前主菜单按钮对象
                self.current_main_menu = btn_panel_temp

            # 触发事件对象所绑定的事件
            controller.call_api(event)
        else:
            # 如果点的是已经激活的菜单，也要重新激活一下，因为toggle按钮组件底层SetToggle一定会被调用，toggle会被设置会False，所以要手动激活一下
            # 尝试过重写，SetToggle方法，但是会出现更奇怪的问题，所以就这样解决吧
            self.current_main_menu.SetToggle(True)

        event.Skip()

    # 子菜单点击事件 - 释放
    def child_menu_toggled(self, event):
        btn_panel_temp = event.GetEventObject()

        if btn_panel_temp is not self.current_main_menu.current_child_menu:
            current = self.current_main_menu.current_child_menu

            # 把当前激活的按钮重置
            current.SetToggle(False)
            # 隐藏当前子菜单的内容
            current.menu_content_panel.Show(False)

            # 激活新的按钮
            btn_panel_temp.SetToggle(True)
            # 显示新激活的菜单的内容
            btn_panel_temp.menu_content_panel.Show(True)

            # # 触发事件对象所绑定的事件
            controller.call_api(event)

            # 更新当前按钮对象
            self.current_main_menu.current_child_menu = btn_panel_temp

        # 不管是啥菜单，只要点了就一定是激活状态（防止重复点击同一个菜单时，按钮组件会在激活和未激活的样式上变来变去）
        self.current_main_menu.current_child_menu.SetToggle(True)
        event.Skip()

    # 主窗口大小变化时，所有界面元素都需要调整
    def main_frame_on_size(self, event):
        self.main_panel.Freeze()
        wx.CallLater(100, self.resize_after)
        event.Skip()

    def resize_after(self):
        # 稍稍滞后，效果看起来更好
        size = self.GetClientSize()
        print("main_frame_on_size, Resolution: ", size)
        if size == (0, 0):
            return
        self.main_panel.SetSize(size)  # hide之后再show不知道为啥不跟着self一起变了，直接设置吧
        self.main_panel.Layout()
        self.main_panel.Thaw()
        self.main_panel.Refresh()

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

    # 给组件绑定所有窗体拖拽事件
    def bind_dragging_event(self, widget_obj):
        widget_obj.Bind(wx.EVT_MOTION, self.window_dragging)
        widget_obj.Bind(wx.EVT_LEFT_DOWN, self.window_dragging_mouse_l_down)
        widget_obj.Bind(wx.EVT_LEFT_UP, self.window_dragging_mouse_l_up)


# 主菜单panel组件
class MainMenuPanel(wx.Panel):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "MainMenuPanel"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size, style = style, name = name)
        self.SetBackgroundColour(configs.COLOR_MENU_BACKGROUND)
        self.menu_buttons = []
        self.logo_bitmap = None
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        # 计算自身size和pos
        size, pos = self.calc_self()
        self.SetSize(size)

        # 重设按钮的size和pos
        for index in range(len(self.menu_buttons)):
            btn = self.menu_buttons[index]
            # 计算当前按钮的size和pos
            b_size, b_pos = self.calc_button(index)
            # 设置size和pos
            btn.SetSize(b_size)
            btn.SetPosition(b_pos)
            # 如果按钮对应的content_panel存在，则触发其on_size事件
            if btn.menu_content_panel is not None:
                btn.menu_content_panel.on_size(event)

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

    def add_menu_button(self, icon, label, is_toggled):
        btn_temp = widgets.CustomMenuButton(
            self,
            wx.ID_ANY,
            icon,
            label = label,
            label_color = configs.COLOR_TEXT_THEME,
            custom_style = widgets.BUTTON_STYLE_VERTICAL,
            background_color = configs.COLOR_MAIN_MENU_BUTTON_BACKGROUND,
            toggle_color = configs.COLOR_MENU_BUTTON_TOGGLE,
            is_toggled = is_toggled
        )
        btn_temp.menu_content_panel = None
        self.menu_buttons.append(btn_temp)
        return btn_temp

    def set_logo(self, bitmap):
        self.logo_bitmap = bitmap

    def calc_self(self):
        p_w, p_h = self.GetParent().GetSize()
        return (p_w, math.ceil(0.12 * p_h)), (0, 0)

    def calc_button(self, index):
        w, h = self.GetSize()
        b_w = b_h = h
        return (b_w, b_h), (index * b_w, 0)

    def calc_logo(self, image_size):
        w, h = self.GetSize()
        i_w, i_h = image_size
        i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), h * 0.7 / i_h)
        return (i_w, i_h), (w - i_w - math.ceil(w / 300), math.ceil((h - i_h) / 2))

    def calc_content(self, p_w, p_h):
        main_menu_h = math.ceil(0.12 * p_h)
        new_h = p_h - main_menu_h
        return (p_w, new_h), (0, main_menu_h)


# 子菜单panel组件
class ChildMenuPanel(wx.Panel):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "ChildMenuPanel"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size, style = style, name = name)
        self.SetBackgroundColour(configs.COLOR_CHILD_MENU_BUTTON_BACKGROUND)
        self.menu_buttons = []
        self.buttons = []
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        # 计算自身size和pos
        size, pos = self.calc_self()
        self.SetSize(size)

        # 重设按钮的size和pos
        for index in range(len(self.menu_buttons)):
            btn = self.menu_buttons[index]
            # 计算当前按钮的size和pos
            b_size, b_pos = self.calc_button(index)
            # 设置size和pos
            btn.SetSize(b_size)
            btn.SetPosition(b_pos)
            # 如果按钮对应的content_panel存在，则触发其on_size事件
            if btn.menu_content_panel is not None:
                btn.menu_content_panel.on_size(event)

        event.Skip()

    def add_menu_button(self, icon, label, is_toggled):
        btn_temp = widgets.CustomMenuButton(
            self,
            wx.ID_ANY,
            icon,
            label = label,
            label_color = configs.COLOR_TEXT_THEME,
            custom_style = widgets.BUTTON_STYLE_HORIZONTAL,
            background_color = configs.COLOR_CHILD_MENU_BUTTON_BACKGROUND,
            toggle_color = configs.COLOR_MENU_BUTTON_TOGGLE,
            need_trigger_bar = True,
            is_toggled = is_toggled,
        )
        btn_temp.menu_content_panel = None
        self.menu_buttons.append(btn_temp)
        return btn_temp

    def calc_self(self):
        p_w, p_h = self.GetParent().GetSize()
        return (math.ceil(0.11 * p_w), p_h), (0, 0)

    def calc_button(self, index):
        w, h = self.GetSize()
        b_w = w
        b_h = math.ceil(h * 0.07)
        return (b_w, b_h), (0, index * b_h)

    def calc_content(self, p_w, p_h):
        child_menu_w = math.ceil(0.11 * p_w)
        new_w = p_w - child_menu_w
        return (new_w, p_h), (child_menu_w, 0)


# 每个菜单按钮对应的content_panel组件（主菜单子菜单都可以）
class MenuContentPanel(wx.Panel):
    def __init__(self, parent, parent_menu, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "MenuContentPanel"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size, style = style, name = name)
        self.parent_menu = parent_menu
        self.button_panel = None
        self.content_panel = None
        self.calc_self = None
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        # 计算自身size和pos
        p_width, p_height = self.GetParent().GetSize()
        size, pos = self.calc_self(p_width, p_height)
        self.SetSize(size)
        self.SetPosition(pos)

        # 重设子菜单panel（如果有的话）的size和pos
        if self.button_panel:
            cbp_size, cbp_pos = self.calc_button_panel()
            self.button_panel.SetSize(cbp_size)
            self.button_panel.SetPosition(cbp_pos)
        else:
            # 重设content_Panel的size和pos
            self.content_panel.SetSize(size)
            self.content_panel.SetPosition((0, 0))

        event.Skip()

    def add_child_button_panel(self, child_button_panel):
        self.button_panel = child_button_panel

    def set_up_content_panel(self):
        self.content_panel = widgets.CustomBorderPanel(self, wx.ID_ANY, border_thickness = 1,
                                                       border_color = configs.COLOR_CONTENT_PANEL_INSIDE_BORDER,
                                                       self_adaptive = True)
        self.content_panel.SetBackgroundColour(configs.COLOR_CONTENT_PANEL_BACKGROUND)

    def calc_self(self):
        pass

    def set_self_calculation(self, method):
        self.calc_self = method

    def calc_button_panel(self):
        w, h = self.GetSize()
        return (math.ceil(0.13 * w), h), (0, 0)



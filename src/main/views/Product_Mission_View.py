import math

import wx

import src.main.widgets as widgets
import src.main.configs as configs
from src.main.controllers import apis
from src.main.utils import CommonUtils, CacheUtil
from src.main.views.Content_Workplace import WorkplaceView


# 任务数据缓存配置
MISSION_DATA_CACHE_KEY = "MISSION_DATA"
MISSION_DATA_CACHE_TIME_OUT = 120 # 数据缓存过期时间（秒）

# 任务列表展示界面的gridSizer的列数固定为4
MISSION_COLUMNS = 4
# 每个任务之间的间隔占content_panel宽度的多少比例
MISSION_GAP_RATIO = 5
# 每个任务的高度占content_panel的多少比例
MISSION_HEIGHT_RATIO = 35
# 展示区域的行达到多少就需要滚动条
MISSION_ROWS_SCROLL = 3


# 产品任务展示界面
class ProductMissionView(widgets.CustomViewPanel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "ProductMissionView"):
        widgets.CustomViewPanel.__init__(self, parent, id, pos, size, style, name)
        self.menu_name = parent.menu_name
        self.call_back_variables = None
        self.add_mission_button = None
        self.block_panel = None
        self.mission_blocks = []
        self.content_blocks = None
        self.has_scroller = False
        self.need_redraw = True
        self.sizer = None
        self.data = None
        self.data_changed = False
        self.size_cache = None

        self.parent = self.GetParent()
        self.parent.scroll_bar = None

        self.is_painting = False
        self.Bind(wx.EVT_PAINT, self.on_paint)

    # 重写父类的on_size方法，并且不需要重复绑定，否则会出现多次调用
    def on_size(self, event):
        self.SetMargin(self.GetSize()[1] * 0.02)
        super().on_size(event)
        # self.Layout()

    def on_paint(self, event):
        # 从缓存中取出数据
        data = self.get_data()
        # data = []

        # 如果没有任何任务，则提供一个跳转到任务管理界面添加任务的按钮
        if len(data) == 0:
            if self.add_mission_button is None:
                self.add_mission_button = widgets.CustomRadiusButton(self, wx.ID_ANY, label = "点击添加任务",
                                                                     font_color = configs.COLOR_BUTTON_TEXT,
                                                                     background_color = configs.COLOR_BUTTON_BACKGROUND,
                                                                     clicked_color = configs.COLOR_BUTTON_CLICKED,
                                                                     button_size_type = widgets.BUTTON_SIZE_TYPE_BIG,
                                                                     button_type = widgets.BUTTON_TYPE_NORMAL,
                                                                     size = self.get_button_size(), radius = 3)
                self.add_mission_button.Bind(wx.EVT_LEFT_DOWN, self.button_on_click)
            else:
                self.add_mission_button.SetSize(self.get_button_size())
            # 刷新按钮至中间的位置
            self.add_mission_button.Center()
            self.add_mission_button.Refresh()
        else:
            if self.data_changed:
                data_len = len(data)
                # 计算grid需要几行
                grid_rows = math.ceil(data_len / MISSION_COLUMNS)
                # 需要一个宽度与self.width一致但高度会根据数据量动态改变的panel（为了实现滚动效果）
                if self.block_panel is None:
                    self.block_panel = MissionBlocksPanel(self, wx.ID_ANY, grid_rows = grid_rows)
                    block_sizer = wx.GridSizer(cols = MISSION_COLUMNS)
                    self.block_panel.SetSizer(block_sizer)
                    # 将此panel加入sizer
                    if self.sizer is None:
                        self.sizer = wx.BoxSizer(wx.VERTICAL)
                        self.SetSizer(self.sizer)
                    self.sizer.Add(self.block_panel, 1, wx.EXPAND)
                else:
                    self.block_panel.SetGridRows(grid_rows)
                    block_sizer = self.block_panel.GetSizer()
                    block_sizer.SetRows(grid_rows)

                # 计算每个展示块的间距
                gap = math.floor(self.GetSize()[1] * (MISSION_GAP_RATIO / 100))
                block_sizer.SetHGap(gap)
                block_sizer.SetVGap(gap)

                # 销毁所有之前的展示块
                if len(self.mission_blocks) != 0:
                    for block in self.mission_blocks:
                        if block and not block.IsBeingDeleted():
                            block.Destroy()
                # 清除sizer中所有的
                block_sizer.Clear()

                # 创建展示块
                for index in range(data_len):
                    mission_obj = data[index]
                    mission_name = mission_obj.GetMissionName()
                    mission_image = mission_obj.GetMissionProductSides()[0].GetSideImage().GetImageOriginal()
                    mission_image = CommonUtils.PILImageToWxImage(mission_image).ConvertToBitmap()
                    mission_block = MissionBlock(self.block_panel, wx.ID_ANY, mission_name = mission_name, mission_image = mission_image)
                    # 初始化视图变量
                    mission_block.view = None
                    mission_block.Bind(wx.EVT_LEFT_UP, self.mission_block_click)
                    block_sizer.Add(mission_block, 1, wx.EXPAND)
                    self.mission_blocks.append(mission_block)

        self.Layout()
        event.Skip()

    # 获取缓存数据
    def get_data(self):
        # 初始化“数据是否有变化”变量
        self.data_changed = False

        # 从缓存中读取数据
        data = CacheUtil.Get(MISSION_DATA_CACHE_KEY)

        # 如果缓存中的数据为空，则重新调用API查询数据
        if data is None:
            # 调用后端API
            apis.API_GET_PRODUCT_MISSIONS(self)
            # 从后端返回的数据中提取需要的数据
            data = self.call_back_variables["data"]
            # 将数据存入缓存
            CacheUtil.Set(MISSION_DATA_CACHE_KEY, data, timeout = MISSION_DATA_CACHE_TIME_OUT)
            # 删除临时参数
            del self.call_back_variables

        # 如果处理后返回的数据还是空，则需要返回一个空数组，方便判断
        if data is None:
            data = []

        # 判断数据是否有变化
        if self.data is None or len(data) != len(self.data):
            self.data_changed = True
        else:
            for index in range(len(data)):
                if data[index] is not self.data[index]:
                    self.data_changed = True

        # 将数据存到对象中
        self.data = data
        return data

    def get_button_size(self):
        width, height = self.GetSize()
        return width / 6.5, height / 10

    def scroll_thumbtrack(self, event):
        scroll_bar = event.GetEventObject()
        print(scroll_bar.GetThumbPosition())
        event.Skip()

    def button_on_click(self, event):
        print("点击添加任务：这里要加跳转到任务管理界面的逻辑，因为没有任务说明需要新增任务，所以直接跳转过去")
        event.Skip()

    # 内容块的点击事件
    def mission_block_click(self, event):
        eventObj = event.GetEventObject()
        print("mission name: ", eventObj.mission_name)

        # 点击事，隐藏主界面，跳转到操作员实际操作的工作台界面
        topParent = CommonUtils.GetTopParent(eventObj)
        topParent.show_all(False)

        if eventObj.view is None:
            eventObj.view = WorkplaceView(topParent, wx.ID_ANY, pos = (0, 0),
                                          size = topParent.GetClientSize(), title = self.menu_name)
        else:
            eventObj.view.Show()


# 显示所有任务块的panel，用于设置GridSizer，高度可以超出父panel，超出时使用滚动条
class MissionBlocksPanel(wx.Panel):
    def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "MissionBlocksPanel", grid_rows = 0):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.grid_rows = grid_rows
        self.Bind(wx.EVT_SIZE, self.on_size)

    def SetGridRows(self, grid_rows):
        self.grid_rows = grid_rows

    def on_size(self, event):
        p_width, p_height = self.GetParent().GetSize()
        new_width = p_width
        new_height = p_height * (MISSION_HEIGHT_RATIO / 100) * self.grid_rows
        self.SetSize(new_width, new_height)
        event.Skip()


# 每一个单独的任务块panel，封装起来更易读、易用、易维护
class MissionBlock(widgets.CustomBorderPanel):
    def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 mission_name = None, mission_image = None):
        widgets.CustomBorderPanel.__init__(self, parent, id, border_color = configs.COLOR_CONTENT_BLOCK_BORDER_1,
                                           pos = pos, size = size, border_thickness = 1, margin = 0, name = "MissionBlock")
        self.SetBackgroundColour(configs.COLOR_CONTENT_BLOCK_BACKGROUND)
        self.mission_name = mission_name
        self.mission_image = mission_image

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.inner_sizer.Add(self.panel, 1, wx.EXPAND | wx.ALL)

        self.panel.Bind(wx.EVT_SIZE, self.on_panel_size)
        self.panel.Bind(wx.EVT_PAINT, self.on_panel_paint)
        self.panel.Bind(wx.EVT_LEFT_UP, self.process_parent_event)

    # 调用父类对应的事件（因为这个组件其实是真正的自定义组件（一个panel假装的）的内部组件，
    # 正常情况下会在父组件的上方，因此事件触发基本上都是触发此对象，而实际代码逻辑中绑定时都是绑定父对象，因此要向上传递
    def process_parent_event(self, event):
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)
        event.Skip()

    def on_panel_size(self, event):
        p_width, p_height = self.GetSize()
        if p_width > 330 or p_height > 210:
            self.SetBorderThickness(2)
        else:
            self.SetBorderThickness(1)
        self.panel.Layout()
        event.Skip()

    # 不知道为啥用sizer搞不定了，直接用DC画了
    # this fucking thing wasted me a whole day
    def on_panel_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self.panel))
        width, height = self.panel.GetSize()
        wx_image = self.mission_image.ConvertToImage()
        bw, bh = math.ceil(width / 10 * 8), math.ceil(height / 10 * 8)
        wx_image.Rescale(bw, bh, wx.IMAGE_QUALITY_BILINEAR)
        bitmap = wx_image.ConvertToBitmap()

        dc.SetTextForeground(configs.COLOR_TEXT_THEME)
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        font_temp.SetPointSize(math.ceil(width / 50 + height / 30) + 1)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(self.mission_name)

        dc.DrawBitmap(bitmap, (width - bw) // 2, (height - bh) // 2 - (th / 2) / 2, bitmap.GetMask() is not None)
        dc.DrawText(self.mission_name, (width - tw) // 2, height / 10 * 8 + (height / 10 * 2 - th / 2) // 2)

        # 删除DC
        del dc

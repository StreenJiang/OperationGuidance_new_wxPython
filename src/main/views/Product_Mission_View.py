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
MISSION_GAP_RATIO = 4
# 每个任务的高度占content_panel的多少比例
MISSION_HEIGHT_RATIO = 33
# 展示区域的行达到多少就需要滚动条
MISSION_ROWS_SCROLL = 3


# 产品任务展示界面
class ProductMissionView(widgets.CustomViewPanel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "ProductMissionView", menu_name = ""):
        widgets.CustomViewPanel.__init__(self, parent, id, pos, size, style, name, menu_name)
        self.menu_name = menu_name
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

        self.initialize()

    def initialize(self):
        # 从缓存中取出数据
        data = self.get_data()
        # data = []

        if len(data) == 0:
            # 如果没有任何任务，则提供一个跳转到任务管理界面添加任务的按钮
            self.create_add_button()
            self.add_mission_button.Center()
            self.add_mission_button.Refresh()
        else:
            self.create_block_panel(data)

    # 创建“添加任务”按钮
    def create_add_button(self):
        self.add_mission_button = widgets.CustomRadiusButton(self, wx.ID_ANY, label = "点击添加任务",
                                                             font_color = configs.COLOR_BUTTON_TEXT,
                                                             background_color = configs.COLOR_BUTTON_BACKGROUND,
                                                             clicked_color = configs.COLOR_BUTTON_CLICKED,
                                                             button_size_type = widgets.BUTTON_SIZE_TYPE_BIG,
                                                             button_type = widgets.BUTTON_TYPE_NORMAL,
                                                             radius = 3)
        self.add_mission_button.Bind(wx.EVT_LEFT_DOWN, self.button_on_click)

    # 创建任务展示块的列表
    def create_block_panel(self, data):
        self.block_panel = MissionBlocksPanel(self, wx.ID_ANY)
        # 创建展示块
        for index in range(len(data)):
            mission_obj = data[index]
            mission_name = mission_obj.GetMissionName()
            mission_image = mission_obj.GetMissionProductSides()[0].GetSideImage().GetImageOriginal()
            mission_image = CommonUtils.PILImageToWxImage(mission_image).ConvertToBitmap()
            mission_block = self.block_panel.add_block(mission_name = mission_name, mission_image = mission_image)
            mission_block.Bind(wx.EVT_LEFT_UP, self.mission_block_click)
            self.mission_blocks.append(mission_block)


    # 重写父类的on_size方法，并且不需要重复绑定，否则会出现多次调用
    def on_size(self, event):
        self.SetMargin(self.GetSize()[1] * 0.02)
        super().on_size(event)

        # 手动触发children的on_size事件
        if self.block_panel is not None:
            event.SetEventObject(self.block_panel)
            self.block_panel.GetEventHandler().ProcessEvent(event)

    def on_paint(self, event):
        # 从缓存中取出数据
        data = self.get_data()
        # data = []

        # 如果没有任何任务，则提供一个跳转到任务管理界面添加任务的按钮
        if len(data) == 0:
            if self.add_mission_button is None:
                self.create_add_button()
            # 计算添加按钮的size
            self.add_mission_button.SetSize(self.calc_add_button())
            # 刷新按钮至中间的位置
            self.add_mission_button.Center()
            self.add_mission_button.Refresh()
            # 按钮有可能隐藏了，所以调用一下show方法
            self.add_mission_button.Show()
            # 如果之前有创建任务展示块，则销毁（这种情况下采用销毁措施会使软件整体性能更好）
            if self.block_panel is not None:
                self.block_panel.Destroy()
                self.block_panel = None
        else:
            # 如果之前有创建添加任务按钮，则销毁（暂时用不到就销毁吧，提升一下性能）
            if self.add_mission_button is not None:
                self.add_mission_button.Destroy()
                self.add_mission_button = None
            # 如果数据有更新，则需要新创建任务展示块
            if self.data_changed:
                # 如果之前创建了则先销毁，重新画
                if self.block_panel is not None:
                    self.block_panel.Destroy()
                self.create_block_panel(data)

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

    def calc_add_button(self):
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


# 显示所有任务块的panel，用于显示、管理所有任务展示块；高度可以超出父panel，超出时使用滚动条
class MissionBlocksPanel(wx.Panel):
    def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "MissionBlocksPanel"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.blocks = []

        self.Bind(wx.EVT_SIZE, self.on_size)

    def add_block(self, mission_name, mission_image):
        # 创建任务展示块
        mission_block = MissionBlock(self, wx.ID_ANY, mission_name = mission_name, mission_image = mission_image)
        # 初始化视图变量
        mission_block.view = None
        # 存入数组
        self.blocks.append(mission_block)
        return mission_block

    def on_size(self, event):
        p_width, p_height = self.GetParent().GetSize()
        blocks_count = len(self.blocks)
        new_width = p_width
        # 计算当前block的数量需要摆几行，公式：向下取整(blocks_count / MISSION_COLUMNS)
        rows = math.ceil(blocks_count / MISSION_COLUMNS)
        # 计算每个block之间的gap，公式：gap += panel宽度 x block横向gap所占比例
        gap = new_width * MISSION_GAP_RATIO / 100
        # 计算panel的高度，公式：new_height = 父panel高度 x block高度所占比例 x 需要多少行
        new_height = p_height * (MISSION_HEIGHT_RATIO / 100) * rows + gap * (rows - 1)
        # 还需要加上每行之间的gap，
        self.SetSize(new_width, new_height)

        if blocks_count > 0:
            for index in range(len(self.blocks)):
                block = self.blocks[index]
                # 计算任务展示块的size和pos
                b_size, b_pos = self.calc_block(index, rows, gap)
                block.SetSize(b_size)
                block.SetPosition(b_pos)

        event.Skip()

    def calc_block(self, index, rows, gap):
        w, h = self.GetSize()
        # 计算block的宽度，公式：b_w = panel宽度 - 每个block之间的gap * 3
        b_w = (w - gap * (MISSION_COLUMNS - 1)) // MISSION_COLUMNS
        b_h = math.floor(h - gap * (rows - 1)) / rows
        b_x = (b_w + gap) * (index % MISSION_COLUMNS)
        b_y = (b_h + gap) * math.floor(index / MISSION_COLUMNS)
        return (b_w, b_h), (b_x, b_y)


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

import math

import wx

import src.main.widgets as widgets
import src.main.configs as configs
from src.main.controllers import apis
from src.main.utils import CommonUtils, CacheUtil
from src.main.views.Content_Workplace import WorkplaceView

# 任务列表展示界面的gridSizer的列数固定为4
MISSION_COLUMNS = 4
# 每个任务之间的间隔占content_panel宽度的多少比例
MISSION_GAP_RATIO = 40
# 每个任务的高度占content_panel的多少比例
MISSION_HEIGHT_RATIO = 3
# 展示区域的行达到多少就需要滚动条
MISSION_ROWS_SCROLL = 3


# 产品任务展示界面
class ProductMissionView(widgets.CustomViewPanel):
    def __init__(self, parent = None, id = wx.ID_ANY,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "ProductMissionView"):
        widgets.CustomViewPanel.__init__(self, parent, id, pos, size, style, name)
        self.SetBackgroundColour(wx.BLUE)
        self.menu_name = parent.menu_name
        self.call_back_variables = None
        self.add_mission_button = None
        self.content_blocks = None
        self.has_scroller = False
        self.size_cache = None
        self.need_redraw = True

        # 数据及缓存相关参数
        self.data_key = "missions_data"
        self.data_timeout = 2 # 数据缓存过期时间（秒）

        self.parent = self.GetParent()
        self.parent.scroll_bar = None

        self.is_painting = False
        # 由于父类CustomViewPanel绑定了EVT_SIZE事件，如果子类再绑定则会替换掉，父类不再触发该事件，会导致size出错
        self.Bind(wx.EVT_PAINT, self.on_paint)

    # 获取缓存数据
    def get_data(self):
        data = CacheUtil.Get(self.data_key)
        if data is None:
            # 调用后端API
            apis.API_GET_PRODUCT_MISSIONS(self)
            # 从后端返回的数据中提取需要的数据
            data = self.call_back_variables["data"]
            # dataTemp = []
            # 将数据存入缓存
            CacheUtil.Set(self.data_key, data, timeout = self.data_timeout)
            # 删除临时参数
            del self.call_back_variables
        return data

    def on_paint(self, event):
        data = self.get_data()
        print("on_paint data: ", data)






        # if not self.is_painting:
        #     # call later
        #     self.is_painting = True
        #     wx.CallLater(200, self.call_later, event)
        event.Skip()

    def call_later(self, event):
        # 经过CallLater异步调用后，event丢失了原本的EventObject，因此需要重新设置一下
        event.SetEventObject(self)
        # 调用后端API
        apis.API_GET_PRODUCT_MISSIONS(event)
        # 从后端返回的数据中提取需要的数据
        dataTemp = self.call_back_variables["data"]
        # dataTemp = []

        newSize = self.parent.GetSize()
        parentSizer = self.parent.GetSizer()
        parentStaticBox = parentSizer.GetStaticBox()

        # 根据内容调整content_panel的尺寸
        margin = parentStaticBox.margin * 2
        contentNewSize = newSize - (margin * 2, margin * 2)

        # 根据后端返回的数据判断该如何绘制当前展示的画面
        if len(dataTemp) > 0:
            # 记录一些参数用于判断是否需要刷新界面
            if self.size_cache is not None:
                if self.has_scroller:
                    if self.size_cache == contentNewSize - (configs.SIZE_SCROLL_BAR, 0):
                        self.need_redraw = False
                elif self.size_cache == contentNewSize:
                    self.need_redraw = False

            if self.data is not None and len(self.data) != len(dataTemp):
                self.need_redraw = True

            # 判断是否需要重新绘制界面
            if not self.need_redraw:
                # 重置参数
                self.need_redraw = True
                self.is_painting = False
                return

            self.data = dataTemp

            # 根据行数判断是否需要滚动条
            mission_count = len(self.data)
            rows = math.ceil(mission_count / MISSION_COLUMNS)
            if rows >= MISSION_ROWS_SCROLL:
                self.has_scroller = True

            if self.has_scroller:  # 如果有滚动条，content_panel的尺寸也要调整
                contentNewSize -= (configs.SIZE_SCROLL_BAR, 0)
            gapBetweenMission = round(contentNewSize[0] / MISSION_GAP_RATIO)
            elementSize = self.get_mission_item_size(contentNewSize, gapBetweenMission)

            if self.GetSizer() is None:
                boxSizer = wx.BoxSizer(wx.VERTICAL)
                parentStaticBox.has_scroller = self.has_scroller

                self.content_blocks = []
                for index in range(len(self.data)):
                    wx.CallAfter(self.create_mission_block, index, self.data[index], gapBetweenMission, elementSize)
                    # self.create_mission_block(index, self.data[index], gapBetweenMission, elementSize)

                self.SetSizer(boxSizer)
                boxSizer.Fit(self)
            else:
                for index in range(len(self.content_blocks)):
                    wx.CallAfter(self.resize_mission_block, index, self.content_blocks[index], gapBetweenMission, elementSize)
                    # self.resize_mission_block(index, self.content_blocks[index], gapBetweenMission, elementSize)
                self.GetSizer().Fit(self)

            # 如果需要滚动条，则增加滚动条
            if self.has_scroller:
                if self.parent.scroll_bar is not None:
                    self.parent.scroll_bar.Destroy()

                self.parent.scroll_bar = wx.ScrollBar(self.parent, pos = (newSize[0] - 16, 0),
                                                      size = (0, newSize[1]), style = wx.SB_VERTICAL)
                self.parent.scroll_bar.Bind(wx.EVT_SCROLL_THUMBTRACK, self.scroll_thumbtrack)
                self.parent.scroll_bar.SetScrollbar(0, 3, 10, 2)
                self.parent.scroll_bar.Layout()
                self.parent.scroll_bar.Fit()

            # 所有内容设置完毕再刷新主界面
            self.reset_and_refresh(margin, contentNewSize)
        else:

            if self.add_mission_button is None:
                self.add_mission_button = widgets.CustomRadiusButton(self, wx.ID_ANY, label = "点击添加任务",
                                                                     font_color = configs.COLOR_BUTTON_TEXT,
                                                                     background_color = configs.COLOR_BUTTON_BACKGROUND,
                                                                     clicked_color = configs.COLOR_BUTTON_CLICKED,
                                                                     button_size_type = widgets.BUTTON_SIZE_TYPE_BIG,
                                                                     button_type = widgets.BUTTON_TYPE_NORMAL,
                                                                     size = self.get_button_size(newSize), radius = 3)
                self.add_mission_button.Bind(wx.EVT_LEFT_DOWN, self.button_on_click)
            else:
                self.add_mission_button.SetSize(self.get_button_size(newSize))

            # 先刷新主界面然后再刷新按钮在上面的位置
            self.reset_and_refresh(margin, contentNewSize)
            self.add_mission_button.Center()
            self.add_mission_button.Refresh()

        # 记录当前尺寸
        self.size_cache = contentNewSize
        self.is_painting = False

    def reset_and_refresh(self, margin, contentNewSize):
        # 设置content_panel的位置和尺寸（放在这里设置是因为还需要根据内容调整尺寸）
        self.SetPosition((margin, margin))
        self.SetSize(contentNewSize)
        # self.SetBackgroundColour(wx.RED)
        self.Refresh()

    def get_button_size(self, content_size):
        return content_size[0] / 6.5, content_size[1] / 10

    def get_mission_item_size(self, content_size, gap_between_mission):
        return (content_size[0] - gap_between_mission * 5) / MISSION_COLUMNS, content_size[1] / MISSION_HEIGHT_RATIO

    def scroll_thumbtrack(self, event):
        scroll_bar = event.GetEventObject()
        print(scroll_bar.GetThumbPosition())
        event.Skip()

    def button_on_click(self, event):
        print("点击添加任务：这里要加跳转到任务管理界面的逻辑，因为没有任务说明需要新增任务，所以直接跳转过去")
        event.Skip()

    def create_mission_block(self, index, missionObj, gapBetweenMission, elementSize):
        # 初始化工作台操作界面
        missionObj.view = None
        # 创建展示内容块
        customPanel = widgets.CustomBorderPanel(self, wx.ID_ANY, border_color = configs.COLOR_CONTENT_BLOCK_BORDER_1,
                                                pos = (gapBetweenMission, gapBetweenMission), border_thickness = 1,
                                                size = elementSize)
        customPanel.SetBackgroundColour(configs.COLOR_CONTENT_BLOCK_BACKGROUND)
        customPanel.missionObj = missionObj
        customPanel.bitmapPanel = None
        customPanel.missionNameStaticText = None

        # 展示只需要【任务名称】和【产品面首页图片】
        customPanel.missionName = missionObj.GetMissionName()
        customPanel.sideImage = missionObj.GetMissionProductSides()[0].GetSideImage().GetImageOriginal()
        # 增加一个覆盖整个内容块的空panel，用于绑定点击事件，保证内容块的所有区域都可以出发点击事件
        customPanel.clickPanel = wx.Panel(customPanel, wx.ID_ANY)

        customPanel.Show(False)
        # 设置内容块的位置、尺寸
        self.resize_mission_block(index, customPanel, gapBetweenMission, elementSize)

        def show_later():
            customPanel.Show()
        wx.CallLater(10, show_later)

        # 绑定点击事件
        customPanel.clickPanel.Bind(wx.EVT_LEFT_UP, self.mission_block_click)

        # 将内容块塞到数组里，方便后续操作
        self.content_blocks.append(customPanel)

    # 设置内容块的位置、尺寸
    def resize_mission_block(self, index, customPanel, gapBetweenMission, elementSize):
        # 修改内容页面的尺寸
        panelX = gapBetweenMission * (index % MISSION_COLUMNS + 1) + elementSize[0] * (index % MISSION_COLUMNS)
        panelY = gapBetweenMission * (math.floor(index / MISSION_COLUMNS) + 1) + elementSize[1] * (math.floor(index / MISSION_COLUMNS))
        if elementSize[0] > 330 or elementSize[1] > 210:
            customPanel.SetBorderThickness(2)
        else:
            customPanel.SetBorderThickness(1)
        customPanel.SetPosition((panelX, panelY))
        customPanel.SetSize(elementSize)

        panelWidth, panelHeight = elementSize
        content_sizer = customPanel.GetSizer()

        # 设置图片的位置、大小
        if customPanel.bitmapPanel is None:
            # 任务产品面的第一个面（展示块的缩略图）
            customPanel.bitmapPanel = widgets.CustomBorderPanel(customPanel, wx.ID_ANY,
                                                                border_color = configs.COLOR_CONTENT_BLOCK_BORDER_3,
                                                                border_thickness = 1)
            content_sizer.Add(customPanel.bitmapPanel)
            customPanel.bitmapPanel.bitmap = wx.StaticBitmap(customPanel.bitmapPanel, wx.ID_ANY)
        # 设置自适应参数
        imagePanel = customPanel.bitmapPanel
        bitmap = customPanel.bitmapPanel.bitmap
        sideWxImage = CommonUtils.PILImageToWxImage(customPanel.sideImage)
        border_width, border_height = panelWidth / 5 * 4, panelHeight / 10 * 7
        sideWxImage.Rescale(border_width, border_height, wx.IMAGE_QUALITY_BILINEAR)
        imagePanel.SetSize(border_width, border_height)
        imagePanel.SetPosition(((panelWidth - border_width) / 2, (panelHeight - border_height) / 3))
        imagePanel.SetBorderThickness(customPanel.border_thickness)
        bitmap.SetBitmap(sideWxImage.ConvertToBitmap())

        # 设置任务名称的位置、字体颜色、字体大小
        if customPanel.missionNameStaticText is None:
            customPanel.missionNameStaticText = wx.StaticText(customPanel, wx.ID_ANY, label = customPanel.missionName)
            content_sizer.Add(customPanel.missionNameStaticText)
            customPanel.missionNameStaticText.SetForegroundColour(configs.COLOR_TEXT_THEME)
        # 设置自适应参数
        text = customPanel.missionNameStaticText
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        font_temp.SetPointSize(int(panelWidth / 50 + panelHeight / 30) + 1)
        text.SetFont(font_temp)
        tw, th = text.GetTextExtent(text.GetLabel())
        text.SetSize(tw, th)
        text.SetPosition(((panelWidth - tw) / 2, panelHeight / 10 * 8.5))

        # 添加了一个用于点击事件的空的panel，在这里保证它的大小和父panel一致
        customPanel.clickPanel.SetSize(elementSize)

        # 刷新
        customPanel.Refresh()

    # 内容块的点击事件
    def mission_block_click(self, event):
        eventObj = event.GetEventObject().GetParent()
        missionObj = eventObj.missionObj
        print("mission name: ", missionObj.GetMissionName())

        # 点击事，隐藏主界面，跳转到操作员实际操作的工作台界面
        topParent = CommonUtils.GetTopParent(eventObj)
        topParent.show_all(False)

        if missionObj.view is None:
            missionObj.view = WorkplaceView(topParent, wx.ID_ANY, pos = (0, 0),
                                            size = topParent.GetClientSize(), title = self.menu_name)
        else:
            missionObj.view.Show()




import math

import wx
import wx.lib.buttons as buttons
from PIL import ImageColor

import src.main.configs as configs
from src.main.exceptions.Custom_Exception import LengthTooLongException
from src.main.utils import CommonUtils


# CustomGenBitmapTextToggleButton： custom_style
BUTTON_STYLE_HORIZONTAL = 1
BUTTON_STYLE_VERTICAL = 2
# 自定义图标文本开关按钮
class CustomGenBitmapTextToggleButton(buttons.GenBitmapTextToggleButton):
    def __init__(self, parent, id = -1, bitmap = wx.NullBitmap, label = '',
                 label_color = "#FFFFFF", toggle_color = "#000000", background_color = "#000000",
                 is_toggled = False, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator, custom_style = BUTTON_STYLE_HORIZONTAL,
                 name = "CustomGenBitmapTextToggleButton"):
        # 按钮的中文文本的长度校验
        if custom_style == BUTTON_STYLE_VERTICAL and len(label) > configs.LENGTH_MAIN_MENU:
            raise LengthTooLongException("Length of main menu label[%s] too long, no more than %d" % (label, configs.LENGTH_MAIN_MENU))
        elif len(label) > configs.LENGTH_CHILD_MENU:
            raise LengthTooLongException("Length of child menu label[%s] too long, no more than %d" % (label, configs.LENGTH_CHILD_MENU))
        # 调用父类的构造函数
        buttons.GenBitmapButton.__init__(self, parent, id, bitmap, pos, size, style, validator, name)
        # 初始化实例变量
        self.label_color = label_color
        self.is_toggled = is_toggled
        self.SetLabel(label)
        self.custom_style = custom_style
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)
        self.SetBackgroundColour(background_color)
        # 按钮激活时的颜色（初始化配置的，这个是固定的）
        self.toggle_color = toggle_color
        self.background_color = background_color

        # 设置初始状态
        self.SetToggle(is_toggled)

        # 绑定事件，实现鼠标悬浮时改变背景颜色效果，移出时恢复原背景颜色（针对激活与否有不同的效果）
        self.Bind(wx.EVT_ENTER_WINDOW, self.process_parent_event)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.process_parent_event)
        self.Bind(wx.EVT_LEFT_DOWN, self.process_parent_event)
        self.Bind(wx.EVT_LEFT_UP, self.process_parent_event)
        self.Bind(wx.EVT_MOTION, self.process_parent_event)

    # 调用父类对应的事件（因为这个组件其实是真正的自定义组件（一个panel假装的）的内部组件，
    # 正常情况下会在父组件的上方，因此事件触发基本上都是触发此对象，而实际代码逻辑中绑定时都是绑定父对象，因此要向上传递
    def process_parent_event(self, event):
        event.SetEventObject(self.GetParent())
        self.GetParent().GetEventHandler().ProcessEvent(event)
        event.Skip()

    def SetToggle(self, flag):
        if flag:
            self.SetBackgroundColour(self.toggle_color)
        else:
            self.SetBackgroundColour(self.background_color)
        super().SetToggle(flag)

    def GetLabel(self):
        return super().GetLabel()

    # 重写绘制方法
    def OnPaint(self, event):
        (width, height) = self.GetClientSize()
        x1 = y1 = 0
        x2 = width - 1
        y2 = height - 1
        dc = wx.PaintDC(self)
        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            # 这里加了一行代码：让背景画刷跟背景颜色一致（不知道为啥这个颜色默认是不一样的）
            # 这个颜色会在按钮被按住时显示出来，然后会发现跟本身的背景颜色不一样
            brush.SetColour(self.GetBackgroundColour())
            dc.SetBackground(brush)
            dc.Clear()
        self.DrawBezel(dc, x1, y1, x2, y2)
        self.DrawLabel(dc, width, height)
        if self.hasFocus and self.useFocusInd:
            self.DrawFocusIndicator(dc, width, height)

    def DrawLabel(self, dc, width, height, dx = 0, dy = 0):
        if width <= 0 or height <= 0:
            return
        bmp = self.bmpLabel
        if bmp is not None:  # if the bitmap is used
            if self.bmpDisabled and not self.IsEnabled():
                bmp = self.bmpDisabled
            if self.bmpFocus and self.hasFocus:
                bmp = self.bmpFocus
            if self.bmpSelected and not self.up:
                bmp = self.bmpSelected

            # make bitmap adjust the size of button itself
            if self.custom_style == BUTTON_STYLE_HORIZONTAL:
                img = bmp.ConvertToImage()
                img.Rescale(math.ceil(height / 3 + width / 45), math.ceil(height / 3 + width / 45), wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
            else:
                img = bmp.ConvertToImage()
                img.Rescale(math.ceil(height / 2.7), math.ceil(height / 2.7), wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)

            bw, bh = bmp.GetWidth(), bmp.GetHeight()
            if not self.up:
                dx = dy = self.labelDelta
            hasMask = bmp.GetMask() is not None
        else:
            bw = bh = 0  # no bitmap -> size is zero
            hasMask = False

        if self.custom_style == BUTTON_STYLE_HORIZONTAL:
            # handle the font, make it adjust the size
            font_temp = self.GetFont()
            font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
            font_temp.SetPointSize(int(width / 25 + height / 9) + 1)
            dc.SetFont(font_temp)
            dc.SetTextForeground(self.label_color)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_x = width / 15 + (width - tw) / 20 # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, pos_x, (height - bh - (bh / 100 * 10)) / 2 + dy, hasMask)  # draw bitmap if available
                pos_x = pos_x + (width / 15)  # extra spacing from bitmap

            dc.DrawText(label, pos_x + bw + dx, (height - th) / 2 + dy)  # draw the text
        else:
            # handle the font, make it adjust the size
            font_temp = self.GetFont()
            font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
            font_temp.SetPointSize(int(height / 9) + 1)
            dc.SetFont(font_temp)
            dc.SetTextForeground(self.label_color)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_y = (height - bh - th) / 2 + dy  # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, (width - bw - (bw / 100 * 10)) / 2 + dx, pos_y, hasMask)  # draw bitmap if available
                pos_y = pos_y + (height / 50)  # extra spacing from bitmap

            dc.DrawText(label, (width - tw) / 2 + dx, pos_y + bh + dy)  # draw the text


# 自定义菜单按钮（用panel模拟按钮，以实现子菜单的左侧选中效果）
class CustomMenuButton(wx.Panel):
    def __init__(self, parent, id = -1, bitmap = wx.NullBitmap, label = '',
                 label_color = "#FFFFFF", is_toggled = False, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator, custom_style = BUTTON_STYLE_HORIZONTAL,
                 background_color = "#000000", toggle_color = "#000000", need_trigger_bar = False,
                 name = "CustomMenuButton"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size, name = name)
        self.button = None
        self.bitmap = bitmap
        self.label = label
        self.label_color = label_color
        self.style = style
        self.custom_style = custom_style
        self.background_color = background_color
        self.toggle_color = toggle_color
        self.is_toggled = is_toggled
        self.validator = validator
        self.need_trigger_bar = need_trigger_bar # 按钮激活后是否需要一个激活的条状效果

        # 按钮是否为激活状态的标识
        self.toggle_flag = False
        # 背景颜色
        self.background_color = background_color
        # 将鼠标悬浮时的颜色设置为背景颜色变淡RBG值的10%
        colorList = []
        if isinstance(background_color, str):
            colorList = list(ImageColor.getcolor(background_color, "RGBA"))
        elif isinstance(background_color, wx.Colour):
            colorList = list(background_color)
        enter_color = []
        for each in colorList:
            each += (255 / 10)
            if each < 0:
                each = 0
            enter_color.append(each)
        self.enter_color = wx.Colour(enter_color)
        # 初始化鼠标移出时的颜色
        self.leave_color = background_color
        # 按钮激活时的颜色
        self.s_toggle_color = None

        if is_toggled and need_trigger_bar:
            self.SetToggle(is_toggled)
            self.SetBackgroundColour(label_color)
            self.leave_color = toggle_color

        self.SetLabel(label)
        # 根据parent重新设定按钮组件的大小
        self.Bind(wx.EVT_SIZE, self.on_size)
        # 绑定事件，实现鼠标悬浮时改变背景颜色效果，移出时恢复原背景颜色（针对激活与否有不同的效果）
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    def on_size(self, event):
        width, height = self.GetSize()
        if self.custom_style == BUTTON_STYLE_VERTICAL:
            self.SetSize(height, height)
        else:
            self.SetSize(width, height)
        # 在这里初始化就不会导致panel在被初始化时，因bitmap是初始大小，而导致整个布局出错
        if self.button is None:
            # the position here for the button should be (0, 0),
            # otherwise the button will disappear if it locates outside the outer panel.
            self.button = CustomGenBitmapTextToggleButton(self, wx.ID_ANY, self.bitmap, self.label,
                                                          self.label_color, self.toggle_color, self.background_color,
                                                          self.is_toggled, (0, 0), (height, height), self.style,
                                                          self.validator, self.custom_style, self.GetName())
        event.Skip()

    def on_enter(self, event):
        self.leave_color = self.background_color
        if self.GetToggle():
            self.leave_color = self.toggle_color
        else:
            self.toggle_flag = False
            self.SetBackgroundColour(self.enter_color)
        event.Skip()

    def on_leave(self, event):
        self.SetBackgroundColour(self.leave_color)
        event.Skip()

    # 先绑定的事件后执行，所以在这个事件执行前，已经修改了背景颜色
    def on_left_up(self, event):
        if self.GetToggle():
            if not self.toggle_flag:
                self.toggle_flag = True
                self.leave_color = self.toggle_color
        event.Skip()

    # 重写SetBackgroundColour方法，以达到给panel和按钮分别着色的目的
    def SetBackgroundColour(self, colour):
        if self.custom_style == BUTTON_STYLE_HORIZONTAL:
            if self.button is not None and self.button.GetToggle() and self.need_trigger_bar:
                super().SetBackgroundColour(self.button.label_color)
            else:
                super().SetBackgroundColour(colour)
        if self.button is not None:
            self.button.SetBackgroundColour(colour)
        self.Refresh()

    # 新建SetToggle，因为panel没有这个方法，实现调用按钮的SetToggle方法
    def SetToggle(self, flag):
        if self.button is not None:
            self.button.SetToggle(flag)
        if flag:
            self.SetBackgroundColour(self.toggle_color)
        else:
            self.SetBackgroundColour(self.background_color)
        self.is_toggled = flag

    def GetToggle(self):
        if self.button is not None:
            self.is_toggled = self.button.GetToggle()
        return self.is_toggled

    # 重写SetSize方法，以达到给panel和按钮分别设置size的目的
    def SetSize(self, *args):
        width, height = (0, 0)

        if len(args) == 1:
            width, height = args[0][0], args[0][1]
        elif len(args) == 2:
            width, height = args

        if width == -1 or height == -1:
            return

        super().SetSize(width, height)
        if self.button is not None:
            self.SetButtonSize(width, height)

    def SetButtonSize(self, width, height):
        if self.custom_style == BUTTON_STYLE_HORIZONTAL and self.need_trigger_bar:
            width_reduction = math.floor(width * 0.05)
            width, height = (width - width_reduction, height)
            self.button.SetPosition((width_reduction, 0))
        else:
            pass
        self.button.SetSize(width, height)


# 自定义圆角按钮的类型
BUTTON_TYPE_NORMAL = 1
BUTTON_TYPE_SWITCH = 2
BUTTON_SIZE_TYPE_NORMAL = 101
BUTTON_SIZE_TYPE_BIG = 102

# 自定义圆角按钮
class CustomRadiusButton(buttons.GenBitmapButton):
    def __init__(self, parent, id = -1, label = "",
                 font_color = "#FFFFFF", background_color = "#000000", clicked_color = "#000000",
                 focused_alpha = 75,  # 透明度（默认75，单位%）
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 radius = 0, button_size_type = BUTTON_SIZE_TYPE_NORMAL, button_type = BUTTON_TYPE_NORMAL,
                 style = 0, validator = wx.DefaultValidator, name = "genbutton"):
        buttons.GenBitmapButton.__init__(self, parent, id, None, pos, size, style, validator, name)
        self.label = label
        self.font_color = wx.Colour(font_color)
        self.background_color = wx.Colour(background_color)
        self.clicked_color = wx.Colour(clicked_color)
        self.focused_alpha = focused_alpha
        self.button_size_type = button_size_type
        self.radius = radius
        self.button_type = button_type

        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)
        self.SetBitmapLabel(self.createBitMap(label, self.font_color, self.background_color, None, radius))
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())

        self.focused = False
        self.is_key_down = False
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)

    def set_custom_font(self, button_size_type):
        self.button_size_type = button_size_type
        self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, None, self.radius))

    def OnSize(self, event):
        if self.is_key_down:
            self.OnKeyDown(event)
        else:
            self.OnLeftUp(event)

    def OnMotion(self, event):
        pass

    def on_enter(self, event):
        if self.button_type == BUTTON_TYPE_NORMAL:
            if not self.focused:
                self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, self.focused_alpha, self.radius))
                self.Refresh()
                self.focused = True
        elif self.button_type == BUTTON_TYPE_SWITCH:
            if not self.focused:
                if not self.is_key_down:
                    self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, self.focused_alpha, self.radius))
                else:
                    self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.clicked_color, self.focused_alpha, self.radius))
                self.Refresh()
                self.focused = True
        event.Skip()

    def on_leave(self, event):
        if self.button_type == BUTTON_TYPE_NORMAL:
            self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, None, self.radius))
        elif self.button_type == BUTTON_TYPE_SWITCH:
            if self.is_key_down:
                self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.clicked_color, None, self.radius))
            else:
                self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, None, self.radius))
        self.Refresh()
        self.focused = False
        event.Skip()

    def OnLeftDown(self, event):
        if not self.is_key_down:
            self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.clicked_color, None, self.radius))
        else:
            self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, None, self.radius))

        # buttons.GenBitmapButton.OnLeftDown(self, event)
        if (not self.IsEnabled()) or self.HasCapture():
            return
        # self.up = False
        self.CaptureMouse()
        self.SetFocus()
        self.Refresh()
        if self.button_type == BUTTON_TYPE_NORMAL:
            self.is_key_down = True
        elif self.button_type == BUTTON_TYPE_SWITCH:
            self.is_key_down = not self.is_key_down
        event.Skip()

    def OnLeftUp(self, event):
        if self.button_type == BUTTON_TYPE_NORMAL:
            self.is_key_down = False
            if self.focused:
                self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, self.focused_alpha, self.radius))
            else:
                self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, None, self.radius))
        elif self.button_type == BUTTON_TYPE_SWITCH:
            pass
        super().OnLeftUp(event)

    # 画bitmap
    def createBitMap(self, label, font_color, background_color, focused_alpha, radius):
        width, height = self.GetSize()
        bitmap = wx.Bitmap(width, height, depth = 32)

        dc = wx.MemoryDC(bitmap)
        # 让背景全黑，方便后续设置透明色
        dc.SetBackground(wx.Brush(wx.BLACK))
        dc.Clear()

        # 设置画笔、画刷的颜色
        pen = wx.Pen(background_color, 1)
        dc.SetPen(pen)
        brush = wx.Brush(background_color)
        dc.SetBrush(brush)

        # 画出bitmap的形状
        dc.DrawRoundedRectangle(0, 0, width, height, radius)

        # Draw the text in the rounded rectangle
        dc.SetTextForeground(font_color)
        w, h = dc.GetSize()
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        # calculate the size of font according to the content size
        if self.button_size_type == BUTTON_SIZE_TYPE_BIG:
            font_temp.SetPointSize(int(w / 30 + h / 9) + 1)
        elif self.button_size_type == BUTTON_SIZE_TYPE_NORMAL:
            font_temp.SetPointSize(int(w / 12 + h / 5) + 1)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, (w - tw) // 2, (h - th) // 2)
        # 删除DC
        del dc

        # 设置透明色
        image = bitmap.ConvertToImage()
        if not image.HasAlpha():
            image.InitAlpha()
        for y in range(image.GetHeight()):
            for x in range(image.GetWidth()):
                pix = wx.Colour(image.GetRed(x, y),
                                image.GetGreen(x, y),
                                image.GetBlue(x, y),
                                image.GetAlpha(x, y))
                if pix == wx.BLACK:
                    image.SetAlpha(x, y, 0)
                else:
                    if focused_alpha is not None:
                        image.SetAlpha(x, y, 255 * focused_alpha / 100)

        # 画好了，返回
        return image.ConvertToBitmap()


# 自定义StaticBox
class CustomStaticBox(wx.StaticBox):
    def __init__(self, parent, id, border_thickness = 1, border_color = wx.BLACK,
                 margin = 0, radius = 0, has_scroller = False, border_extra = 0,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.TRANSPARENT_WINDOW):
        wx.StaticBox.__init__(self, parent, id, "", pos, size, style, "")
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.margin = margin
        self.radius = radius
        self.has_scroller = has_scroller
        self.border_extra = border_extra

        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(self.border_color, self.border_thickness))
        x = self.margin + math.floor(self.border_thickness / 2)
        y = self.margin + math.floor(self.border_thickness / 2)
        width, height = self.GetValidSize()
        # 如果有滚动条，则给滚动条留出位置
        if self.has_scroller:
            width -= configs.SIZE_SCROLL_BAR
        dc.DrawRoundedRectangle(x, y, width, height, self.radius)

    def SetBorderThickness(self, border_thickness):
        self.border_thickness = border_thickness

    def SetBorderColor(self, border_color):
        self.border_color = border_color

    def SetMargin(self, margin):
        self.margin = margin

    def SetBordersForSizer(self, border_extra):
        self.border_extra = border_extra

    def GetValidSize(self):
        width = self.GetSize()[0] - self.margin * 2 - math.fabs(self.border_thickness - 1)
        height = self.GetSize()[1] - self.margin * 2 - math.fabs(self.border_thickness - 1)
        return int(width), int(height)

    def GetBordersForSizer(self):
        return self.border_extra, self.border_extra


# 自定义带边框的panel容器
class CustomBorderPanel(wx.Panel):
    def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 border_thickness = 1, margin = 0, radius = 0, border_extra = 0,
                 border_color = wx.BLACK, self_adaptive = False, style = 0, name = "CustomBorderPanel"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.staticBox = CustomStaticBox(self, wx.ID_ANY, border_thickness = border_thickness, size = size,
                                         border_color = border_color, margin = margin, radius = radius,
                                         border_extra = border_extra)
        self.inner_sizer = wx.StaticBoxSizer(self.staticBox, wx.HORIZONTAL)
        # 这里将sizer设置到父类中，因为这个panel需要固定的内边框
        super().SetSizer(self.inner_sizer)

        self.border_thickness = border_thickness
        self.border_color = border_color
        self.margin = margin
        self.border_extra = border_extra
        self.self_adaptive = self_adaptive
        # 绑定事件：margin根据size大小自适应调整
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        if self.self_adaptive:
            margin_1 = math.ceil(self.GetSize()[0] / 350)
            margin_2 = math.ceil(self.GetSize()[1] / 300)
            margin = margin_1
            if margin > margin_2:
                margin = margin_2
            self.SetMargin(margin + 3)
        event.Skip()

    # 重写SetSizer以支持对Panel本身设置Sizer
    def SetSizer(self, sizer, deleteOld = True):
        self.inner_sizer.Add(sizer, 1, wx.EXPAND)

    # 重写GetSizer，返回Panel本身的Sizer而不是static box sizer
    def GetSizer(self):
        return self.inner_sizer.GetChildren()[0]

    def SetBorderThickness(self, border_thickness):
        self.border_thickness = border_thickness
        self.staticBox.SetBorderThickness(border_thickness)

    def SetBorderColor(self, border_color):
        self.border_color = border_color
        self.staticBox.SetBorderColor(border_color)

    def SetMargin(self, margin):
        self.margin = margin
        self.staticBox.SetMargin(margin)

    def GetMargin(self):
        return self.margin

    def SetBordersForSizer(self, border_extra):
        self.border_extra = border_extra
        self.staticBox.SetBordersForSizer(border_extra)

    def GetValidSize(self):
        return self.staticBox.GetValidSize()

    def GetBordersForSizer(self):
        return self.staticBox.GetBordersForSizer()


# 自定义的view_panel，可以设定margin（外边距）
class CustomViewPanel(wx.Panel):
    def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, name = "CustomViewPanel", margin = 0):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.margin = margin
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        size = self.GetSize()
        size -= (self.margin * 4, self.margin * 4)
        position = self.GetPosition()
        position += (self.margin * 2, self.margin * 2)
        self.SetSize(size)
        self.SetPosition(position)
        # event.Skip() # 注释掉就可以解决触发重复触发次数过多的问题，暂时不太理解为什么

    def SetMargin(self, margin):
        self.margin = margin

    def GetMargin(self):
        return self.margin


# 菜单panel里的logo组件
class LogoPanel(wx.Panel):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, image_ratio = 70, # 图片比例，单位%
                 size = wx.DefaultSize, style = 0, name = "CustomMenuButton"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size, style = style, name = name)
        self.image_ratio = image_ratio
        self.logo_img_png = wx.Image(configs.PATH_LOGO_IMAGE, wx.BITMAP_TYPE_ANY)
        # self.logo_img_static = wx.StaticBitmap(self, wx.ID_ANY, self.logo_img_png.ConvertToBitmap())

        # # 添加一个sizer让图片右对齐
        # self.sizer = wx.BoxSizer(wx.VERTICAL) # 由于右对齐对水平sizer不生效因此加一个垂直sizer
        # self.sizer.Add(self.logo_img_static, 1, wx.RIGHT | wx.ALIGN_RIGHT, border = 5)
        # self.SetSizer(self.sizer)
        # self.Layout()

        # 绑定on_size事件
        # self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        # self.logo_img_static.Bind(wx.EVT_MOTION, self.process_parent_event)
        # self.logo_img_static.Bind(wx.EVT_LEFT_DOWN, self.process_parent_event)
        # self.logo_img_static.Bind(wx.EVT_LEFT_UP, self.process_parent_event)

    # 调用父类对应的事件（因为这个组件其实是真正的自定义组件（一个panel假装的）的内部组件，
    # 正常情况下会在父组件的上方，因此事件触发基本上都是触发此对象，而实际代码逻辑中绑定时都是绑定父对象，因此要向上传递
    def process_parent_event(self, event):
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)
        event.Skip()

    def on_size(self, event):
        # 复制一个wx.Image，以免多次Rescale导致图片失真
        log_temp = self.logo_img_png.Copy()

        # 重新根据当前父panel的size计算新的图片size及图片右边的border
        logo_img_width, logo_img_height, border = self.calculate_logo_img_size()
        log_temp.Rescale(logo_img_width, logo_img_height, wx.IMAGE_QUALITY_BILINEAR)

        # # 设置新的bitmap
        # self.logo_img_static.SetBitmap(log_temp.ConvertToBitmap())
        # # 设定新的border
        # self.sizer.GetChildren()[0].SetBorder(border)

        # 刷新一下布局
        self.Layout()
        event.Skip()


    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))

        # 复制一个wx.Image，以免多次Rescale导致图片失真
        log_temp = self.logo_img_png.Copy()

        # 重新根据当前父panel的size计算新的图片size及图片右边的border
        logo_img_width, logo_img_height, border = self.calculate_logo_img_size()
        log_temp.Rescale(logo_img_width, logo_img_height, wx.IMAGE_QUALITY_BILINEAR)

        bitmap = log_temp.ConvertToBitmap()
        dc.DrawBitmap(bitmap, 0, 0, bitmap.GetMask() is not None)

        del dc
        event.Skip()


    # 重新根据当前父panel的size计算新的图片size及图片右边的border
    def calculate_logo_img_size(self):
        p_width, p_height = self.GetParent().GetSize()
        img_size = self.logo_img_png.GetSize()
        width, height = CommonUtils.CalculateNewSizeWithSameRatio(img_size, p_height * (self.image_ratio / 100) / img_size[1])
        return width, height, p_width / 200

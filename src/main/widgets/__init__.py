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
                 label_color = "#FFFFFF", pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator, custom_style = BUTTON_STYLE_HORIZONTAL,
                 background_color = "#000000",
                 name = "CustomGenBitmapTextToggleButton"):
        if custom_style == BUTTON_STYLE_VERTICAL and len(label) > configs.LENGTH_MAIN_MENU:
            raise LengthTooLongException("Length of main menu label[%s] too long, no more than %d" % (label, configs.LENGTH_MAIN_MENU))
        elif len(label) > configs.LENGTH_CHILD_MENU:
            raise LengthTooLongException("Length of child menu label[%s] too long, no more than %d" % (label, configs.LENGTH_CHILD_MENU))

        buttons.GenBitmapButton.__init__(self, parent, id, bitmap, pos, size, style, validator, name)
        self.label_color = label_color
        self.SetLabel(label)
        self.custom_style = custom_style
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)
        self.SetBackgroundColour(background_color)

    def DrawLabel(self, dc, width, height, dx = 0, dy = 0):
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
                img.Rescale(height / 3 + width / 45, height / 3 + width / 45, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
            else:
                img = bmp.ConvertToImage()
                img.Rescale(height / 2.7, height / 2.7, wx.IMAGE_QUALITY_HIGH)
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
            font_temp.SetPointSize(int(width / 30 + height / 9) + 1)
            dc.SetFont(font_temp)
            dc.SetTextForeground(self.label_color)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_x = width / 15 + (width - tw) / 20 # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, pos_x, (height - bh - (bh / 100 * 10)) / 2 + dy, hasMask)  # draw bitmap if available
                pos_x = pos_x + (width / 20)  # extra spacing from bitmap

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

    # 重写绘制方法
    def OnPaint(self, event):
        (width, height) = self.GetClientSize()
        x1 = y1 = 0
        x2 = width - 1
        y2 = height - 1
        dc = wx.PaintDC(self)
        brush = self.GetBackgroundBrush(dc)

        # 这里加了一行代码：让背景画刷跟背景颜色一致（不知道为啥这个颜色默认是不一样的）
        brush.SetColour(self.GetBackgroundColour())

        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        self.DrawBezel(dc, x1, y1, x2, y2)
        self.DrawLabel(dc, width, height)
        if self.hasFocus and self.useFocusInd:
            self.DrawFocusIndicator(dc, width, height)


# 自定义菜单按钮（用panel模拟按钮，以实现子菜单的左侧选中效果）
class CustomMenuButton(wx.Panel):
    def __init__(self, parent, id = -1, bitmap = wx.NullBitmap, label = '',
                 label_color = "#FFFFFF", pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator, custom_style = BUTTON_STYLE_HORIZONTAL,
                 background_color = "#000000", need_trigger_bar = False,
                 name = "CustomGenBitmapTextToggleButton"):
        wx.Panel.__init__(self, parent, id, pos = pos, size = size)
        self.button = CustomGenBitmapTextToggleButton(parent, id, bitmap, label, label_color, pos, size, style,
                                                      validator, custom_style, background_color, name)
        # 按钮激活后是否需要一个激活的条状效果
        self.need_trigger_bar = need_trigger_bar

        # 上面那个要先设置，因为SetSize要用
        self.SetLabel(label)
        self.SetSize(size)
        self.SetPosition(pos)

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

        # 绑定事件，实现鼠标悬浮时改变背景颜色效果，移出时恢复原背景颜色（针对激活与否有不同的效果）
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    def on_enter(self, event):
        self.leave_color = self.background_color
        if self.button.GetToggle():
            self.leave_color = self.s_toggle_color
        else:
            self.toggle_flag = False
            self.SetBackgroundColour(self.enter_color)

    def on_leave(self, event):
        self.SetBackgroundColour(self.leave_color)

    # 先绑定的事件后执行，所以在这个事件执行前，已经修改了背景颜色
    def on_left_up(self, event):
        if self.button.GetToggle():
            if not self.toggle_flag:
                self.toggle_flag = True
                self.leave_color = self.s_toggle_color = self.background_color
        event.Skip()

    # 重写SetBackgroundColour方法，以达到给panel和按钮分别着色的目的
    def SetBackgroundColour(self, colour):
        self.background_color = colour
        if self.button.custom_style == BUTTON_STYLE_HORIZONTAL:
            if self.button.GetToggle() and self.need_trigger_bar:
                super().SetBackgroundColour(self.button.label_color)
            else:
                super().SetBackgroundColour(colour)
        self.button.SetBackgroundColour(colour)
        self.button.Refresh()
        self.Refresh()

    # 新建SetToggle，因为panel没有这个方法，实现调用按钮的SetToggle方法
    def SetToggle(self, flag):
        self.button.SetToggle(flag)

    # 重写SetSize方法，以达到给panel和按钮分别设置size的目的
    def SetSize(self, *args):
        width, height = (0, 0)

        if len(args) == 1:
            width, height = args[0][0], args[0][1]
        elif len(args) == 2:
            width, height = args

        super().SetSize(width, height)

        if self.button.custom_style == BUTTON_STYLE_HORIZONTAL and self.need_trigger_bar:
            width, height = (width - width * 0.05, height)
        else:
            pass

        self.button.SetSize(width, height)

    # 重写SetPosition方法，以达到给panel和按钮分别设置position的目的
    def SetPosition(self, pt):
        super().SetPosition(pt)

        if self.button.custom_style == BUTTON_STYLE_HORIZONTAL:
            pt = (pt[0] + self.GetSize()[0] - self.button.GetSize()[0], pt[1])
        else:
            pass

        self.button.SetPosition(pt)


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
                 margin = 5, radius = 0, has_scroller = False, border_extra = 0,
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
                 border_color = wx.BLACK, style = 0, name = "CustomBorderPanel"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.staticBox = CustomStaticBox(self, wx.ID_ANY, border_thickness = border_thickness, size = size,
                                         border_color = border_color, margin = margin, radius = radius,
                                         border_extra = border_extra)
        sizer = wx.StaticBoxSizer(self.staticBox, wx.HORIZONTAL)
        self.SetSizer(sizer)

        self.border_thickness = border_thickness
        self.border_color = border_color
        self.margin = margin
        self.border_extra = border_extra

    def SetBorderThickness(self, border_thickness):
        self.border_thickness = border_thickness
        self.staticBox.SetBorderThickness(border_thickness)

    def SetBorderColor(self, border_color):
        self.border_color = border_color
        self.staticBox.SetBorderColor(border_color)

    def SetMargin(self, margin):
        self.margin = margin
        self.staticBox.SetMargin(margin)

    def SetBordersForSizer(self, border_extra):
        self.border_extra = border_extra
        self.staticBox.SetBordersForSizer(border_extra)

    def GetValidSize(self):
        return self.staticBox.GetValidSize()

    def GetBordersForSizer(self):
        return self.staticBox.GetBordersForSizer()


# 自定义Panel，这个只显示一个会根据Panel大小和比例参数，自适应改变大小并显示在正中央的bitmap图片
class CustomBitmapPanel(wx.Panel):
    def __init__(self, parent, id,
                 image = None,                      # 这个是wx.Image对象
                 image_ratio = 90,                  # 这个是图片大小的比例，单位%
                 pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, name = "CustomBitmapPanel"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        # bitmap的parent采用跟当前对象的parent同一个，是为了避免bitmap改变大小时会影响到其parent的大小
        # 测试发现bitmap改变大小时，parent的大小如果小于bitmap的尺寸，好像是会跟着变大的
        self.bitmap = wx.StaticBitmap(self, id, wx.Bitmap.FromRGBA(1, 1, 0, 0, 0), pos, size, style, name)
        self.image = image
        self.image_ratio = image_ratio
        self.Rescale(size)

        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        self.Rescale(self.GetSize())
        event.Skip()

    def Rescale(self, size):
        self_w, self_h = size
        if self.image is not None and self_w > 0 and self_h > 0:
            size_base = self_w
            if size_base > self_h:
                size_base = self_h
            image = self.image.Copy()
            i_size = image.GetSize()
            new_w, new_h = CommonUtils.CalculateNewSizeWithSameRatio(i_size, size_base * (self.image_ratio / 100) / i_size[1])
            image.Rescale(new_w, new_h, wx.IMAGE_QUALITY_NEAREST)
            self.bitmap.SetBitmap(image.ConvertToBitmap())
            # 由于bitmap本身的parent不是self，而是跟self一样的self.parent，因此position需要加上self的position才是我们想要的结果
            new_x, new_y = self.GetPosition()
            new_x += (self_w - new_w) // 2
            new_y += (self_h - new_h) // 2
            self.bitmap.SetPosition((new_x, new_y))

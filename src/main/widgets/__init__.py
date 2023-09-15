import math
import string
import time

import wx
import wx.lib.buttons as buttons
from PIL import ImageColor

import configs
from exceptions.Custom_Exception import LengthTooLongException
from utils import CommonUtils


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
                img.Rescale(math.ceil(height / 4.5 + width / 45), math.ceil(height / 4.5 + width / 45), wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
            else:
                img = bmp.ConvertToImage()
                img.Rescale(math.ceil(height / 3.3), math.ceil(height / 3.3), wx.IMAGE_QUALITY_HIGH)
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
            font_temp.SetPointSize(int(width / 35 + height / 10) + 1)
            dc.SetFont(font_temp)
            dc.SetTextForeground(self.label_color)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_x = width / 10 + (width - tw) / 20 # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, pos_x + dx, (height - bh - (bh / 100 * 2)) / 2 + dy, hasMask)  # draw bitmap if available
                pos_x = pos_x + (width / 18)  # extra spacing from bitmap

            dc.DrawText(label, pos_x + bw + dx, (height - th) / 2 + dy)  # draw the text
        else:
            # handle the font, make it adjust the size
            font_temp = self.GetFont()
            font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
            font_temp.SetPointSize(int(height / 10) + 1)
            dc.SetFont(font_temp)
            dc.SetTextForeground(self.label_color)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_y = (height - bh - th * 1.5) / 2 + dy  # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, (width - bw - (bw / 100 * 5)) / 2 + dx, pos_y + dy, hasMask)  # draw bitmap if available
                pos_y = pos_y + (height / 50)  # extra spacing from bitmap

            dc.DrawText(label, (width - tw) / 2 + dx, pos_y + bh * 1.1 + dy)  # draw the text


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
            self.SetToggle(self.GetToggle())
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
            width, height = self.GetSize()
            self.SetSize(width, height)
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
        x, y = 0, 0
        if self.custom_style == BUTTON_STYLE_HORIZONTAL and self.need_trigger_bar:
            if self.GetToggle():
                width_reduction = self.get_width_reduction(width)
                width, height = (width - width_reduction, height)
                x = width_reduction
        else:
            pass
        self.button.SetSize(width, height)
        self.button.SetPosition((x, y))

    def get_width_reduction(self, width):
        return math.floor(width * 0.04)


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
        self.focusing = False
        self.is_key_down = False

        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)
        self.SetBitmapLabel(self.createBitMap(self.background_color, None))
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)

    def set_custom_font(self, button_size_type):
        self.button_size_type = button_size_type
        self.SetBitmapLabel(self.createBitMap(self.background_color, None))

    def OnSize(self, event):
        if self.is_key_down:
            self.OnKeyDown(event)
        else:
            self.OnLeftUp(event)
        super().OnSize(event)

    def OnMotion(self, event):
        pass

    def OnPaint(self, event):
        super().OnPaint(event)

    def on_enter(self, event):
        if self.button_type == BUTTON_TYPE_NORMAL:
            if not self.focusing:
                self.focusing = True
                self.SetBitmapLabel(self.createBitMap(self.background_color, self.focused_alpha))
                self.Refresh()
        elif self.button_type == BUTTON_TYPE_SWITCH:
            if not self.focusing:
                self.focusing = True
                if not self.is_key_down:
                    self.SetBitmapLabel(self.createBitMap(self.background_color, self.focused_alpha))
                else:
                    self.SetBitmapLabel(self.createBitMap(self.clicked_color, self.focused_alpha))
                self.Refresh()
        event.Skip()

    def on_leave(self, event):
        if self.button_type == BUTTON_TYPE_NORMAL:
            self.SetBitmapLabel(self.createBitMap(self.background_color, None))
        elif self.button_type == BUTTON_TYPE_SWITCH:
            if self.is_key_down:
                self.SetBitmapLabel(self.createBitMap(self.clicked_color, None))
            else:
                self.SetBitmapLabel(self.createBitMap(self.background_color, None))
        self.Refresh()
        self.focusing = False
        event.Skip()

    def OnLeftDown(self, event):
        if not self.is_key_down:
            self.SetBitmapLabel(self.createBitMap(self.clicked_color, None))
        else:
            self.SetBitmapLabel(self.createBitMap(self.background_color, None))

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
            if self.focusing:
                self.SetBitmapLabel(self.createBitMap(self.background_color, self.focused_alpha))
            else:
                self.SetBitmapLabel(self.createBitMap(self.background_color, None))
        elif self.button_type == BUTTON_TYPE_SWITCH:
            pass
        super().OnLeftUp(event)

    # 画bitmap
    def createBitMap(self, background_color, focused_alpha):
        width, height = self.GetSize()
        label, font_color, radius = self.label, self.font_color, self.radius
        bitmap = wx.Bitmap(width, height, depth = 32)

        dc = wx.MemoryDC(bitmap)
        # 让背景全黑，方便后续设置透明色
        dc.SetBackground(wx.Brush(wx.BLACK))
        dc.Clear()

        # 设置画笔、画刷的颜色
        dc.SetPen(wx.Pen(background_color, 1))
        dc.SetBrush(wx.Brush(background_color))

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
            pixel_h = h * 0.6
            pixel_w = pixel_h * 0.5
            font_temp.SetPixelSize((pixel_w, pixel_h))
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(label)
        tx, ty = (w - tw) // 2, math.ceil((h - th) / 2 - th / 20)
        dc.DrawText(label, tx, ty)
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

    def SetRadius(self, radius):
        self.radius = radius

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
        self.radius = radius
        self.border_color = border_color
        self.margin = margin
        self.border_extra = border_extra
        self.self_adaptive = self_adaptive
        # 绑定事件：margin根据size大小自适应调整
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        if self.self_adaptive:
            margin_1 = math.ceil(self.GetSize()[0] / 300)
            margin_2 = math.ceil(self.GetSize()[1] / 300)
            self.SetMargin(margin_1 + margin_2)
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

    def SetRadius(self, radius):
        self.radius = radius
        self.staticBox.SetRadius(radius)

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
                 style = 0, name = "CustomViewPanel", margin = 0, menu_name = ""):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.margin = margin
        self.menu_name = menu_name
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        size = self.GetSize()
        size -= (self.margin * 4, self.margin * 4)
        position = self.GetPosition()
        position += (self.margin * 2, self.margin * 2)
        self.SetSize(size)
        self.SetPosition(position)
        # event.Skip() # 注释掉就可以解决触发重复触发次数过多的问题，暂时不太理解为什么

    def on_paint(self, event):
        event.Skip()

    def SetMargin(self, margin):
        self.margin = margin

    def GetMargin(self):
        return self.margin


# 弹出框里的按钮的对齐方式
BUTTONS_ALIGNMENT_CENTER = 0
BUTTONS_ALIGNMENT_LEFT = 1
BUTTONS_ALIGNMENT_RIGHT = 2

# 通用的弹出型窗口组件
class CustomPopupWindow(wx.PopupTransientWindow):
    # 为了提速暂时不做有右上方按钮的弹出窗，以后有需要再做
    # PATH_MINIMIZE_BUTTON    = "configs/icons/button_minimize.png"
    # PATH_MAXIMIZE_BUTTON    = "configs/icons/button_maximize.png"
    # PATH_RESTORE_BUTTON     = "configs/icons/button_restore.png"
    # PATH_CLOSE_BUTTON       = "configs/icons/button_close.png"

    def __init__(self, parent: wx.Window,
                 title = "",
                 border_color = configs.COLOR_COMMON_DDDDDD,
                 background_color = configs.COLOR_SYSTEM_BACKGROUND):
        wx.PopupTransientWindow.__init__(self, parent)
        self.title = title
        self.title_font_pixel_height = 0
        self.border_color = border_color
        self.background_color = background_color
        self.shadow_thickness = 4
        self.buttons = []
        self.button_height = 0
        self.buttons_alignment = BUTTONS_ALIGNMENT_RIGHT
        self.size_cache = None
        self.indent = 0
        self.content_size = (0, 0)
        self.content_font_pixel_height = 0
        self.content_font_pixel_size = None
        self.content_panel = wx.Panel(self, wx.ID_ANY)
        self.Bind(wx.EVT_SHOW, self.on_show)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

    def add_button(self, label, event_handler = None):
        button = CustomRadiusButton(self, wx.ID_ANY,
                                    label = label,
                                    font_color = configs.COLOR_BUTTON_TEXT,
                                    background_color = configs.COLOR_BUTTON_BACKGROUND,
                                    clicked_color = configs.COLOR_BUTTON_FOCUSED,
                                    radius = 2)
        if event_handler is not None:
            button.Bind(wx.EVT_LEFT_UP, event_handler)
        self.buttons.append(button)

    def on_show(self, event):
        self.center_on_parent()
        event.Skip()

    def on_size(self, event):
        w, h = self.GetSize()
        p_w, p_h = CommonUtils.GetTopParent(self).GetSize()

        # 若果没有缓存的size或者主窗体size有改变，则赋值
        if self.size_cache is None or self.GetSize() != self.size_cache:
            self.size_cache = w + self.shadow_thickness, h + self.shadow_thickness
            self.size_cache = self.size_cache
            w, h = self.size_cache
            self.indent = int(p_w / 190 + p_h / 90)
            self.SetSize(self.size_cache)
            # 计算标题字体和内容字体大小
            self.title_font_pixel_height = p_h * 0.03
            self.content_font_pixel_height = self.title_font_pixel_height * 0.8
            self.content_font_pixel_size = self.content_font_pixel_height / 2, self.content_font_pixel_height
            # 如果有按钮
            buttons_len = len(self.buttons)
            if buttons_len:
                self.button_height = 0
                # 计算button之间的v_gap和button的h_gap
                v_gap = w // 25
                h_gap = self.indent
                # 所有buttons的宽度总量
                b_w_sum = 0
                # button的y坐标值
                b_y = 0
                for index in range(buttons_len):
                    button = self.buttons[index]
                    # 计算button的size和pos
                    b_w, b_h = self.calc_button_size(button.label)
                    if self.button_height == 0:
                        self.button_height = b_h
                    button.SetSize(b_w, b_h)
                    # y坐标是一直不变的，只要拿到第一个按钮的高度，就能知道y坐标的值，因此只计算一次
                    if b_y == 0:
                        b_y = h - b_h - h_gap
                    b_w_sum += b_w

                next_b_x = 0
                for index in range(buttons_len):
                    button = self.buttons[index]
                    b_w = button.GetSize()[0]
                    b_x = 0
                    # 计算当前button的x坐标值
                    if next_b_x == 0:
                        if self.buttons_alignment == BUTTONS_ALIGNMENT_CENTER:
                            b_x = (w - b_w_sum - v_gap * (buttons_len - 1)) // 2
                        elif self.buttons_alignment == BUTTONS_ALIGNMENT_LEFT:
                            b_x = self.indent
                        elif self.buttons_alignment == BUTTONS_ALIGNMENT_RIGHT:
                            b_x = w - b_w_sum - self.indent - v_gap * (buttons_len - 1)
                        next_b_x = b_x + v_gap + b_w
                    else:
                        b_x = next_b_x
                        next_b_x += v_gap + b_w

                    button.SetPosition((b_x, b_y))
                    button.Refresh()

            # 最后重设content_panel的size和pos
            c_size, c_pos = self.get_content_size_and_pos(w, h)
            self.content_panel.SetSize(c_size)
            self.content_panel.SetPosition(c_pos)

        event.Skip()

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        shadow_thickness = self.shadow_thickness
        w, h = self.GetSize()

        # 设置画笔、画刷的颜色
        pen = wx.Pen(self.border_color, 1)
        dc.SetPen(pen)
        brush = wx.Brush(self.background_color)
        dc.SetBrush(brush)

        # 画出bitmap的形状
        dc.DrawRoundedRectangle(0, 0, w - shadow_thickness, h - shadow_thickness, 0)

        shadow_w, shadow_h = w - shadow_thickness, h - shadow_thickness
        for i in range(shadow_thickness):
            dc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 255 / 4 + (1 - 255 / 4) * (i + 1) / shadow_thickness), 1))
            dc.DrawLine((i, shadow_h + i), (shadow_w + i, shadow_h + i))
            dc.DrawLine((shadow_w + i, i), (shadow_w + i, shadow_h + i - 1))

        # 绘制标题
        if self.title is not None and self.title != "":
            font_temp = self.GetFont()
            font_temp.SetPixelSize((self.title_font_pixel_height / 2, self.title_font_pixel_height))
            dc.SetFont(font_temp)
            dc.DrawText(self.title, self.indent, self.indent)

        # 绘制分割线
        line_len = w - self.indent * 2
        line_height = self.indent
        if self.title is not None and self.title != "":
            line_height += self.title_font_pixel_height * 1.4
        dc.SetPen(wx.Pen(configs.COLOR_COMMON_DDDDDD, 1))
        dc.DrawLine(self.indent, line_height, line_len + self.indent, line_height)

        del dc
        event.Skip()

    def center_on_parent(self):
        p_x, p_y = CommonUtils.GetTopParent(self).GetPosition()
        p_w, p_h = CommonUtils.GetTopParent(self).GetSize()
        w, h = self.GetSize()
        self.SetPosition((p_x + p_w // 2 - w // 2, p_y + p_h // 2 - h // 2))
        # self.Refresh()

    def calc_button_size(self, label):
        p_w, p_h = CommonUtils.GetTopParent(self).GetSize()
        b_h = math.ceil(p_h / 27)
        b_w = b_h * 1.5 + b_h * 0.5 * len(label)
        return b_w, b_h

    def get_content_size_and_pos(self, w, h):
        c_w = w - self.indent * 2
        c_h = h - self.indent * 4
        c_x = self.indent
        c_y = self.indent * 2
        if self.title is not None and self.title != "":
            c_h -= self.title_font_pixel_height * 1.4 + self.button_height
            c_y += self.title_font_pixel_height * 1.4
        self.content_size = (c_w, c_h)
        return (c_w, c_h), (c_x, c_y)


# 自定义TextCtrl组件
class CustomTextCtrl(wx.Control):
    def __init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition,
                 size = wx.DefaultSize, style = 0, validator = wx.DefaultValidator,
                 name = "CustomTextCtrl", hint = "", value = "", background_color = ""):
        wx.Control.__init__(self, parent, id, pos, size, wx.BORDER_NONE | style, validator, name)
        self.text_control = wx.TextCtrl(self, value = value, style = wx.BORDER_NONE | style, validator = validator)
        self.text_control.SetBackgroundColour(background_color)
        if hint:
            self.text_control.SetHint(hint)
        self.indent = 0
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_size(self, event):
        w, h = self.GetSize()
        self.indent = h // 8
        self.text_control.SetSize(w - 2 - self.indent * 2, h - 2 - self.indent * 2)
        self.text_control.SetPosition((1 + self.indent, 1 + self.indent))
        event.Skip()

    def on_paint(self, event):
        dc = wx.GCDC(wx.PaintDC(self))
        w, h = self.GetSize()

        dc.SetPen(wx.Pen(configs.COLOR_COMMON_DDDDDD, 1))
        dc.DrawRoundedRectangle(0, 0, w, h, 0)

        del dc
        event.Skip()

    def SetFont(self, font):
        super().SetFont(font)
        self.text_control.SetFont(font)

    def GetValue(self):
        return self.text_control.GetValue()

    def DiscardEdits(self):
        self.text_control.DiscardEdits()

    def EmulateKeyPress(self, event):
        self.text_control.EmulateKeyPress(event)

    def flush(self):
        self.text_control.flush()

    def GetDefaultStyle(self):
        self.text_control.GetDefaultStyle()

    def GetLineLength(self, lineNo):
        self.text_control.GetLineLength(lineNo)

    def GetLineText(self, lineNo):
        return self.text_control.GetLineText(lineNo)

    def GetNumberOfLines(self):
        self.text_control.GetNumberOfLines()

    def GetStyle(self, position, style):
        return self.text_control.GetStyle(position, style)

    def HideNativeCaret(self):
        return self.text_control.HideNativeCaret()

    def HitTestPos(self, pt):
        self.text_control.HitTestPos(pt)

    def IsModified(self):
        return self.text_control.IsModified()

    def IsMultiLine(self):
        return self.text_control.IsMultiLine()

    def IsSingleLine(self):
        return self.text_control.IsSingleLine()

    def LoadFile(self, *args, **kws):
        return self.text_control.LoadFile(*args, **kws)

    def MacCheckSpelling(self, check):
        self.text_control.MacCheckSpelling(check)

    def MarkDirty(self):
        self.text_control.MarkDirty()

    def OSXDisableAllSmartSubstitutions(self):
        self.text_control.OSXDisableAllSmartSubstitutions()

    def OSXEnableAutomaticDashSubstitution(self, enable):
        self.text_control.OSXEnableAutomaticDashSubstitution(enable)

    def OSXEnableAutomaticQuoteSubstitution(self, enable):
        self.text_control.OSXEnableAutomaticQuoteSubstitution(enable)

    def PositionToCoords(self, pos):
        return self.text_control.PositionToCoords(pos)

    def PositionToXY(self, pos):  # real signature unknown; restored from __doc__
        self.text_control.PositionToXY(pos)

    def SaveFile(self, *args, **kws):
        return self.text_control.SaveFile(*args, **kws)

    def SetDefaultStyle(self, style):
        return self.text_control.SetDefaultStyle(style)

    def SetModified(self, modified):
        self.text_control.SetModified(modified)

    def SetStyle(self, start, end, style):
        return self.text_control.SetStyle(start, end, style)

    def ShowNativeCaret(self, *args, **kws):
        return self.text_control.ShowNativeCaret(*args, **kws)

    def ShowPosition(self, pos):
        self.text_control.ShowPosition(pos)

    def write(self, text):
        self.text_control.write(text)

    def XYToPosition(self, x, y):
        return self.text_control.XYToPosition(x, y)


# 自定义数字validator
class NumericalValidator(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.on_char)

    # 一定需要有这个否则这个validator不生效
    def Clone(self):
        return NumericalValidator()

    def on_char(self, event):
        keycode = int(event.GetKeyCode())
        if 0 < keycode < 256:
            key = chr(keycode)
            if key in string.ascii_letters:
                return
        else:
            return
        event.Skip()



import wx
import wx.lib.buttons as buttons

from src.main.configs.SystemConfigs import *

# CustomGenBitmapTextToggleButton： custom_style
BUTTON_STYLE_HORIZONTAL = 1
BUTTON_STYLE_VERTICAL = 2


# 自定义图标文本开关按钮
class CustomGenBitmapTextToggleButton(buttons.GenBitmapTextToggleButton):
    def __init__(self, parent, id = -1, bitmap = wx.NullBitmap, label = '',
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator, custom_style = BUTTON_STYLE_HORIZONTAL,
                 background_color = "#000000",
                 name = "CustomGenBitmapTextToggleButton"):
        buttons.GenBitmapButton.__init__(self, parent, id, bitmap, pos, size, style, validator, name)
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
                img.Rescale(height / 3 + width / 50, height / 3 + width / 50, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
            else:
                img = bmp.ConvertToImage()
                img.Rescale(height / 3, height / 3, wx.IMAGE_QUALITY_HIGH)
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
            font_temp.SetPointSize(int(width / 50) + int(height / 10) + 3)
            dc.SetFont(font_temp)
            dc.SetTextForeground(COLOR_TEXT_THEME)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_x = width / 10  # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, pos_x, (height - bh - (bh / 100 * 10)) / 2 + dy, hasMask)  # draw bitmap if available
                pos_x = pos_x + (width / 20)  # extra spacing from bitmap

            dc.DrawText(label, pos_x + bw + dx, (height - th) / 2 + dy)  # draw the text
        else:
            # handle the font, make it adjust the size
            font_temp = self.GetFont()
            font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
            font_temp.SetPointSize(int(height / 10) + 1)
            dc.SetFont(font_temp)
            dc.SetTextForeground(COLOR_TEXT_THEME)

            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)  # size of text
            if not self.up:
                dx = dy = self.labelDelta

            pos_y = (height - bh - th) / 2 + dy  # adjust for bitmap and text to centre
            if bmp is not None:
                dc.DrawBitmap(bmp, (width - bw - (bw / 100 * 10)) / 2 + dx, pos_y, hasMask)  # draw bitmap if available
                pos_y = pos_y + (height / 50)  # extra spacing from bitmap

            dc.DrawText(label, (width - tw) / 2 + dx, pos_y + bh + dy)  # draw the text


# 自定义圆角按钮
class CustomRadiusButton(buttons.GenBitmapButton):
    def __init__(self, parent, id = -1, label = "",
                 font_color = "#FFFFFF", background_color = "#000000",
                 clicked_color = "#000000", radius = 0,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator,
                 name = "genbutton"):
        buttons.GenBitmapButton.__init__(self, parent, id, None, pos, size, style, validator, name)
        self.label = label
        self.font_color = font_color
        self.background_color = background_color
        self.clicked_color = clicked_color
        self.radius = radius

        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)
        self.SetBitmapLabel(self.createBitMap(label, font_color, background_color, radius))
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())

    def OnLeftDown(self, event):
        self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.clicked_color, self.radius))

        # buttons.GenBitmapButton.OnLeftDown(self, event)
        if (not self.IsEnabled()) or self.HasCapture():
            return
        # self.up = False
        self.CaptureMouse()
        self.SetFocus()
        self.Refresh()
        event.Skip()

    def OnMotion(self, event):
        pass


    def OnLeftUp(self, event):
        self.SetBitmapLabel(self.createBitMap(self.label, self.font_color, self.background_color, self.radius))
        buttons.GenBitmapButton.OnLeftUp(self, event)

    # 画bitmap
    def createBitMap(self, label, font_color, background_color, radius):
        width, height = self.GetSize() - (5, 5)
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
        w, h = dc.GetSize()
        dc.SetTextForeground(font_color)
        font_temp = self.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
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
                                image.GetBlue(x, y))
                if pix == wx.BLACK:
                    image.SetAlpha(x, y, 0)

        # 画好了，返回
        return image.ConvertToBitmap()


# 自定义panel容器
class CustomPanel(wx.Panel):
    def __init__(self, *args, **kws):
        wx.Panel.__init__(self, *args, **kws)

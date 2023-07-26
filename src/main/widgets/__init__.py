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


# 自定义panel容器
class CustomPanel(wx.Panel):
    def __init__(self, *args, **kws):
        wx.Panel.__init__(self, *args, **kws)

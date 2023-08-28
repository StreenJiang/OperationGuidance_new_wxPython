import math
import random

import wx
import threading

from src.main import configs, widgets
import src.main.models.ProductMission as pdctmsn
from src.main.utils import CommonUtils


# 工作台操作界面右侧上方状态展示的线程
class WorkplaceWorkingStatusThread(threading.Thread):
    def __init__(self,
                 window: widgets.CustomBorderPanel,
                 mission_obj: pdctmsn.ProductMission):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.window = window
        self.mission_obj = mission_obj

        self.running = True
        self.tightening_icon = wx.Image("configs/icons/processing_clockwise.png", wx.BITMAP_TYPE_ANY)
        self.loosening_icon = wx.Image("configs/icons/processing_anticlockwise.png", wx.BITMAP_TYPE_ANY)

        self.size_cache = None
        self.child_thread = None
        self.child_threads = {}

    def run(self) -> None:
        print("thread<WorkplaceWorkingStatusThread> running")
        self.running = True
        while self.running:
            # 获取产品任务对象
            mission_status = self.mission_obj.GetMissionStatus()

            if mission_status == pdctmsn.STATUS_MISSION_WORKING:
                # 根据不同状态进行不同的处理
                if not self.handle_process():
                    break
            elif mission_status == pdctmsn.STATUS_MISSION_DEFAULT:
                self.handle_others("待机", configs.COLOR_SYSTEM_LOGO)
                print("STATUS_MISSION_DEFAULT: waiting for any progress...")
            elif mission_status == pdctmsn.STATUS_MISSION_READY:
                self.handle_others("就绪", configs.COLOR_COMMON_GREEN)

            self.event.wait(0.25)

    def handle_others(self, status_text, background_color):
        if self.size_cache is None or self.size_cache != self.window.GetSize():
            self.size_cache = self.window.GetSize()
        w, h = self.size_cache
        dc = wx.WindowDC(self.window)

        # 背景设为logo的主题色
        dc.SetBackground(wx.Brush(background_color))
        dc.Clear()

        # 获取字体
        font_temp = self.window.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetTextForeground(configs.COLOR_COMMON_WHITE)

        # 绘制待机字样
        font_temp.SetPointSize(int(w / 9 + h / 7) + 2)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(status_text)
        t_y = math.ceil((h - th) / 2)
        dc.DrawText(status_text, (w - tw) // 2, t_y)

        del dc

    def handle_process(self):
        # 获取当前正在操作的产品面/孔位的indexs
        indexs = self.mission_obj.GetMissionIndexs()
        # 获取当前正在操作的螺丝孔位对象
        bolt_temp = self.mission_obj.GetMissionProductSides()[indexs[0]].GetBolts()[indexs[1]]
        # 获取当前正在操作的螺丝孔位的状态
        working_status = bolt_temp.GetBoltStatus()
        # 之后是否继续循环的标识
        continue_flag = True

        # 根据不同状态进行不同的处理
        if working_status == pdctmsn.STATUS_SCREW_GUN_TIGHTENING:
            # 正在拧紧
            self.handle_tightening(working_status, indexs)
        elif working_status == pdctmsn.STATUS_SCREW_GUN_TIGHTENING_COMPLETE:
            # 拧紧完成
            self.handle_tightening_complete(indexs)
        elif working_status == pdctmsn.STATUS_SCREW_GUN_TIGHTENING_ERROR:
            # 拧紧错误
            self.handle_tightening_error(indexs)
        elif working_status == pdctmsn.STATUS_SCREW_GUN_LOOSENING:
            # 正在反松
            self.handle_loosening(working_status, indexs)
        elif working_status == pdctmsn.STATUS_SCREW_GUN_LOOSENING_COMPLETE:
            # 反松完成
            self.handle_loosening_complete(indexs)
        elif working_status == pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR:
            # 反松错误
            self.handle_loosening_error(indexs)
        elif working_status == pdctmsn.STATUS_SCREW_GUN_DEFAULT:
            # 反松错误
            print("STATUS_SCREW_GUN_DEFAULT: waiting for any progress...")
        else:
            # 未知状态终止线程
            continue_flag = False

        return continue_flag

    def handle_tightening(self, working_status, indexs):
        if working_status not in self.child_threads.keys():
            self.clear_thread()
            child_thread = self.IconRotate(working_status, self.window,
                                           self.tightening_icon, True, indexs[1])
            child_thread.start()
            self.child_threads[working_status] = child_thread

    def handle_tightening_complete(self, indexs):
        self.handle_complete(True, indexs)

    def handle_tightening_error(self, indexs):
        self.handle_error(True, indexs)

    def handle_loosening(self, working_status, indexs):
        if working_status not in self.child_threads.keys():
            self.clear_thread()
            child_thread = self.IconRotate(working_status, self.window,
                                           self.loosening_icon, False, indexs[1])
            child_thread.start()
            self.child_threads[working_status] = child_thread

    def handle_loosening_complete(self, indexs):
        self.handle_complete(False, indexs)

    def handle_loosening_error(self, indexs):
        self.handle_error(False, indexs)

    def clear_thread(self):
        if len(self.child_threads) > 0:
            for dict_key in self.child_threads.keys():
                self.child_threads[dict_key].stop()

    def handle_complete(self, operation_flag, indexs):
        if self.size_cache is None or self.size_cache != self.window.GetSize():
            self.size_cache = self.window.GetSize()
        w, h = self.size_cache
        dc = wx.WindowDC(self.window)
        status_text = "OK"
        if operation_flag:
            message = f"[{indexs[1] + 1}]号螺丝拧紧合格"
        else:
            message = f"[{indexs[1] + 1}]号螺丝反松完成"

        # 背景设为绿色
        dc.SetBackground(wx.Brush(configs.COLOR_COMMON_GREEN))
        dc.Clear()

        # 获取字体
        font_temp = self.window.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetTextForeground(configs.COLOR_COMMON_WHITE)

        # 额外的垂直缩进
        vertical_indent = math.fabs((h - w) / 3) + 5
        # 绘制上方OK文字
        font_temp.SetPointSize(int(w / 6 + h / 5) + 2)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(status_text)
        t_y = math.ceil((h - th) / 2) - vertical_indent
        dc.DrawText(status_text, (w - tw) // 2, t_y)

        # 绘制下方文字描述
        font_temp.SetPointSize(int(w / 30 + h / 40) + 1)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(message)
        t_y = h - th - vertical_indent
        dc.DrawText(message, (w - tw) // 2, t_y)

        del dc

    def handle_error(self, operation_flag, indexs):
        if self.size_cache is None or self.size_cache != self.window.GetSize():
            self.size_cache = self.window.GetSize()
        w, h = self.size_cache
        dc = wx.WindowDC(self.window)
        status_text = "ERROR"
        if operation_flag:
            message = f"[{indexs[1] + 1}]号螺丝拧紧错误"
        else:
            message = f"[{indexs[1] + 1}]号螺丝反松错误"

        # 背景设为绿色
        dc.SetBackground(wx.Brush(configs.COLOR_COMMON_RED))
        dc.Clear()

        # 获取字体
        font_temp = self.window.GetFont()
        font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetTextForeground(configs.COLOR_COMMON_WHITE)

        # 额外的垂直缩进
        vertical_indent = math.fabs((h - w) / 3) + 5
        # 绘制上方OK文字
        font_temp.SetPointSize(int(w / 13 + h / 11) + 1)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(status_text)
        t_y = math.ceil((h - th) / 2) - vertical_indent
        dc.DrawText(status_text, (w - tw) // 2, t_y)

        # 绘制下方文字描述
        font_temp.SetPointSize(int(w / 30 + h / 40) + 1)
        dc.SetFont(font_temp)
        tw, th = dc.GetTextExtent(message)
        t_y = h - th - vertical_indent
        dc.DrawText(message, (w - tw) // 2, t_y)

        del dc

    def stop(self):
        self.running = False
        self.clear_thread()
        print("thread<WorkplaceWorkingStatusThread> stopped")


    class IconRotate(threading.Thread):
        def __init__(self, thread_type, window, icon_image, clockwise, bolt_num):
            threading.Thread.__init__(self)
            self.event = threading.Event()
            self.thread_type = thread_type
            self.window = window
            self.icon_image = icon_image
            self.clockwise = clockwise
            if self.clockwise:
                self.message = f"正在拧紧[{bolt_num + 1}]号螺丝"
            else:
                self.message = f"正在反松[{bolt_num + 1}]号螺丝"

            self.running = True
            self.dc = None
            self.size_cache = None
            self.angle = 0
            self.angle_span = 15 * math.pi / 180

        def run(self) -> None:
            print("thread<IconRotate: type = thread_type> rotating")
            self.running = True
            try:
                while self.running:
                    image = self.icon_image.Copy()

                    # 如果界面有大小变化，则内容需要自适应调整
                    if self.size_cache is None or self.size_cache != self.window.GetSize():
                        self.size_cache = self.window.GetSize()
                    w, h = self.size_cache

                    if self.dc is None:
                        self.dc = wx.WindowDC(self.window)

                    i_w, i_h = image.GetSize()
                    i_w, i_h = CommonUtils.CalculateNewSizeWithSameRatio((i_w, i_h), w * 0.7 / i_w)
                    image = image.Rescale(i_w, i_h, wx.IMAGE_QUALITY_HIGH)
                    # 旋转图片
                    if self.clockwise:
                        image = image.Rotate(-self.angle, (i_w / 2, i_h / 2))
                    else:
                        image = image.Rotate(self.angle, (i_w / 2, i_h / 2))
                    # 需要重新获取尺寸，因为旋转了以后，长宽会因为旋转后斜边从45度变为了其他的角度，导致图片水平和垂直的尺寸有变化
                    i_w, i_h = image.GetSize()
                    bitmap = image.ConvertToBitmap()
                    b_pos = (math.ceil((w - i_w) / 2), math.ceil((h * 0.9 - i_h) / 2))
                    self.dc.Clear()
                    # 绘制边框
                    self.dc.SetPen(wx.Pen(configs.COLOR_COMMON_GREEN, int(w / 40 + h / 80)))
                    self.dc.DrawRoundedRectangle(0, 0, w, h, 0)
                    # 绘制小图标
                    self.dc.DrawBitmap(bitmap, b_pos, bitmap.GetMask() is not None)

                    # 绘制文字
                    font_temp = self.window.GetFont()
                    font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
                    font_temp.SetPointSize(int(w / 30 + h / 40) + 1)
                    self.dc.SetTextForeground(configs.COLOR_COMMON_GREEN)
                    self.dc.SetFont(font_temp)
                    tw, th = self.dc.GetTextExtent(self.message)
                    t_y = h - th - math.fabs((h - w) / 3) - 2
                    self.dc.DrawText(self.message, (w - tw) // 2, t_y)

                    self.angle += self.angle_span
                    self.event.wait(0.03)
            finally:
                if self.dc is not None:
                    del self.dc

        def reset_angle(self):
            self.angle = 0

        def stop(self):
            self.running = False
            print("thread<IconRotate: type = thread_type> stopped")


# 工作台操作界面右侧中间数据实时展示的线程
class WorkplaceWorkingDataThread(threading.Thread):
    def __init__(self,
                 window: widgets.CustomBorderPanel,
                 data_obj: pdctmsn.RealtimeData):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.window = window
        self.data_obj = data_obj
        self.dc = None

        self.running = True
        self.size_cache = None

    def run(self) -> None:
        print("thread<WorkplaceWorkingDataThread> running")
        self.running = True
        try:
            while self.running:
                # 获取实时数据
                torque = str(round(self.data_obj.torque, 2))
                angle = str(self.data_obj.angle)

                if self.size_cache is None or self.size_cache != self.window.GetSize():
                    self.size_cache = self.window.GetSize()
                w, h = self.size_cache

                self.dc = wx.WindowDC(self.window)
                torque_title = "扭矩（N*m)"
                angle_title = "角度（°）"

                # 获取字体
                font_temp = self.window.GetFont()
                font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
                self.dc.SetTextForeground(configs.COLOR_TEXT_BLACK)

                # 水平、垂直缩进
                w_h_difference = math.ceil((h - w) / 50)
                horizontal_indent = math.ceil(w / 50)
                vertical_indent = math.ceil(h / 40) + w_h_difference

                # 扭矩标题的字体大小
                font_temp.SetPointSize(int(w / 30 + h / 25) + 1)
                self.dc.SetFont(font_temp)
                torque_title_w, torque_title_h = self.dc.GetTextExtent(torque_title)
                # 标题size、pos、背景颜色
                self.dc.SetPen(wx.Pen(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
                self.dc.SetBrush(wx.Brush(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
                self.dc.DrawRoundedRectangle(0, 0, w, torque_title_h + vertical_indent * 2, 0)
                # 绘制完背景再绘制扭矩标题
                self.dc.DrawText(torque_title, horizontal_indent, vertical_indent)

                # 绘制扭矩实时数据
                font_temp.SetPointSize(int(w / 27 + h / 6.3) + w_h_difference)
                self.dc.SetFont(font_temp)
                torque_w, torque_h = self.dc.GetTextExtent(torque)
                self.dc.DrawText(torque, w - torque_w - horizontal_indent, torque_title_h + vertical_indent * 2)

                # 扭矩标题的字体大小
                font_temp.SetPointSize(int(w / 30 + h / 25) + 1)
                self.dc.SetFont(font_temp)
                angle_title_w, angle_title_h = self.dc.GetTextExtent(angle_title)
                # 标题size、pos、背景颜色
                self.dc.SetPen(wx.Pen(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
                self.dc.SetBrush(wx.Brush(configs.COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND))
                self.dc.DrawRoundedRectangle(0, torque_title_h + torque_h + vertical_indent * 2, w, angle_title_h + vertical_indent * 2, 0)
                # 绘制完背景再绘制角度标题
                self.dc.DrawText(angle_title, horizontal_indent, torque_title_h + torque_h + vertical_indent * 3)

                # 绘制角度实时数据
                font_temp.SetPointSize(int(w / 48 + h / 9.2) + w_h_difference)
                self.dc.SetFont(font_temp)
                angle_w, angle_h = self.dc.GetTextExtent(angle)
                self.dc.DrawText(angle, w - angle_w - horizontal_indent, torque_title_h + torque_h + angle_title_h + vertical_indent * 4)

                # 背景设为透明（不遮挡其它已经绘制好的信息）
                self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
                # 将原来的框画回去
                self.dc.SetPen(wx.Pen(self.window.border_color, self.window.border_thickness))
                self.dc.DrawRoundedRectangle(0, 0, w, h, self.window.radius)

                self.event.wait(0.1)
        finally:
            if self.dc is not None:
                del self.dc

    def stop(self):
        self.running = False
        print("thread<WorkplaceWorkingStatusThread> stopped")

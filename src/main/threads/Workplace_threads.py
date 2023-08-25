import math

import wx
import threading
import time

from src.main import configs
import src.main.models.ProductMission as pdctmsn
from src.main.controllers import ProductMissionService as productMissionService
from src.main.utils import CommonUtils


# 工作台操作界面需要持续运行的主线程
class WorkplaceMainThread(threading.Thread):
    def __init__(self,
                 window: wx.Window,
                 mission_obj: pdctmsn.ProductMission):
        threading.Thread.__init__(self)
        self.window = window
        self.mission_obj = mission_obj

        self.running = True
        self.tightening_icon = wx.Image("configs/icons/processing_clockwise.png", wx.BITMAP_TYPE_ANY)
        self.loosening_icon = wx.Image("configs/icons/processing_anticlockwise.png", wx.BITMAP_TYPE_ANY)

        self.size_cache = None
        self.child_thread = None
        self.child_threads = {}

        # 绘制静态状态时需要一个计数器，因为window_size变化时线程执行到哪还不确定，为了保证绘制不出问题，会多绘制几次
        self.paint_count = 0
        self.paint_count_max = 5

    def run(self) -> None:
        print("thread<WorkplaceMainThread> running")
        self.running = True
        while self.running:
            # 获取产品任务对象
            mission_status = self.mission_obj.GetMissionStatus()
            if mission_status == pdctmsn.STATUS_MISSION_DEFAULT:
                print("waiting for any progress...")
                time.sleep(1)
            elif mission_status == pdctmsn.STATUS_MISSION_WORKING:
                # 根据不同状态进行不同的处理
                if not self.handle_process():
                    break

                # 更新产品任务的状态
                productMissionService.update_by_id(self.mission_obj.GetID())

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
        else:
            # 未知状态终止线程
            continue_flag = False

        time.sleep(0.5)
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
            self.paint_count = 0

        if self.paint_count < self.paint_count_max:
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
            self.paint_count += 1

    def handle_error(self, operation_flag, indexs):
        if self.size_cache is None or self.size_cache != self.window.GetSize():
            self.size_cache = self.window.GetSize()
            self.paint_count = 0

        if self.paint_count < self.paint_count_max:
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
            self.paint_count += 1

    def stop(self):
        self.running = False
        self.clear_thread()
        print("thread<WorkplaceMainThread> stopped")


    class IconRotate(threading.Thread):
        def __init__(self, thread_type, window, icon_image, clockwise, bolt_num):
            threading.Thread.__init__(self)
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

                    # 如果界面有大小变化，则图标也要变
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
                    time.sleep(0.03)
            finally:
                if self.dc is not None:
                    del self.dc

        def reset_angle(self):
            self.angle = 0

        def stop(self):
            self.running = False
            print("thread<IconRotate: type = thread_type> stopped")





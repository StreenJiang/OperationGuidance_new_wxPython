import wx
import threading
import math
import traceback

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
            try:
                # 获取产品任务对象
                mission_status = self.mission_obj.GetMissionStatus()
                mission_status_temp = self.mission_obj.mission_status_temp
                if mission_status_temp is not None:
                    mission_status = mission_status_temp

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
            except Exception as e:
                print("WorkplaceWorkingStatusThread -> e: ", e)
                traceback.print_exc()

    def handle_others(self, status_text, background_color):
        dc = wx.BufferedDC(wx.WindowDC(self.window), wx.Bitmap(self.window.GetSize()))
        try:
            if self.size_cache is None or self.size_cache != self.window.GetSize():
                self.size_cache = self.window.GetSize()
            w, h = self.size_cache

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
        except Exception as e:
            print("handle_others -> e", e)
            traceback.print_exc()
        finally:
            del dc

    def handle_process(self):
        # 获取当前正在操作的产品面/孔位的indexs
        indexs = self.mission_obj.GetMissionIndexs()
        # 获取当前正在操作的螺丝孔位对象
        bolt_temp = self.mission_obj.GetMissionProductSides()[indexs[0]].GetBolts()[indexs[1]]
        # 获取当前正在操作的螺丝孔位的状态
        working_status = bolt_temp.GetBoltStatus()
        bolt_status_temp = bolt_temp.bolt_status_temp
        if bolt_status_temp is not None:
            working_status = bolt_status_temp
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
            # 默认状态
            print("STATUS_SCREW_GUN_DEFAULT: waiting for any progress...")
        else:
            # 未知状态终止线程
            continue_flag = False

        return continue_flag

    def handle_tightening(self, working_status, indexs):
        if working_status not in self.child_threads.keys() or len(self.child_threads.keys()) > 1:
            self.clear_thread()
            child_thread = self.IconRotate(working_status, self.window,
                                           self.tightening_icon, True, indexs[1])
            child_thread.start()
            self.child_threads[working_status] = child_thread
        else:
            child_thread = self.child_threads[working_status]
            child_thread.bolt_num = indexs[1]
    def handle_tightening_complete(self, indexs):
        self.clear_thread()
        self.handle_complete(True, indexs)

    def handle_tightening_error(self, indexs):
        self.clear_thread()
        self.handle_error(True, indexs)

    def handle_loosening(self, working_status, indexs):
        if working_status not in self.child_threads.keys() or len(self.child_threads.keys()) > 1:
            self.clear_thread()
            child_thread = self.IconRotate(working_status, self.window,
                                           self.loosening_icon, False, indexs[1])
            child_thread.start()
            self.child_threads[working_status] = child_thread

    def handle_loosening_complete(self, indexs):
        self.clear_thread()
        self.handle_complete(False, indexs)

    def handle_loosening_error(self, indexs):
        self.clear_thread()
        self.handle_error(False, indexs)

    def clear_thread(self):
        if len(self.child_threads) > 0:
            for dict_key in self.child_threads.keys():
                self.child_threads[dict_key].stop()
            self.child_threads.clear()

    def handle_complete(self, operation_flag, indexs):
        dc = wx.BufferedDC(wx.WindowDC(self.window))
        try:
            status_text = "OK"
            if self.size_cache is None or self.size_cache != self.window.GetSize():
                self.size_cache = self.window.GetSize()
            w, h = self.size_cache

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
        except Exception as e:
            print("handle_complete -> e: ", )
            traceback.print_exc()
        finally:
            del dc

    def handle_error(self, operation_flag, indexs):
        dc = wx.BufferedDC(wx.WindowDC(self.window))
        try:
            status_text = "ERROR"
            if self.size_cache is None or self.size_cache != self.window.GetSize():
                self.size_cache = self.window.GetSize()
            w, h = self.size_cache

            if operation_flag:
                message = f"[{indexs[1] + 1}]号螺丝拧紧错误"
            else:
                message = f"[{indexs[1] + 1}]号螺丝反松错误"

            # 背景设为红色
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
        except Exception as e:
            print("handle_error -> e: ", e)
            traceback.print_exc()
        finally:
            del dc

    def stop(self):
        self.running = False
        self.clear_thread()
        print("thread<WorkplaceWorkingStatusThread> stopped")


    class IconRotate(threading.Thread):
        def __init__(self, thread_type, window: widgets.CustomBorderPanel,
                     icon_image, clockwise, bolt_num):
            threading.Thread.__init__(self)
            self.event = threading.Event()
            self.thread_type = thread_type
            self.window = window
            self.icon_image = icon_image
            self.clockwise = clockwise
            self.bolt_num = bolt_num
            self.message = None

            self.running = True
            self.size_cache = None
            self.angle = 0
            self.angle_span = 15 * math.pi / 180

        def update_message(self):
            if self.clockwise:
                self.message = f"正在拧紧[{self.bolt_num + 1}]号螺丝"
            else:
                self.message = f"正在反松[{self.bolt_num + 1}]号螺丝"

        def run(self) -> None:
            print(f"thread<IconRotate: type = {self.thread_type}> rotating")
            self.running = True
            while self.running:
                dc = wx.BufferedDC(wx.WindowDC(self.window))
                try:
                    image = self.icon_image.Copy()

                    # 如果界面有大小变化，则内容需要自适应调整
                    if self.size_cache is None or self.size_cache != self.window.GetSize():
                        self.size_cache = self.window.GetSize()
                    w, h = self.size_cache

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
                    # 绘制边框
                    dc.SetPen(wx.Pen(configs.COLOR_COMMON_GREEN, int(w / 40 + h / 80)))
                    dc.DrawRoundedRectangle(0, 0, w, h, 0)
                    # 绘制小图标
                    dc.DrawBitmap(bitmap, b_pos, bitmap.GetMask() is not None)

                    # 绘制文字
                    font_temp = self.window.GetFont()
                    font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
                    font_temp.SetPointSize(int(w / 30 + h / 40) + 1)
                    dc.SetTextForeground(configs.COLOR_COMMON_GREEN)
                    dc.SetFont(font_temp)
                    self.update_message()
                    tw, th = dc.GetTextExtent(self.message)
                    t_y = h - th - math.fabs((h - w) / 3) - 2
                    dc.DrawText(self.message, (w - tw) // 2, t_y)

                    self.angle += self.angle_span
                    self.event.wait(0.03)
                except Exception as e:
                    print("IconRotate -> e: ", e)
                    traceback.print_exc()
                finally:
                    del dc

        def reset_angle(self):
            self.angle = 0

        def stop(self):
            self.running = False
            print(f"thread<IconRotate: type = {self.thread_type}> stopped")


# 工作台操作界面右侧中间数据实时展示的线程
class WorkplaceWorkingDataThread(threading.Thread):
    def __init__(self,
                 window: widgets.CustomBorderPanel,
                 data_obj: pdctmsn.RealtimeData):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.window = window
        self.data_obj = data_obj

        self.running = True
        self.size_cache = None

    def run(self) -> None:
        print("thread<WorkplaceWorkingDataThread> running")
        self.running = True
        while self.running:
            dc = wx.WindowDC(self.window)
            try:
                w_h_difference = self.window.w_h_difference
                horizontal_indent = self.window.horizontal_indent
                vertical_indent = self.window.vertical_indent
                # 如果标题文字的大小还是空的，说明标题栏还没有绘制完毕，则暂时跳过，直到标题绘制完毕后再绘制数据
                if self.window.title_text_size is None:
                    continue
                title_w, title_h = self.window.title_text_size

                # 获取实时数据
                torque = str(round(self.data_obj.torque, 2))
                angle = str(self.data_obj.angle)

                if self.size_cache is None or self.size_cache != self.window.GetSize():
                    self.size_cache = self.window.GetSize()
                w, h = self.size_cache

                # 获取字体
                font_temp = self.window.GetFont()
                font_temp.SetWeight(wx.FONTWEIGHT_BOLD)
                dc.SetTextForeground(configs.COLOR_TEXT_BLACK)

                # 绘制扭矩实时数据
                font_temp.SetPointSize(self.window.torque_font_size)
                dc.SetFont(font_temp)
                torque_w, torque_h = dc.GetTextExtent(torque)
                dc.DrawText(torque,
                            x = w - torque_w - horizontal_indent,
                            y = title_h + vertical_indent * 2 + w_h_difference)

                # 绘制角度实时数据
                font_temp.SetPointSize(self.window.angle_font_size)
                dc.SetFont(font_temp)
                angle_w, angle_h = dc.GetTextExtent(angle)
                dc.DrawText(angle,
                            x = w - angle_w - horizontal_indent,
                            y = title_h * 2 + torque_h + vertical_indent * 5 + w_h_difference)

                # 背景设为透明（不遮挡其它已经绘制好的信息）
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                # 将原来的框画回去
                dc.SetPen(wx.Pen(self.window.border_color, self.window.border_thickness))
                dc.DrawRoundedRectangle(0, 0, w, h, self.window.radius)

                self.event.wait(0.1)
            except Exception as e:
                print("WorkplaceWorkingDataThread -> e: ", e)
                traceback.print_exc()
            finally:
                del dc


    def stop(self):
        self.running = False
        print("thread<WorkplaceWorkingDataThread> stopped")

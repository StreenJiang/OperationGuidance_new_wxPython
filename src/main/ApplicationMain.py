import wx

import configs
from views.MainFrame import MainFrame
from utils import ThreadPool


class MainApp(wx.App):
    def __init__(self, *args, **kws):
        wx.App.__init__(self, *args, **kws)
        self.frame = None

    def OnInit(self):
        # 1. 程序唯一性检测
        if self.Check_program_is_duplicated():
            return False

        # 2. 初始化系统参数
        variables = {
            "license_data": self.Analyse_license(),         # 解析许可证
        }
        # 初始化保存在磁盘中的系统参数
        self.Initialize_system_config()

        # 3. 开始画界面
        self.frame = MainFrame(parent = None, id = wx.ID_ANY, variables = variables)

        # 4. 创建线程池
        if not ThreadPool.initiate_pool(max_workers = configs.THREAD_POOL_TASK_MAS,
                                        thread_name_prefix = configs.THREAD_POOL_PREFIX):
            # 如果线程池初始化失败，则结束程序
            return False

        # 设置顶端窗体
        self.SetTopWindow(self.frame)

        # 默认显示在屏幕中间
        self.frame.Center()

        # 显示主窗体
        self.frame.Show()
        return True


    # 检查程序是否重复启动
    def Check_program_is_duplicated(self):
        import psutil
        pids = psutil.pids()  # 获取所有进程PID

        count = 0
        for pid in pids:  # 遍历所有PID进程
            try:
                p = psutil.Process(pid)  # 得到每个PID进程信息
                s = str(p.name())  # 将PID名称转换成字符串进行判断
                if s == "ApplicationMain.exe":  # “123.exe”你要防多开进程的名称
                    count += 1
            except psutil.NoSuchProcess as e:
                continue

        print("count: ", count)
        if count > 1:
            dlg = wx.MessageDialog(None, "程序已在运行中", "提示", wx.OK | wx.ICON_WARNING)
            result = dlg.ShowModal()
            return True

        return False


    # 解析许可证内容并返回配置信息
    def Analyse_license(self):

        # 实际上应该从许可证文件内容中解析后返回给main app，现在先手写
        return {
            "MAIN_MENU_LIST": [
                # "00001",
                "00002",
                "00003",
                "00004",
                "00005",
                "00006",
                "00007",
                "00000",
            ]
        }


    # 初始化系统参数
    def Initialize_system_config(self):
        # 从存储在磁盘中的系统参数文件中读取数据，然后修改软件默认的系统参数
        pass

    def OnExit(self):
        # 清理线程池
        return super().OnExit()


if __name__ == '__main__':
    MainApp().MainLoop()

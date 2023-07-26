import datetime


class CommonUtil:
    @staticmethod
    def CheckNone(obj, error_msg):
        if obj is None:
            raise Exception(error_msg)


    # 系统当前时间
    @staticmethod
    def System_Current_Datetime(format_str):
        try:
            value = datetime.datetime.now().strftime(format_str)
        except Exception:
            value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return value


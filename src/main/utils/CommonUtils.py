import datetime
import wx
from PIL import Image

from src.main.exceptions.Custom_Exception import ArgumentTypeException


def CheckNone(obj, error_msg):
    """
        检查对象是否是None，是的话直接抛出异常
        :param obj: 要检查的对象
        :param error_msg: 如果为空则抛出异常的异常信息描述
    """
    if obj is None:
        raise Exception(error_msg)


def System_Current_Datetime(format_str: str = None) -> str:
    """
        根据指定时间格式获取系统当前时间
        :param format_str: 时间格式化字符串
        :return: 时间字符串
    """
    if format_str is not None:
        value = datetime.datetime.now().strftime(format_str)
    else:
        value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return value


def CheckArgumentType(obj, argument_type: type) -> bool:
    """
        检查参数类型
        :param obj: 需要检查的参数
        :param argument_type: 需要参数是否是此类型
        :return: 返回真或者直接抛出异常
    """
    if isinstance(obj, argument_type):
        return True
    raise ArgumentTypeException("参数类型错误：[%s]应该是[%s]" % (obj, argument_type))


def PILImageToWxImage(pilImage: Image.Image) -> wx.Image:
    """
        转换　PIL Image 为　wxPython Image
        :param pilImage: PIL.Image.Image
        :return: wx.Image
    """
    return wx.Image((pilImage.size[0], pilImage.size[1]), pilImage.convert("RGB").tobytes())


def PILImageToWxBitmap(pilImage: Image.Image) -> wx.Bitmap:
    """
        转换　PIL Image 为　wxPython Bitmap
        :param pilImage: PIL.Image.Image
        :return: wx.Bitmap
    """
    return PILImageToWxImage(pilImage).ConvertToBitmap()


def WxBitmapToPILImage(wxBitmap: wx.Bitmap) -> Image.Image:
    """
        转换 wxPython Bitmap 为　PIL Image 对象
        :param wxBitmap: wx.Bitmap 实例
        :return: PIL.Image.Image
    """
    wxImage = wxBitmap.ConvertToImage()
    return Image.frombytes('RGB', (wxImage.GetWidth(), wxImage.GetHeight()), bytes(wxImage.GetData()))


def WxImageToPILImage(wxImage: wx.Image) -> Image.Image:
    """
        转换 wxPython Image 为　PIL Image 对象
        :param wxImage: wx.Image 实例
        :return: PIL.Image.Image
    """
    # wxImage 的 GetData方法返回图像的字节码，通过bytes强制转换，可以直接作为frombytes的参数。
    return Image.frombytes('RGB', (wxImage.GetWidth(), wxImage.GetHeight()), bytes(wxImage.GetData()))

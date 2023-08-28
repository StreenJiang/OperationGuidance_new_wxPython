import wx
from PIL import Image

from src.main.models.base import BaseEntity
import src.main.utils.CommonUtils as CommonUtils


# 任务状态
STATUS_MISSION_DEFAULT = 0
STATUS_MISSION_READY = 1
STATUS_MISSION_WORKING = 2
STATUS_MISSION_ERROR = 3
STATUS_MISSION_FINISHED = 4

# 螺丝孔位工作状态
STATUS_SCREW_GUN_DEFAULT = 0
STATUS_SCREW_GUN_TIGHTENING = 1
STATUS_SCREW_GUN_TIGHTENING_COMPLETE = 2
STATUS_SCREW_GUN_TIGHTENING_ERROR = 3
STATUS_SCREW_GUN_LOOSENING = 4
STATUS_SCREW_GUN_LOOSENING_COMPLETE = 5
STATUS_SCREW_GUN_LOOSENING_ERROR = 6


# 产品任务实体（里面还有嵌套的list实体、图片实体，是子类，在下面）
class ProductMission(BaseEntity):
    def __init__(self,
                 id: int,
                 mission_name: str,
                 mission_pn_code: str,
                 mission_status: int,
                 mission_product_sides: list,
                 creator: str,
                 last_updater: str,
                 mission_indexs: list = [0, 0],
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                                          # 实体id
        self.__mission_name = mission_name                      # 任务名称
        self.__mission_pn_code = mission_pn_code                # PN码
        self.__mission_status = mission_status                  # 任务状态
        self.__mission_indexs = mission_indexs                  # 当前正在进行操作的产品面/孔位的indexs
        CommonUtils.CheckArgumentType(mission_product_sides, list)
        for side in mission_product_sides:
            CommonUtils.CheckArgumentType(side, ProductSides)
        self.__mission_product_sides = mission_product_sides    # 产品面list

    def SetId(self, id: int):
        self.__id = id
    def SetMissionName(self, mission_name: str):
        self.__mission_name = mission_name
    def SetMissionPnCode(self, mission_pn_code: str):
        self.__mission_pn_code = mission_pn_code
    def SetMissionStatus(self, mission_status: int):
        self.__mission_status = mission_status
    def SetMissionIndexs(self, mission_indexs: list):
        self.__mission_indexs = mission_indexs
    def SetMissionProductSides(self, mission_product_sides: list):
        CommonUtils.CheckArgumentType(mission_product_sides, list)
        for side in mission_product_sides:
            CommonUtils.CheckArgumentType(side, ProductSides)
        self.__mission_product_sides = mission_product_sides

    def GetID(self) -> int:
        return self.__id
    def GetMissionName(self) -> str:
        return self.__mission_name
    def GetMissionPnCode(self) -> str:
        return self.__mission_pn_code
    def GetMissionStatus(self) -> int:
        return self.__mission_status
    def GetMissionIndexs(self) -> list:
        return self.__mission_indexs
    def GetMissionProductSides(self) -> list:
        return self.__mission_product_sides


# 产品面图片实体，子类之一
class ProductImage(BaseEntity):
    def __init__(self,
                 id: int,
                 image_original: Image.Image,
                 image_zooming_ratio: float,
                 image_relative_position: tuple,
                 creator: str,
                 last_updater: str,
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                                              # 实体id

        CommonUtils.CheckArgumentType(image_original, Image.Image)
        self.__image_original = image_original                      # 图片原始数据

        self.__image_zooming_ratio = image_zooming_ratio            # 图片缩放比例
        self.__image_relative_position = image_relative_position    # 图片相对位置

    def SetId(self, id: int):
        self.__id = id
    def SetImageOriginal(self, image_original: Image.Image):
        CommonUtils.CheckArgumentType(image_original, Image.Image)
        self.__image_original = image_original
    def SetImageZoomingRatio(self, image_zooming_ratio: float):
        self.__image_zooming_ratio = image_zooming_ratio
    def SetImageRelativePosition(self, image_relative_position: tuple):
        self.__image_relative_position = image_relative_position

    def GetID(self) -> int:
        return self.__id
    def GetImageOriginal(self) -> wx.Image:
        return self.__image_original
    def GetImageZoomingRatio(self) -> float:
        return self.__image_zooming_ratio
    def GetImageRelativePosition(self) -> tuple:
        return self.__image_relative_position

# 产品面实体，子类之一
class ProductSides(BaseEntity):
    def __init__(self,
                 id: int,
                 side_name: str,
                 side_image: ProductImage,
                 bolts: list,
                 creator: str,
                 last_updater: str,
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                  # 实体id
        self.__side_name = side_name    # 产品面名称
        self.__side_image = side_image  # 产品面的图片

        CommonUtils.CheckArgumentType(bolts, list)
        for bolt in bolts:
            CommonUtils.CheckArgumentType(bolt, ProductBolts)
        self.__bolts = bolts            # 螺栓点位list

    def SetId(self, id: int):
        self.__id = id
    def SetSideName(self, side_name: str):
        self.__side_name = side_name
    def SetSideImage(self, side_image: ProductImage):
        self.__side_image = side_image
    def SetBolts(self, bolts: list):
        CommonUtils.CheckArgumentType(bolts, list)
        for bolt in bolts:
            CommonUtils.CheckArgumentType(bolt, ProductBolts)
        self.__bolts = bolts

    def GetID(self) -> int:
        return self.__id
    def GetSideName(self) -> str:
        return self.__side_name
    def GetSideImage(self) -> ProductImage:
        return self.__side_image
    def GetBolts(self) -> list:
        return self.__bolts


# 螺栓点位实体，是子类之一，并且是子类[产品面]的子类
class ProductBolts(BaseEntity):
    def __init__(self,
                 id: int,
                 bolt_name: str,
                 bolt_position: tuple,
                 bolt_status: int,
                 creator: str,
                 last_updater: str,
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                          # 实体id
        self.__bolt_name = bolt_name            # 螺栓点位名称
        self.__bolt_position = bolt_position    # 螺栓点位坐标
        self.__bolt_status = bolt_status        # 螺栓点位状态（是不是放着还待定，如果放的话，应该考虑每个实体都加状态）

    def SetId(self, id: int):
        self.__id = id
    def SetBoltName(self, bolt_name: str):
        self.__bolt_name = bolt_name
    def SetBoltPosition(self, bolt_position: tuple):
        self.__bolt_position = bolt_position
    def SetBoltStatus(self, bolt_status: str):
        self.__bolt_status = bolt_status

    def GetID(self) -> int:
        return self.__id
    def GetSBoltName(self) -> tuple:
        return self.__bolt_position
    def GetBoltPosition(self) -> tuple:
        return self.__bolt_position
    def GetBoltStatus(self) -> int:
        return self.__bolt_status


# 实时数据实体
class RealtimeData:
    def __init__(self,
                 mission_id: int,
                 mission_indexs: tuple):
        self.mission_id = mission_id
        self.mission_indexs = mission_indexs
        self.torque = 0.0
        self.angle = 0

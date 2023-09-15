import wx
from PIL import Image
from typing import List

from models.base import BaseEntity
import utils.CommonUtils as CommonUtils


# 任务状态
STATUS_MISSION_DEFAULT                  = 0     # 任务状态 - 默认
STATUS_MISSION_READY                    = 1     # 任务状态 - 就绪
STATUS_MISSION_WORKING                  = 2     # 任务状态 - 工作中
STATUS_MISSION_ERROR                    = 3     # 任务状态 - 错误
STATUS_MISSION_FINISHED                 = 4     # 任务状态 - 完成

# 螺丝孔位工作状态
STATUS_SCREW_GUN_DEFAULT                = 0     # 螺栓点位状态 - 默认
STATUS_SCREW_GUN_TIGHTENING             = 1     # 螺栓点位状态 - 拧紧中
STATUS_SCREW_GUN_TIGHTENING_COMPLETE    = 2     # 螺栓点位状态 - 拧紧完成
STATUS_SCREW_GUN_TIGHTENING_ERROR       = 3     # 螺栓点位状态 - 拧紧错误
STATUS_SCREW_GUN_LOOSENING              = 4     # 螺栓点位状态 - 反松中
STATUS_SCREW_GUN_LOOSENING_COMPLETE     = 5     # 螺栓点位状态 - 反松完成
STATUS_SCREW_GUN_LOOSENING_ERROR        = 6     # 螺栓点位状态 - 反松错误


# 螺栓点位实体，是子类之一，并且是子类[产品面]的子类
class ProductBolt(BaseEntity):
    def __init__(self,
                 id: int,
                 bolt_name: str = "",
                 bolt_position: list = None,
                 bolt_description: str = "",
                 bolt_specification: float = 0.0,
                 tool_id: int = -1,
                 tool_description: str = "",
                 bit_specification: float = 0.0,
                 procedure_set: int = -1,
                 torque_limit: tuple = (0.0, 999.99),
                 angle_limit: tuple = (0, 99999),
                 bolt_status: int = STATUS_SCREW_GUN_DEFAULT,
                 creator: str = "",
                 last_updater: str = "",
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                                  # 实体id
        self.__bolt_name = bolt_name                    # 螺栓点位名称
        self.__bolt_position = bolt_position            # 螺栓点位在[已设定好的]产品图片中的坐标
        self.__bolt_description = bolt_description      # 螺栓点位描述
        self.__bolt_specification = bolt_specification  # 螺栓规格
        self.__tool_id = tool_id                        # 工具id
        self.__tool_description = tool_description      # 工具描述
        self.__bit_specification = bit_specification    # 批头规格
        self.__procedure_set = procedure_set            # pset=程序号
        self.__torque_limit = torque_limit              # 扭矩上下限
        self.__angle_limit = angle_limit                # 角度上下限
        self.__bolt_status = bolt_status                # 螺栓点位状态（是不是放着还待定，如果放的话，应该考虑每个实体都加状态）
        # 临时变量，用于一些变量切换前的中间状态/值等
        self.bolt_status_temp = None

    def SetID(self, id: int):
        self.__id = id
    def SetBoltName(self, bolt_name: str):
        self.__bolt_name = bolt_name
    def SetBoltPosition(self, bolt_position: list):
        self.__bolt_position = bolt_position
    def SetBoltDescription(self, bolt_description: str):
        self.__bolt_description = bolt_description
    def SetBoltSpecification(self, bolt_specification: float):
        self.__bolt_specification = bolt_specification
    def SetToolID(self, tool_id: int):
        self.__tool_id = tool_id
    def SetToolDescription(self, tool_description: str):
        self.__tool_description = tool_description
    def SetBitSpecification(self, bit_specification: float):
        self.__bit_specification = bit_specification
    def SetProcedureSet(self, procedure_set: int):
        self.__procedure_set = procedure_set
    def SetTorqueLimit(self, torque_limit: tuple):
        self.__torque_limit = torque_limit
    def SetAngleLimit(self, angle_limit: tuple):
        self.__angle_limit = angle_limit
    def SetBoltStatus(self, bolt_status: str):
        self.__bolt_status = bolt_status
        self.bolt_status_temp = None

    def GetID(self) -> int:
        return self.__id
    def GetBoltName(self) -> str:
        return self.__bolt_name
    def GetBoltPosition(self) -> list:
        return self.__bolt_position
    def GetBoltDescription(self) -> str:
        return self.__bolt_description
    def GetBoltSpecification(self) -> float:
        return self.__bolt_specification
    def GetToolID(self) -> int:
        return self.__tool_id
    def GetToolDescription(self) -> str:
        return self.__tool_description
    def GetBitSpecification(self) -> float:
        return self.__bit_specification
    def GetProcedureSet(self) -> int:
        return self.__procedure_set
    def GetTorqueLimit(self) -> tuple:
        return self.__torque_limit
    def GetAngleLimit(self) -> tuple:
        return self.__angle_limit
    def GetBoltStatus(self) -> int:
        return self.__bolt_status


# 产品面图片实体，子类之一
class ProductImage(BaseEntity):
    def __init__(self,
                 id: int,
                 image_original: Image.Image = None,
                 image_zooming_ratio: float = 0.0,
                 image_center_coordinate: tuple = (0, 0),
                 creator: str = "",
                 last_updater: str = "",
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                                              # 实体id

        CommonUtils.CheckArgumentType(image_original, Image.Image)
        self.__image_original = image_original                      # 图片原始数据

        self.__image_zooming_ratio = image_zooming_ratio            # 图片缩放比例
        self.__image_center_coordinate = image_center_coordinate    # 图片中心坐标

    def SetID(self, id: int):
        self.__id = id
    def SetImageOriginal(self, image_original: Image.Image):
        CommonUtils.CheckArgumentType(image_original, Image.Image)
        self.__image_original = image_original
    def SetImageZoomingRatio(self, image_zooming_ratio: float):
        self.__image_zooming_ratio = image_zooming_ratio
    def SetImageCenterCoordinate(self, image_center_coordinate: tuple):
        self.__image_center_coordinate = image_center_coordinate

    def GetID(self) -> int:
        return self.__id
    def GetImageOriginal(self) -> wx.Image:
        return self.__image_original
    def GetImageZoomingRatio(self) -> float:
        return self.__image_zooming_ratio
    def GetImageCenterCoordinate(self) -> tuple:
        return self.__image_center_coordinate


# 产品面实体，子类之一
class ProductSide(BaseEntity):
    def __init__(self,
                 id: int,
                 side_name: str = "",
                 side_image: ProductImage = None,
                 bolts: List[ProductBolt] = None,
                 creator: str = "",
                 last_updater: str = "",
                 create_time: str = CommonUtils.System_Current_Datetime(),
                 last_update_time: str = CommonUtils.System_Current_Datetime(),
                 is_deleted: bool = False):
        BaseEntity.__init__(self, creator, create_time, last_updater, last_update_time, is_deleted)
        self.__id = id                  # 实体id
        self.__side_name = side_name    # 产品面名称
        self.__side_image = side_image  # 产品面的图片

        CommonUtils.CheckArgumentType(bolts, list)
        for bolt in bolts:
            CommonUtils.CheckArgumentType(bolt, ProductBolt)
        self.__bolts = bolts            # 螺栓点位list

    def SetID(self, id: int):
        self.__id = id
    def SetSideName(self, side_name: str):
        self.__side_name = side_name
    def SetSideImage(self, side_image: ProductImage):
        self.__side_image = side_image
    def SetBolts(self, bolts: List[ProductBolt]):
        CommonUtils.CheckArgumentType(bolts, list)
        for bolt in bolts:
            CommonUtils.CheckArgumentType(bolt, ProductBolt)
        self.__bolts = bolts

    def GetID(self) -> int:
        return self.__id
    def GetSideName(self) -> str:
        return self.__side_name
    def GetSideImage(self) -> ProductImage:
        return self.__side_image
    def GetBolts(self) -> List[ProductBolt]:
        return self.__bolts


# 产品任务实体（里面还有嵌套的list实体、图片实体，是子类，在下面）
class ProductMission(BaseEntity):
    def __init__(self,
                 id: int,
                 mission_name: str = "",
                 mission_pn_code: str = -1,
                 mission_status: int = STATUS_MISSION_READY,
                 mission_product_sides: List[ProductSide] = None,
                 mission_indexs: list = None,
                 creator: str = "",
                 last_updater: str = "",
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
            CommonUtils.CheckArgumentType(side, ProductSide)
        self.__mission_product_sides = mission_product_sides    # 产品面list
        # 临时变量，用于一些变量切换前的中间状态/值等
        self.mission_status_temp = None

    def SetID(self, id: int):
        self.__id = id
    def SetMissionName(self, mission_name: str):
        self.__mission_name = mission_name
    def SetMissionPnCode(self, mission_pn_code: str):
        self.__mission_pn_code = mission_pn_code
    def SetMissionStatus(self, mission_status: int):
        self.__mission_status = mission_status
        self.mission_status_temp = None
    def SetMissionIndexs(self, mission_indexs: list):
        self.__mission_indexs = mission_indexs
    def SetMissionProductSides(self, mission_product_sides: List[ProductSide]):
        CommonUtils.CheckArgumentType(mission_product_sides, list)
        for side in mission_product_sides:
            CommonUtils.CheckArgumentType(side, ProductSide)
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
    def GetMissionProductSides(self) -> List[ProductSide]:
        return self.__mission_product_sides


# 实时数据实体
class RealtimeData:
    def __init__(self,
                 mission_id: int,
                 mission_indexs: list):
        self.mission_id = mission_id
        self.mission_indexs = mission_indexs
        self.torque = 0.0
        self.angle = 0
        self.coordinate = [-1, -1, -1]


    #     t = threading.Thread(target = self.test)
    #     t.start()
    #
    # def test(self):
    #     while True:
    #         self.torque += random.randrange(1, 50)
    #         self.angle += random.randrange(1, 20)
    #         time.sleep(0.1)


from PIL import Image

import models.ProductMission as pdctmsn


# 获取任务（产品）列表
def get_all_missions(obj) -> list:
    # TODO: get missions data from back-end api(s)
    # 这里先暂时手写，之后要调用后端api，让后端返回
    return [
        pdctmsn.ProductMission(
            id = 1,
            mission_name = "OP-10机盖装配",
            mission_pn_code = "12345678",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [0, 0],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [220, 450], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING_COMPLETE,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品中间才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [70, 150], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 2,
            mission_name = "任务名称2",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [1, 1],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [20, 90], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [20, 110], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 3,
            mission_name = "任务名称3",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [0, 1],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_DEFAULT,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [20, 240], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING_COMPLETE,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_DEFAULT,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [110, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 3,
            mission_name = "任务名称4",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [1, 0],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [90, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_DEFAULT,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_COMPLETE,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "我是螺栓", [50, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_DEFAULT,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 5,
            mission_name = "任务名称5",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [0, 1],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(3, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(4, "2号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 6,
            mission_name = "任务名称5",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [1, 1],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(3, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(4, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 7,
            mission_name = "任务名称5",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_DEFAULT,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [0, 0],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(3, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(4, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
        pdctmsn.ProductMission(
            id = 8,
            mission_name = "任务名称5",
            mission_pn_code = "555555",
            mission_status = pdctmsn.STATUS_MISSION_READY,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [0, 0],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(3, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(4, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_LOOSENING_ERROR,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        ),
    ]


# 获取当前任务进行的状态
def get_by_id(mission_id) -> pdctmsn.ProductMission:
    return pdctmsn.ProductMission(
            id = 1,
            mission_name = "OP-10机盖装配",
            mission_pn_code = "12345678",
            mission_status = pdctmsn.STATUS_MISSION_WORKING,
            creator = "创建人",
            last_updater = "创建人",
            mission_indexs = [0, 0],
            mission_product_sides = [
                pdctmsn.ProductSide(
                    id = 1,
                    side_name = "产品正面",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (1).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_DEFAULT,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                ),
                pdctmsn.ProductSide(
                    id = 2,
                    side_name = "产品正面才怪",
                    side_image = pdctmsn.ProductImage(1, Image.open("产品图片样图 (2).jpg"), 1, (-1, -1), "me", "me"),
                    creator = "创建人",
                    last_updater = "创建人",
                    bolts = [
                        pdctmsn.ProductBolt(1, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_TIGHTENING,
                                            creator = "创建人", last_updater = "创建人"),
                        pdctmsn.ProductBolt(2, "1号螺栓", [20, 50], bolt_status = pdctmsn.STATUS_SCREW_GUN_DEFAULT,
                                            creator = "创建人", last_updater = "创建人"),
                    ]
                )
            ]
        )


def update_by_id(mission_id) -> None:
    return None



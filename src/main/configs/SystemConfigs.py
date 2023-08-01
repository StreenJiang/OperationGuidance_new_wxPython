import wx

from src.main.controllers import apis, call_backs
from src.main.views.Content_Workplace import ContentWorkplace

# 系统菜单列表
main_menus_config = [
    {
        "id": "00001",                                          # 菜单ID，用于许可证识别（不可重复；00000代表默认enabled，不需要配置）
        "name": "用户操作",                                       # 菜单名称
        "icon": "configs/icons/user_operation.png",             # 菜单icon路径
        "view": None,                                           # 菜单所代表的视图（如果=None，则看子菜单的View；如果所有子菜单也没有视图，就代表是一个功能性按钮。比如退出按钮）
        "enabled": True,                                        # 菜单是否激活（根据许可证）
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
            wx.EVT_MOTION: [
                {
                    "api": apis.API_EVT_MOUSE_EVENTS_TEST,
                    "call_back": None
                },
            ],
        },
        "children": [                                               # 子菜单
            {
                "name": "手动操作",
                "icon": "configs/icons/manual_manipulate_tool.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "手动控制",
                "icon": "configs/icons/manual_control.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            },
        ]
    }, {
        "id": "00002",
        "name": "任务管理",
        "icon": "configs/icons/mission_management.png",
        "view": wx.Panel,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
        },
        "children": []
    }, {
        "id": "00003",
        "name": "工作台",
        "icon": "configs/icons/workplace.png",
        "view": ContentWorkplace,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_GET_PRODUCT_MISSIONS,
                    "call_back": call_backs.CALL_BACK_SHOW_PRODUCT_MISSIONS
                },
            ],
        },
        "children": []
    }, {
        "id": "00004",
        "name": "数据查询",
        "icon": "configs/icons/data_query.png",
        "view": wx.Panel,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
        },
        "children": []
    }, {
        "id": "00005",
        "name": "事件日志",
        "icon": "configs/icons/event_log.png",
        "view": wx.Panel,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
        },
        "children": []
    }, {
        "id": "00006",
        "name": "参数配置",
        "icon": "configs/icons/variable_settings.png",
        "view": None,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
        },
        "children": [
            {
                "name": "账户管理",
                "icon": "configs/icons/user_info.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "站点配置",
                "icon": "configs/icons/station_settings.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "通讯设备",
                "icon": "configs/icons/communication_device.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "串口设备",
                "icon": "configs/icons/serial_port_device.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "存储参数",
                "icon": "configs/icons/store_variables.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "开发者选项",
                "icon": "configs/icons/developer_choices.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "软件许可",
                "icon": "configs/icons/software_license.png",
                "view": wx.Panel,
                "events": {
                    wx.EVT_LEFT_DOWN: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "系统设置",
                "icon": "configs/icons/variable_settings.png",
                "events": {},
            },
        ]
    }, {
        "id": "00007",
        "name": "用户信息",
        "icon": "configs/icons/user_info.png",
        "view": wx.Panel,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_DOWN: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
        },
        "children": []
    }, {
        "id": "00000",
        "name": "退出",
        "icon": "configs/icons/exit.png",
        "view": None,
        "enabled": True,
        "events": {
            wx.EVT_LEFT_UP: [
                {
                    "api": apis.exit_confirmation,
                    "call_back": None
                },
            ],
        },
        "children": []
    },
]




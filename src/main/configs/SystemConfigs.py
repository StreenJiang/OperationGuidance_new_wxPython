import wx

from src.main.controllers import apis, call_backs

# 主窗体初始大小
SIZE_MAIN_FRAME_DEFAULT = (800, 600)
# 主窗体最小尺寸
SIZE_MAIN_FRAME_MINIMUM = (400, 300)

# 日志文件存储路径（以数组形式设置，以防以后有多个地方需要存储）
PATH_FILE_LOG = [
    "configs/logs/"
]

# 默认参数 - 颜色 - 系统背景颜色
COLOR_SYSTEM_BACKGROUND = "#F0F0F0"

# 默认参数 - 颜色 - 菜单栏的背景颜色
COLOR_MENU_BACKGROUND = "#3F3F3F"
# 默认参数 - 颜色 - 菜单按钮的背景颜色
COLOR_MENU_BUTTON_BACKGROUND = "#3F3F3F"
# 默认参数 - 颜色 - 菜单按钮触发后的颜色
COLOR_MENU_BUTTON_TOGGLE = "#FEFEFE"

# 默认参数 - 颜色 - 内容主体界面的背景颜色
COLOR_CONTENT_PANEL_BACKGROUND = "#F0F0F0"

# 默认参数 - 颜色 - 文本颜色_主题色
COLOR_TEXT_THEME = "#E86C10"


# 系统菜单列表
main_menus_config = [
    {
        "id": "00001", # 菜单ID，用于许可证识别（不可重复；00000代表默认enabled，不需要配置）
        "name": "用户操作", # 菜单名称
        "icon": "configs/icons/user_operation.png", # 菜单icon路径
        "enabled": True, # 菜单是否激活（根据许可证）
        "events": {
            wx.EVT_BUTTON: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
            wx.EVT_MOUSE_EVENTS: [
                {
                    "api": apis.API_EVT_MOUSE_EVENTS_TEST,
                    "call_back": None
                },
            ],
        },
        "children": [ # 子菜单
            {
                "name": "手动操作工具",
                "icon": "configs/icons/manual_manipulate_tool.png",
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "手动控制",
                "icon": "configs/icons/manual_control.png",
                "events": {
                    wx.EVT_BUTTON: [
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
        "name": "产品管理",
        "icon": "configs/icons/product_management.png",
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
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
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": call_backs.CALL_BACK_TEST
                },
            ],
        },
        "children": []
    }, {
        "id": "00004",
        "name": "数据查询",
        "icon": "configs/icons/data_query.png",
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
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
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
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
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
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
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "站点配置",
                "icon": "configs/icons/station_settings.png",
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "通讯设备",
                "icon": "configs/icons/communication_device.png",
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "串口设备",
                "icon": "configs/icons/serial_port_device.png",
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "存储参数",
                "icon": "configs/icons/store_variables.png",
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "开发者选项",
                "icon": "configs/icons/developer_choices.png",
                "events": {
                    wx.EVT_BUTTON: [
                        {
                            "api": apis.API_EVT_BUTTON_TEST,
                            "call_back": call_backs.CALL_BACK_TEST
                        },
                    ],
                },
            }, {
                "name": "软件许可",
                "icon": "configs/icons/software_license.png",
                "events": {
                    wx.EVT_BUTTON: [
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
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
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
        "enabled": True,
        "events": {
            wx.EVT_BUTTON: [
                {
                    "api": apis.API_EVT_BUTTON_TEST,
                    "call_back": None
                },
            ],
        },
        "children": []
    },
]




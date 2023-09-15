SIZE_MAIN_FRAME_DEFAULT                                 = (800, 600)                # 主窗体初始大小
SIZE_MAIN_FRAME_MINIMUM                                 = (400, 300)                # 主窗体最小尺寸
SIZE_SCROLL_BAR                                         = 16                        # 系统滚动条的最小宽度

PATH_FILE_LOG = [                                                                   # 日志文件存储路径（以数组形式设置，以防以后有多个地方需要存储）
    "configs/logs/",
]

LENGTH_MAIN_MENU                                        = 5                         # 主菜单名称字数
LENGTH_CHILD_MENU                                       = 7                         # 子菜单名称字数
PATH_LOGO_IMAGE                                         = "configs/icons/logo.png"  # logo图片存储路径

THREAD_POOL_TASK_MAS                                    = 10                        # 线程池异步运行最大数
THREAD_POOL_PREFIX                                      = "pool_thread"             # 线程池异步运行最大数

COLOR_COMMON_GREEN                                      = "#2AB514"                 # 默认参数 - 颜色 - 通用绿色（成功、完成等）
COLOR_COMMON_WHITE                                      = "#FEFEFE"                 # 默认参数 - 颜色 - 通用白色
COLOR_COMMON_RED                                        = "#F01414"                 # 默认参数 - 颜色 - 通用红色（错误）
COLOR_COMMON_DDDDDD                                     = "#DDDDDD"                 # 默认参数 - 颜色 - 通用淡灰色

COLOR_SYSTEM_LOGO                                       = "#E86C10"                 # 默认参数 - 颜色 - logo颜色（主题色）
COLOR_SYSTEM_BACKGROUND                                 = "#F0F0F0"                 # 默认参数 - 颜色 - 系统背景颜色

COLOR_MENU_BACKGROUND                                   = "#3F3F3F"                 # 默认参数 - 颜色 - 菜单栏的背景颜色
COLOR_MAIN_MENU_BUTTON_BACKGROUND                       = "#3F3F3F"                 # 默认参数 - 颜色 - 主菜单按钮的背景颜色
COLOR_CHILD_MENU_BUTTON_BACKGROUND                      = "#444444"                 # 默认参数 - 颜色 - 子菜单按钮的背景颜色
COLOR_MENU_BUTTON_TOGGLE                                = "#F0F0F0"                 # 默认参数 - 颜色 - 菜单按钮触发后的颜色

COLOR_CONTENT_PANEL_BACKGROUND                          = "#F0F0F0"                 # 默认参数 - 颜色 - 内容主体界面的背景颜色
COLOR_CONTENT_PANEL_INSIDE_BORDER                       = COLOR_COMMON_DDDDDD         # 默认参数 - 颜色 - 内容主体界面的框框颜色

COLOR_TEXT_BLACK                                        = "#222222"                 # 默认参数 - 颜色 - 文本颜色_黑色（不是纯黑，有一丁点的灰，但是几乎看不出来）
COLOR_TEXT_THEME                                        = COLOR_SYSTEM_LOGO         # 默认参数 - 颜色 - 文本颜色_主题色
COLOR_TEXT_MAIN_MENU                                    = COLOR_COMMON_WHITE        # 默认参数 - 颜色 - 菜单条上的文本颜色_白色
COLOR_TEXT_CONTROL_BACKGROUND                           = COLOR_COMMON_WHITE        # 默认参数 - 颜色 - 文本框背景颜色
COLOR_TEXT_CONTROL_FONT                                 = "#666666"                 # 默认参数 - 颜色 - 文本框字体颜色

COLOR_CONTENT_BLOCK_BORDER_1                            = COLOR_SYSTEM_LOGO         # 默认参数 - 颜色 - 内容块颜色边框_1_主题色
COLOR_CONTENT_BLOCK_BORDER_2                            = "#AAAAAA"                 # 默认参数 - 颜色 - 内容块颜色边框_2_淡灰色
COLOR_CONTENT_BLOCK_BORDER_3                            = "#222222"                 # 默认参数 - 颜色 - 内容块颜色边框_3_黑色（不是纯黑，有一丁点的灰，但是几乎看不出来）
COLOR_CONTENT_BLOCK_BACKGROUND                          = COLOR_COMMON_WHITE        # 默认参数 - 颜色 - 内容块背景颜色

COLOR_BUTTON_TEXT                                       = COLOR_COMMON_WHITE        # 默认参数 - 颜色 - 按钮文本颜色
COLOR_BUTTON_BACKGROUND                                 = COLOR_SYSTEM_LOGO         # 默认参数 - 颜色 - 按钮背景色_主题色
COLOR_BUTTON_FOCUSED                                    = "#F19753"                 # 默认参数 - 颜色 - 按钮捕捉到鼠标时的颜色
COLOR_BUTTON_CLICKED                                    = "#D05900"                 # 默认参数 - 颜色 - 按钮按下的颜色

COLOR_DEVICE_BUTTON_HOVER                               = "#FAFAFA"                 # 默认参数 - 颜色 - 设备小图标按钮鼠标移上时的颜色
COLOR_DEVICE_BUTTON_DOWN                                = "#D1D1D1"                 # 默认参数 - 颜色 - 设备小图标按钮鼠标按下时的颜色
COLOR_DEVICE_BUTTON_TOGGLED                             = "#D9D9D9"                 # 默认参数 - 颜色 - 设备小图标按钮被激活时的颜色

COLOR_WORKPLACE_BLOCK_TITLE_BACKGROUND                  = COLOR_COMMON_DDDDDD         # 默认参数 - 颜色 - 工作台任务操作界面小标题背景颜色
COLOR_WORKPLACE_BOLT_NUMBER                             = "#444444"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位文字
COLOR_WORKPLACE_BOLT_BORDER                             = "#444444"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位边框
COLOR_WORKPLACE_BOLT_BG_WAITING                         = "#D9D9D9"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_等待中
COLOR_WORKPLACE_BOLT_BG_WAITING_HOVER                   = "#E8E8E8"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_等待中_鼠标移上
COLOR_WORKPLACE_BOLT_BG_WAITING_KEY_DOWN                = "#CCCCCC"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_等待中_按钮按下
COLOR_WORKPLACE_BOLT_BG_WORKING                         = "#FAFF18"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_工作中
COLOR_WORKPLACE_BOLT_BG_WORKING_HOVER                   = "#FDFFA5"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_工作中_鼠标移上
COLOR_WORKPLACE_BOLT_BG_WORKING_KEY_DOWN                = "#E0E411"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_工作中_按钮按下
COLOR_WORKPLACE_BOLT_BG_DONE                            = COLOR_COMMON_GREEN        # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_已完成
COLOR_WORKPLACE_BOLT_BG_DONE_HOVER                      = "#7BCD6E"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_已完成_鼠标移上
COLOR_WORKPLACE_BOLT_BG_DONE_KEY_DOWN                   = "#1A9E05"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_已完成_按钮按下
COLOR_WORKPLACE_BOLT_BG_ERROR                           = COLOR_COMMON_RED          # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_错误
COLOR_WORKPLACE_BOLT_BG_ERROR_HOVER                     = "#F86565"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_错误_鼠标移上
COLOR_WORKPLACE_BOLT_BG_ERROR_KEY_DOWN                  = "#CB0303"                 # 默认参数 - 颜色 - 工作台主要工作区域-产品展示区域-螺丝点位背景_错误_按钮按下

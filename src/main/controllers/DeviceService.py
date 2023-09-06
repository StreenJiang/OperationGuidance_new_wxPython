import models.Device as dvs


# 获取设备列表
def get_devices(obj) -> list:
    # TODO: get devices from back-end api(s)
    return [
        dvs.Device(
            id = 1,
            device_name = "设备名称111",
            device_category = dvs.DEVICE_CATEGORY_TOOL,
            device_type = dvs.DEVICE_TYPE_TOOL_PF4000,
            device_ip = "192.168.1.1",
            device_port = 4040,
            device_status = dvs.DEVICE_STATUS_CONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
        dvs.Device(
            id = 2,
            device_name = "设备名称222222",
            device_category = dvs.DEVICE_CATEGORY_ARM,
            device_type = dvs.DEVICE_TYPE_ARM_CF01,
            device_ip = "192.168.1.2",
            device_port = 4041,
            device_status = dvs.DEVICE_STATUS_DISCONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
        dvs.Device(
            id = 3,
            device_name = "设备名称3333333",
            device_category = dvs.DEVICE_CATEGORY_ARM,
            device_type = dvs.DEVICE_TYPE_ARM_CF01,
            device_ip = "192.168.1.2",
            device_port = 4042,
            device_status = dvs.DEVICE_STATUS_CONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
        dvs.Device(
            id = 4,
            device_name = "设备名称44444444",
            device_category = dvs.DEVICE_CATEGORY_ARM,
            device_type = dvs.DEVICE_TYPE_ARM_CF01,
            device_ip = "192.168.1.2",
            device_port = 4043,
            device_status = dvs.DEVICE_STATUS_CONNECTED,
            creator = "创建人",
            last_updater = "创建人"
        ),
    ]

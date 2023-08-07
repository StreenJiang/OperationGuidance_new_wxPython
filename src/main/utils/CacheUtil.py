from datetime import datetime

# 缓存变量
cache = {}

def Set(key, value, timeout):
    """
        设置缓存变量
        :param key: 缓存数据的key
        :param value: 缓存数据的value（需要缓存的数据）
        :param timeout: 超时时间（单位秒）
    """
    cache[key] = {}
    cache[key]["value"] = value
    cache[key]["timeout"] = timeout
    cache[key]["time"] = datetime.now()

def Get(key):
    """
        获取缓存数据
        :param key: 缓存数据的key
        :return: 返回缓存数据。如果超时则返回None
    """
    if key in cache.keys():
        time = cache[key]["time"]
        time_diff = datetime.now() - time
        if time_diff.seconds > cache[key]["timeout"]:
            cache[key] = None
            return None
        else:
            return cache[key]["value"]
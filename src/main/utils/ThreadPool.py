import traceback

from concurrent.futures import ThreadPoolExecutor, Future

# 线程池全局变量
threadPool: ThreadPoolExecutor

def initiate_pool(max_workers, thread_name_prefix) -> bool:
    """
        创建线程池
        :return: 创建成功则返回 True，否则返回 False
    """
    try:
        global threadPool
        threadPool = ThreadPoolExecutor(max_workers = max_workers,
                                        thread_name_prefix = thread_name_prefix)
        print("线程池初始化成功")
        return True
    except Exception as e:
        print("线程池初始化失败，e: ", e)
        traceback.print_exc()
    return False

def submit(task: callable, *args, **kws) -> Future:
    """
        将线程函数提交给线程池管理
        :param task: 要执行的线程函数
        :return: Future对象
    """
    return threadPool.submit(task, *args, **kws)



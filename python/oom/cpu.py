import threading
import multiprocessing

def cpu_intensive_task():
    while True:
        # 无限循环进行一些计算
        pass

if __name__ == "__main__":
    # 获取CPU核心数量
    num_cores = multiprocessing.cpu_count()
    print(f"检测到 {num_cores} 个CPU核心，将创建相应数量的线程")

    # 为每个CPU核心创建一个线程
    for _ in range(num_cores):
        thread = threading.Thread(target=cpu_intensive_task)
        thread.daemon = True
        thread.start()

    # 主线程也加入计算
    cpu_intensive_task()

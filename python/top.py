#30s/T
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# 定义一个函数来解析日志行并提取所需信息
def extract_info(line):
    fields = line.split(',')
    if len(fields) > 6:  # 确保有足够的字段
        try:
            # 分割第七个字段以获取冒号分隔的部分
            parts = fields[6].split(':')
            if len(parts) > 1:
                # 分割第二部分以获取双引号内的内容
                quoted_part = parts[1].split('"')[1]  # 假设双引号内的内容是我们想要的
                return quoted_part  
        except IndexError:
            pass  # 如果分割失败，则忽略此行
    return None

def process_file_segment(file_segment, result_dict):
    info_list = [extract_info(line.strip()) for line in file_segment if line.strip()]
    for info in info_list:
        if info is not None:
            result_dict[info] = result_dict.get(info, 0) + 1

if __name__ == "__main__":
    topN = int(sys.argv[1])
    chunk_size = int(sys.argv[2])
    result_dict = {}
  
    start_time = time.time()

    futures = []
    chunk = []
    lineNo = 0
    with open('vpndns.log', 'r', encoding='utf-8', errors='ignore') as file, ThreadPoolExecutor(max_workers=8) as executor:
        for line in file:
            lineNo += 1
            chunk.append(line)
            if len(chunk) == chunk_size:
                future = executor.submit(process_file_segment, chunk, result_dict)
                futures.append(future)
                chunk = []
        # 不要忘记添加最后一块（如果不足chunk_size）
        if chunk:
            future = executor.submit(process_file_segment, chunk, result_dict)
            futures.append(future)

    # 等待所有任务完成
    for future in futures:
        future.result()  # 这里可以捕获异常，但在这个例子中我们忽略了它们
  
    # 排序结果
    sorted_info_counts = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
  
    # 打印结果
    i = 0
    for item, count in sorted_info_counts:
        print("%s: %d" % (item, count))
        i += 1
        if i >= topN:
            break
  
    end_time = time.time()
    run_time = end_time - start_time
    print("脚本运行时间: %.2f 秒, lineNo = %d" % (run_time, lineNo))
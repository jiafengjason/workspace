import argparse
import concurrent.futures
import csv
import dns.resolver
import requests
import uuid
import random
import threading
import time
from itertools import islice
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

URL = None

# 请求头
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Python/3.9",
    "Authorization": "Basic cm9vdDplbmxpbmtAMjAyMw=="
}

# 线程安全的计数器
success_count = 0
fail_count = 0
lock = threading.Lock()

def send_request(app):
    global success_count, fail_count
    
    # 随机生成数据
    data = {
        "id": app['id'],
        "type": "cs",
        "enable": True,
        "isFake": True,
        "name": app['domain'],
        "server": f"https://{app['domain']}",
        "method": "http",
        "status": "",
        "score": "90",
        "reason": "",
        "secauth": False,
        "enhancedAuthId": "",
        "urlPermissionEnable": False,
        "certId": "",
        "ipv4s": [],
        "serviceSso": None,
        "serviceTerminal": None,
        "accountFilling": None
    }

    try:
        response = requests.post(
            URL,
            json=data,
            headers=headers,
            verify=False,
            timeout=10
        )
        
        # 检查响应状态码
        if response.status_code == 200:
            with lock:
                success_count += 1
            print(f"Success: {response.status_code} - {data['id']}")
        else:
            with lock:
                fail_count += 1
            print(f"Failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        with lock:
            fail_count += 1
        print(f"Error: {str(e)}")

# 多线程发送请求
def run_concurrent_requests(domains, max_threads):
    threads = []
    for app in apps:
        t = threading.Thread(target=send_request, args=(app,))
        threads.append(t)
        t.start()
        
        # 控制并发线程数
        while threading.active_count() > max_threads:
            time.sleep(0.1)
    
    # 等待所有线程完成
    for t in threads:
        t.join()

    print(f"\nCompleted: {success_count}成功, {fail_count}失败")

def dns_query(hostname, dns_server, record_type="A", timeout=3):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    resolver.timeout = timeout
    resolver.lifetime = timeout * 2  # 总超时稍长于单次超时

    try:
        answers = resolver.resolve(hostname, record_type)
        results = [answer.to_text() for answer in answers]
        print(results)
        return (hostname, record_type, results)
    except Exception as e:
        print(str(e))
        return (hostname, record_type, f"ERROR: {str(e)}")

def thread_task(app, args):
    #send_request(app)
    dns_query(app['domain'], args.ip)

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ip",
        type=str,
        default="192.168.113.242",
        #required=True,
        help="Server host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=58679,
        help="Server port"
    )
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=50,
        help="Concurrent num"
    )
    parser.add_argument(
        "-t", "--total",
        type=int,
        default=1,
        help="User total count"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v: INFO, -vv: DEBUG)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = setup_args()
    URL = f"https://{args.ip}:{args.port}/engateway/api/app/_add"
    
    with open('domain1.csv', mode='r', encoding='gbk') as file:
        csv_reader = csv.DictReader(file)
        rows = islice(csv_reader, args.total)
        apps = list(rows)
        #run_concurrent_requests(apps, args.concurrent)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrent) as executor:
            futures = [executor.submit(send_request, app, args) for app in apps]
            concurrent.futures.wait(futures)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrent) as executor:
            futures = [executor.submit(thread_task, app, args) for app in apps]
            concurrent.futures.wait(futures)
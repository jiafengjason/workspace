import argparse
import logging
import base64
import csv
import os
import random
import requests
import json
import sys
import concurrent.futures
import time
from itertools import islice
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from functools import wraps
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# 全局配置
SERVER = None
MAX_WORKERS = 25  # 根据实际机器性能调整
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRIES = 3  # 最大重试次数
RETRY_BACKOFF_FACTOR = 1  # 重试退避因子

class AESUtils:
    @staticmethod
    def encrypt(data: str, key: str, iv: str) -> str:
        cipher = AES.new(
            key.encode('utf-8'), 
            AES.MODE_CBC, 
            iv.encode('utf-8')
        )
        encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def decrypt(data: str, key: str, iv: str) -> str:
        cipher = AES.new(
            key.encode('utf-8'), 
            AES.MODE_CBC, 
            iv.encode('utf-8')
        )
        decrypted = unpad(
            cipher.decrypt(base64.b64decode(data)), 
            AES.block_size
        )
        return decrypted.decode('utf-8')

def send_request(
    session: requests.Session,
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    default_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
        "Content-Type": "application/json;charset=UTF-8",
        "cpuArch": "X86"
    }
    final_headers = {**default_headers, **(headers or {})}
    if final_headers:
        for key, value in final_headers.items():
            if isinstance(value, str):
                final_headers[key] = value.encode('utf-8').decode('latin-1') if any(ord(c) > 127 for c in value) else value
            else:
                final_headers[key] = str(value)
    try:
        if method.upper() == "GET":
            response = session.get(
                f"{SERVER}{url}",
                headers=final_headers,
                verify=False,
                timeout=REQUEST_TIMEOUT
            )
        elif method.upper() == "POST":
            response = session.post(
                f"{SERVER}{url}",
                json=json_data,
                headers=final_headers,
                verify=False,
                timeout=REQUEST_TIMEOUT
            )

        response.raise_for_status()  # 检查HTTP状态码

        # 尝试解析JSON，失败则返回文本
        try:
            data = response.json()
            if data["code"] != "200":
                logging.info(f"请求失败: {url} - {data}")
            return response.json()
        except ValueError:
            return {"raw_response": response.text}

    except requests.exceptions.RequestException as e:
        logging.info(f"请求失败: {url} - {str(e)}")
        return None
    except Exception as e:
        logging.info(f"处理响应失败: {url} - {str(e)} - {final_headers}")
        return None

def create_session() -> requests.Session:
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=[408, 429, 500, 502, 503, 504]
    )
    
    # 配置适配器
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=MAX_WORKERS,
        pool_maxsize=MAX_WORKERS
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return (end - start, result)  # 返回(耗时, 结果)
    return wrapper

@time_it
def thread_task(account):
    session = requests.Session()

    headers = {
        "FeatureCode": account["FeatureCode"],
        "Model": account["UserDeviceName"],
        "SystemInfo": account["SystemInfo"],
        "TerminalInfo": account["TerminalInfo"],
        "UserDeviceName": account["UserDeviceName"]
    }

    preLoginUrls = [
        ("GET", f"/enclient/api/users/device/access/check?featureCode={account['FeatureCode']}&terminalInfo={account['TerminalInfo']}", None, "检测设备是否准入"),
        ("POST", f"/enclient/api/users/select/mqtt/server/conf", {"featureCode":account['FeatureCode']}, "获取mqtt相关信息"),
        ("GET", f"/enclient/api/users/client/auth/generateKey", None, "生成会话信息"),
        ("GET", f"/enclient/api/users/device/access/check?featureCode={account['FeatureCode']}&terminalInfo={account['TerminalInfo']}", None, "检测设备是否准入"),
        ("GET", f"/enclient/api/users/device/managerPolicy?featureCode={account['FeatureCode']}", None, "设备管理类信息"),
        ("GET", f"/enclient/api/users/device/watermarkPolicy?featureCode={account['FeatureCode']}", None, "设备水印配置信息"),
        ("GET", f"/enclient/api/users/pkgRelease/latestOut?basicType=Basic&type=EnUES&version=3.2.0.9037", None, "获取终端最新版本号"),
        ("GET", f"/enclient/api/users/pkgRelease/latestOut?basicType=Basic&type=EnUES&version=3.2.0.9037", None, "获取终端最新版本号"),
        ("GET", f"/enclient/api/users/client/auth/generateKey", None, "生成会话信息"),
        ("GET", f"/enclient/api/users/pkgRelease/latestOut?basicType=Basic&type=EnUES&version=3.2.0.9037", None, "获取终端最新版本号"),
        ("POST", f"/enclient/api/users/custom/page/login/cfg/select", None, "前端获取页面配置信息"),
        ("GET", f"/enclient/api/users/pkgRelease/latestOut?basicType=Basic&type=EnUES&version=3.2.0.9037", None, "获取终端最新版本号"),
        ("GET", f"/enclient/api/users/device/access/check?featureCode={account['FeatureCode']}&terminalInfo={account['TerminalInfo']}", None, "检测设备是否准入"),
        ("GET", f"/enclient/api/users/client/auth/generateKey", None, "生成会话信息"),
        ("POST", f"/enclient/api/users/terminal/server_list", {"f":account['FeatureCode'], "k":"0123456789012345"}, "服务器配置信息更新同步"),
        ("GET", f"/enclient/api/users/device/managerPolicy?featureCode={account['FeatureCode']}", None, "设备管理类信息"),
        ("GET", f"/enclient/api/users/device/watermarkPolicy?featureCode={account['FeatureCode']}", None, "设备水印配置信息"),
    ]
    for method, url, data, desc in preLoginUrls:
        result = send_request(session, url, method, headers=headers, json_data=data)
        logging.debug(f"{account['name']} - {desc}: {result}")

    result = send_request(session, "/enclient/api/users/client/auth/generateKey", "GET", headers= headers)
    if not result or "data" not in result:
        print(f"{account['name']} generateKey fail")
        return
    enToken = result["data"]["enToken"]
    key = enToken.split("-")[-1]
    
    iv = key[::-1]
    pwd = "111111"
    
    passwd = AESUtils.encrypt(pwd, key, iv)
    
    headers["Authorization"] = f"Bearer {enToken}"
    data = {
        "account": account["name"],
        "passwd": passwd,
        "type": "local"
    }
    result = send_request(session, "/enclient/api/users/auth/login", "POST", headers= headers, json_data = data)
    userId = result["data"]["userId"]
    
    loginUrls = [
        ("GET", "/enclient/api/users/pkgRelease/latest?basicType=Basic&type=EnUES&version=3.2.0.0012", None, "获取终端最新版本号"),
        ("POST", "/enclient/api/users/device/bind", {
            "featureCode": account["FeatureCode"],
            "model": account["UserDeviceName"],
            "systemInfo": account["SystemInfo"],
            "terminalInfo": account["TerminalInfo"],
            "userDeviceName": account["UserDeviceName"],
            "localAddr": account["localAddr"],
            "deviceModel": "VMware20,1",
            "macAddress": account["macAddress"],
            "serialNumber": "VMware-56 4d 85 4a 55 dc 55 1e-42 07 61 dd a8 58 cb cb",
            "manuFacturer": "VMware, Inc.",
            "terminalVersion": None,
            "registerMethod": None
        }, "检测设备是否注册"),
        ("POST", f"/enclient/api/users/select/mqtt/server/conf", {"featureCode": account['FeatureCode'],"userId":userId}, "获取mqtt相关信息"),
        ("GET", "/enclient/api/users/device/terminal/detection/cycle", None, "获取采集组件相关策略"),
        ("GET", "/enclient/api/users/device/getDeviceConfig", None, "空间策略缓存配置,进程管控策略"),
        ("GET", "/enclient/api/users/device/getDeviceExecutePolicy", None, "浏览器访问限制策略"),
        ("GET", "/enclient/api/users/terminal/networkControl", None, "网络控制策略"),
        ("GET", "/enclient/api/users/terminal/rules", None, "网关列表相关信息"),
        ("GET", f"/enclient/api/users/device/access/check?featureCode={account['FeatureCode']}&terminalInfo={account['TerminalInfo']}", None, "检测设备是否准入"),
        ("GET", f"/enclient/api/users/device/managerPolicy?featureCode={account['FeatureCode']}", None, "设备管理类信息"),
        ("GET", f"/enclient/api/users/device/watermarkPolicy?featureCode={account['FeatureCode']}", None, "设备水印配置信息"),
        ("GET", "/enclient/api/users/message/list", None, "获取消息中心信息"),
        ("GET", "/enclient/api/users/safeSpace/getPolicy", None, "获取空间策略"),
        ("GET", "/enclient/api/users/device/getReportInterval", None, "获取日志上报时间"),
        ("GET", "/enclient/api/users/pkgRelease/latest?basicType=UI&type=UES&version=3.2.0.9042", None, "获取终端最新版本号"),
        ("GET", "/enclient/api/users/pkgRelease/latest?basicType=Basic&type=EnUES&version=3.2.0.9042", None, "获取终端最新版本号"),
        ("POST", f"/enclient/api/users/custom/page/login/cfg/select", None, "前端获取页面配置信息"),
        ("POST", f"/enclient/api/users/custom/page/login/cfg/select", None, "前端获取页面配置信息"),
        ("GET", "/enclient/api/users/message/count", None, "获取消息中心信息总数"),
        ("GET", "/enclient/api/users/info", None, "获取身份个人信息"),
        ("POST", "/enclient/api/client/user/getUserGroupedServiceList", {"serviceName": ""}, "获取应用列表"),
        ("POST", "/enclient/api/client/playStore/software/page", {"chipSoc":"X64","featureCode":account['FeatureCode'],"osInfo":"Windows 11","platformName":"Windows","softwareNameLk":"EnDesktop"}, "应用市场应用查询"),
        ("POST", "/enclient/api/users/terminal/gateway/uploadChoosedGateway", {"changeType":"2","unique":"00000000000000002"}, "上报连接的网关"),
        ("GET", "/enclient/api/users/safeSpace/getPolicy", None, "获取空间策略"),
        ("POST", "/enclient/api/users/client/updateUserSession", {"virtualIp":"1.1.0.1","virtualIpV6":"1001::1"}, "上报网络虚拟IP地址"),
        ("GET", "/enclient/api/users/safeSpace/getPolicy", None, "获取空间策略"),
        ("GET", "/enclient/api/users/third/customAuth/getRedirectUrl", None, "三方认证信息"),
        ("GET", "/enclient/api/users/terminal/tunnel_policy", None, "三方隧道"),
        ("GET", "/enclient/api/users/safeSpace/getPolicy", None, "获取空间策略"),
        ("GET", "/enclient/api/users/third/customAuth/getRedirectUrl", None, "三方认证信息"),
        ("GET", "/enclient/api/users/info", None, "获取身份个人信息"),
        ("POST", "/enclient/api/users/device/list/get", {"deviceType": "","userId":userId}, "前端查看活动设备列表"),
        ("POST", "/enclient/api/users/person/select/enableIsOpened", None, "前端获取第三方账号绑定状况"),
        ("GET", "/enclient/api/users/pkgRelease/latest?basicType=UI&type=UES&version=3.2.0.9042", None, "获取终端最新版本号"),
        ("GET", "/enclient/api/users/pkgRelease/latest?basicType=UI&type=UES&version=3.2.0.9042", None, "获取终端最新版本号"),
        ("GET", "/enclient/api/users/pkgRelease/latest?basicType=UI&type=UES&version=3.2.0.9042", None, "获取终端最新版本号"),
        ("POST", f"/enclient/api/users/custom/page/login/cfg/select", None, "前端获取页面配置信息"),
        ("POST", "/enclient/api/client/user/getUserGroupedServiceList", {"serviceName": ""}, "获取应用列表"),
        ("GET", f"/enclient/api/users/client/auth/generateKey", None, "生成会话信息"),
        ("POST", f"/enclient/api/users/custom/page/login/cfg/select", None, "前端获取页面配置信息"),
        ("POST", "/enclient/api/users/terminal/checkPolicyVersion", [
            {"policyType": "NETWORK_CONTROL_POLICY", "version": 36},
            {"policyType": "TERMINAL_RULES_POLICY", "version": 2}
        ], "策略更新"),
    ]

    for method, url, data, desc in loginUrls:
        result = send_request(session, url, method, headers=headers, json_data=data)
        logging.debug(f"{account['name']} - {desc}: {result}")

    session.close()

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ip",
        type=str,
        default="192.168.108.49",
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
        default=25,
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

def setup_logging(verbosity=0):
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbosity, len(levels) - 1)]
    
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=level,
        stream=sys.stdout
    )

if __name__ == "__main__":
    args = setup_args()
    setup_logging(args.verbose)
    SERVER = f"https://{args.ip}:{args.port}"

    processed_accounts = 0
    try:
        with open('account.csv', mode='r', encoding='gbk') as file:
            csv_reader = csv.DictReader(file)
            rows = islice(csv_reader, args.total)
            accounts = list(rows)

            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrent) as executor:
                futures = []
                for account in accounts:
                    future = executor.submit(thread_task, account)
                    future.add_done_callback(lambda _: globals().update(processed_accounts=processed_accounts+1))
                    futures.append(future)
                    
                # 显示进度
                while not all(f.done() for f in futures):
                    print(f"\nInprogress: {processed_accounts}/{len(accounts)}", end="")
                    time.sleep(0.5)
                
                execution_times = []
                for future in concurrent.futures.as_completed(futures):
                    elapsed_time, _ = future.result()
                    execution_times.append(elapsed_time)
                    # 检查是否有异常
                    if future.exception():
                        logging.error(f"task fail: {future.exception()}")
                        
            # 计算统计量
            avg_time = sum(execution_times) / len(execution_times)
            print(f"\n平均耗时: {avg_time:.2f}s")
            print(f"总耗时: {sum(execution_times):.2f}s")
            print(f"最大耗时: {max(execution_times):.2f}s")
            print(f"最小耗时: {min(execution_times):.2f}s")

    except Exception as e:
        logging.error(f"主程序异常: {str(e)}")


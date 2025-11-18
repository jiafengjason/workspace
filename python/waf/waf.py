#python waf.py https://webvpn1.sdwm.cn:7116/web-terminal/websocket-tunnel?token=D85671B9C561E329A529A6A7CE6CB8AE08D5E4987FDBC53B74F6BDB0830851BD&GUAC_DATA_SOURCE=default&GUAC_ID=rdp%3A%2F%2F10.10.1.11%3A3389%2F145ea030ad5b440ab50351e4331fe909&GUAC_TYPE=c&GUAC_WIDTH=1920&GUAC_HEIGHT=408&GUAC_DPI=96&GUAC_TIMEZONE=Asia%2FShanghai&GUAC_AUDIO=audio%2FL8&GUAC_AUDIO=audio%2FL16&GUAC_IMAGE=image%2Fjpeg&GUAC_IMAGE=image%2Fpng&GUAC_IMAGE=image%2Fwebp
import requests
import time
import subprocess
import re
import sys
import statistics
from urllib.parse import urlparse
from wafw00f import main

def check_waf_headers(url):
    """通过HTTP响应头检测WAF"""
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        
        waf_indicators = {
            'server': ['cloudflare', 'akamai', 'imperva', 'f5', 'barracuda', 
                      'fortinet', 'sucuri', 'aws', 'azurewaf'],
            'x-powered-by': ['cloudflare', 'akamai'],
            'x-cache': ['cloudflare'],
            'x-waf': [],
            'x-protected-by': [],
            'x-firewall': []
        }
        
        detected_waf = []
        for header, values in headers.items():
            header_lower = header.lower()
            value_lower = str(values).lower()
            
            # 检查特定的WAF头
            if any(waf in header_lower for waf in ['waf', 'firewall', 'shield']):
                detected_waf.append(f"{header}: {values}")
            
            # 检查已知WAF标识
            for waf_name in waf_indicators.get(header_lower, []):
                if waf_name in value_lower:
                    detected_waf.append(f"{header}: {waf_name}")
        
        return detected_waf if detected_waf else "未检测到明显WAF标识"
    
    except Exception as e:
        return f"检测失败: {e}"

def waf_fingerprinting(url):
    """通过发送特定payload进行WAF指纹识别"""
    
    # 常见的WAF测试payload
    test_payloads = [
        "../../etc/passwd",
        "<script>alert('xss')</script>",
        "1' OR '1'='1",
        "UNION SELECT",
        "../../../etc/passwd",
        "eval(",
        "base64_decode",
    ]
    
    waf_signatures = {
        'cloudflare': ['cloudflare', 'cf-ray', 'attention required'],
        'akamai': ['akamai', 'denied by akamai'],
        'imperva': ['incapsula', 'imperva'],
        'f5': ['bigip', 'f5', 'the requested url was rejected'],
        'fortinet': ['fortigate', 'fortinet'],
        'sucuri': ['sucuri', 'access denied - sucuri'],
    }
    
    results = []
    
    for payload in test_payloads:
        try:
            test_url = f"{url}?test={payload}"
            response = requests.get(test_url, timeout=3)
            
            # 检查响应特征
            content_lower = response.text.lower()
            status_code = response.status_code
            
            # 403/406等状态码可能表示WAF拦截
            if status_code in [403, 406, 419, 500]:
                for waf_name, signatures in waf_signatures.items():
                    if any(sig in content_lower for sig in signatures):
                        results.append(f"检测到 {waf_name} - Payload: {payload}")
            
            # 检查自定义拦截页面
            if any(keyword in content_lower for keyword in ['blocked', 'forbidden', 'firewall', 'waf']):
                results.append(f"疑似WAF拦截 - keyword")
                
            time.sleep(0.5)  # 避免请求过快
            
        except requests.exceptions.RequestException as e:
            results.append(f"请求失败: {payload} - {e}")
    
    return results

def ttl_analysis(hostname):
    """通过TTL值分析网络路径"""
    try:
        # 执行traceroute（Linux/Mac）
        result = subprocess.run(['traceroute', hostname], 
                              capture_output=True, text=True, timeout=30)
        
        # 或者使用ping分析TTL（跨平台）
        # ping_result = subprocess.run(['ping', '-c', '4', hostname], capture_output=True, text=True, timeout=10)
        
        ttl_pattern = r'ttl=(\d+)'
        ttls = re.findall(ttl_pattern, result.stdout)
        
        if ttls:
            ttl_value = int(ttls[0])
            # TTL分析：常见初始TTL值
            initial_ttls = {128: 'Windows', 64: 'Linux/Unix', 255: '网络设备'}
            
            # 如果TTL异常，可能中间有设备
            if ttl_value not in [128, 64, 255] and ttl_value < 60:
                return f"TTL异常 ({ttl_value})，可能存在中间设备"
            else:
                return f"TTL正常 ({ttl_value})，疑似 {initial_ttls.get(ttl_value, '未知')}"
        
        return "无法获取TTL信息"
        
    except Exception as e:
        return f"TTL分析失败: {e}"

def use_wafw00f(target):
    """使用wafw00f工具进行专业检测"""
    try:
        detector = main.WAFW00F(target)
        waf = detector.identwaf()
        if(waf):
            return waf[0]
        else:
            return ""
    except Exception as e:
        print(e)
        return ""

def use_nikto(target):
    """使用nikto进行漏洞扫描（可间接检测WAF）"""
    try:
        result = subprocess.run(['nikto', '-h', target, '-o', 'nikto_scan.html'],
                              capture_output=True, text=True, timeout=120)
        return "扫描完成，查看nikto_scan.html"
    except FileNotFoundError:
        return "nikto未安装，请使用: yum install nikto"
    except Exception as e:
        return f"Nikto扫描失败: {e}"

def timing_analysis(url):
    """通过响应时间分析判断WAF"""
    normal_requests = []
    malicious_requests = []
    
    # 正常请求
    for i in range(5):
        start = time.time()
        requests.get(url)
        end = time.time()
        normal_requests.append(end - start)
        time.sleep(1)
    
    # 恶意请求（触发WAF检测）
    malicious_payloads = ["' OR 1=1--", "<script>alert(1)</script>"]
    
    for payload in malicious_payloads:
        start = time.time()
        try:
            requests.get(f"{url}?q={payload}", timeout=5)
        except:
            pass
        end = time.time()
        malicious_requests.append(end - start)
        time.sleep(1)
    
    # 分析时间差异
    if malicious_requests and normal_requests:
        avg_normal = statistics.mean(normal_requests)
        avg_malicious = statistics.mean(malicious_requests)
        
        # 如果恶意请求明显变慢，可能存在WAF
        if avg_malicious > avg_normal * 2:
            return f"疑似存在WAF: 正常请求{avg_normal:.3f}s, 恶意请求{avg_malicious:.3f}s"
        else:
            return f"未检测到WAF时间差异: 正常{avg_normal:.3f}s, 恶意{avg_malicious:.3f}s"
    
    return "时间分析失败"

if __name__ == "__main__":
    target_url = "https://www.baidu.com"
    parsed = urlparse(target_url)
    target = parsed.netloc
    
    print(target)
    
    print(f"开始检测目标: {target_url}")
    print("=" * 50)
    
    # 1. HTTP头检测
    print("1. HTTP头分析:")
    header_result = check_waf_headers(target_url)
    print(f"   {header_result}")
    
    # 2. TTL分析
    print("2. TTL分析:")
    ttl_result = ttl_analysis(target)
    print(f"   {ttl_result}")
    
    # 3. 时间延迟分析
    print("3. 时间延迟分析:")
    timing_result = timing_analysis(target_url)
    print(f"   {timing_result}")
    
    # 4. 主动指纹识别
    print("4. 主动指纹识别:")
    fingerprint_results = waf_fingerprinting(target_url)
    for result in fingerprint_results[:3]:  # 显示前3个结果
        print(f"   {result}")
    
    # 5. wafw00f检测
    print("5. wafw00f检测:")
    print(use_wafw00f(target_url))
    
    # 6. Nikto扫描
    print("6. Nikto扫描:")
    print(use_nikto(target))
    
    print("=" * 50)
    print("检测完成")

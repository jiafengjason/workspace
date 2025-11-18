import random
import string
import sys
import time
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

def generate_random_subdomains(wildcard_domain, total):
    if not wildcard_domain.startswith('*.'):
        raise ValueError("泛域名格式不正确，应以*开头，例如 *.example.com")
    
    main_domain = wildcard_domain[2:]
    subdomains = set()
    
    while len(subdomains) < total:
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        subdomains.add(f"{random_str}.{main_domain}")
    
    return list(subdomains)

def dns_query(domain, dns_ip, dns_port):
    print(f"dns_query: {domain} {dns_ip} {dns_port}")
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_ip]
    resolver.port = dns_port
    try:
        answers = resolver.resolve(domain, 'A', lifetime=2)
        return [rdata.address for rdata in answers]
    except dns.resolver.NoAnswer:
        print(f"No answer from {dns_ip}:{dns_port} for domain {domain}")
        return []
    except dns.resolver.NXDOMAIN:
        print(f"Domain {domain} does not exist")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def batch_executor(subdomains, dns_ip, dns_port, batch_size):
    total = len(subdomains)
    
    with ThreadPoolExecutor(max_workers=100) as executor:  # 设置足够大的线程池
        for i in range(0, total, batch_size):
            batch = subdomains[i:i+batch_size]
            print(f"正在执行第 {i//batch_size+1} 批，剩余 {total-i} 个域名")
            
            # 提交批次任务
            futures = [executor.submit(dns_query, domain, dns_ip, dns_port) for domain in batch]
            
            # 等待本批次任务提交完成
            time.sleep(1)  # 关键速率控制点

def main(wildcard_domain, dns_ip, dns_port, batch_size, total):
    # 生成子域名列表
    subdomains = generate_random_subdomains(wildcard_domain, total)
    print(f"已生成 {len(subdomains)} 个随机子域名")
    
    # 分批执行查询
    start_time = time.time()
    results = batch_executor(subdomains, dns_ip, dns_port, batch_size)
    elapsed = time.time() - start_time
    
    print(f"总耗时: {elapsed:.2f}秒")
    print(f"平均速率: {len(subdomains)/elapsed:.2f}次/秒")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python wildcardDomain.py <wildcard_domain> <dns_ip> <dns_port> <batch_size> <total>")
        print("Example: python wildcardDomain.py *.example.com 127.0.0.1 53 20 5000")
        sys.exit(1)

    wildcast_domain = sys.argv[1]
    dns_ip = sys.argv[2]
    dns_port = int(sys.argv[3])
    batch_size = int(sys.argv[4])
    total = int(sys.argv[5])

    try:
        main(wildcast_domain, dns_ip, dns_port, batch_size, total)
    except KeyboardInterrupt:
        print("stop")
        


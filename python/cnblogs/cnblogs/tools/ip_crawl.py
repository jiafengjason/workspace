import os.path
import pickle
import random
import requests
import telnetlib

from scrapy.selector import Selector

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

def judge_proxy(proxy):
    scheme = proxy.split(":")[0]
    test_urls = {
        "http": 'http://icanhazip.com/',
        "https": 'https://icanhazip.com/',
    }
    proxies = {scheme: proxy}
    print(scheme, proxy)
    print(test_urls[scheme])
    try:
        response = requests.get(test_urls[scheme], headers=headers, proxies=proxies, timeout=10)
        #response = requests.get(test_urls[scheme], headers=headers, timeout=6)
    except Exception as e:
        print(e)
        return False
    else:
        if 200 <= response.status_code < 300:
            print(response.content)
            return True
        else:
            return False

def get_ip3366_proxys():
    response = requests.get("http://www.ip3366.net/free", headers=headers)

    sel = Selector(text=response.text)
    nodes = sel.css("#list tbody tr")
    http = []
    https = []
    for node in nodes:
        items = node.css("td::text").extract()
        ip = items[0]
        port = items[1]
        scheme = items[3].lower()
        proxy = "{0}://{1}:{2}".format(scheme, ip, port)
        if scheme == "http":
            http.append(proxy)
        elif scheme == "https":
            https.append(proxy)
    proxys = {
        "http": http,
        "https": https,
    }
    pickle.dump(proxys, open("ip3366.pkl", "wb"))
    return proxys

def get_freeproxylist_proxys():
    proxys = {
        "http": [],
        "https": []
    }
    if os.path.exists("freeproxylist.pkl"):
        proxys = pickle.load(open("freeproxylist.pkl", "rb"))

    response = requests.get("http://www.freeproxylist.cc/", headers=headers)

    sel = Selector(text=response.text)
    nodes = sel.css("#proxylisttable tbody tr")
    for node in nodes:
        # ['59.110.139.131', '3128', ' CN', 'Elite', 'No', '7 mins ago']
        items = node.css("td::text").extract()
        ip = items[0]
        port = items[1]
        if items[4] == "Yes":
            scheme = "https"
            proxy = "{0}://{1}:{2}".format(scheme, ip, port)
            if detectTcp(ip, port):
                print("Add proxy:", proxy)
                if proxy not in proxys["https"]:
                    proxys["https"].append(proxy)
        elif items[4] == "No":
            scheme = "http"
            proxy = "{0}://{1}:{2}".format(scheme, ip, port)
            if detectTcp(ip, port):
                print("Add proxy:", proxy)
                if proxy not in proxys["http"]:
                    proxys["http"].append(proxy)

    pickle.dump(proxys, open("freeproxylist.pkl", "wb"))
    return proxys

def detectTcp(ip, port):
    try:
        telnetlib.Telnet(ip, port, timeout=3)
    except Exception as e:
        print(e)
        return False
    else:
        return True

def get_proxy(scheme="https"):
    if os.path.exists("freeproxylist.pkl"):
        proxys = pickle.load(open("freeproxylist.pkl", "rb"))
    else:
        proxys = get_freeproxylist_proxys()
    while True:
        if len(proxys["http"]) == 0 or len(proxys["https"]) == 0:
            proxys = get_freeproxylist_proxys()
        proxy = random.choice(proxys[scheme])
        if judge_proxy(proxy):
            print(proxy)
            return proxy
        else:
            proxys[scheme].remove(proxy)
            pickle.dump(proxys, open("freeproxylist.pkl", "wb"))

if __name__ == '__main__':
    #get_proxy("http")
    #judge_proxy("http://70.184.195.196:80")
    #get_freeproxylist_proxys()
    get_proxy("https")

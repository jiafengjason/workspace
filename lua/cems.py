# -*- coding: utf-8 -*-
import sys
import requests
#from lxml import etree
from bs4 import BeautifulSoup
import random 
from Crypto.Cipher import AES
import base64
import time
import datetime
import re
import urllib3
from hashlib import md5

import sys
import urllib

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

def pad(m):
    print(chr(16-len(m)%16))
    print(16-len(m)%16)
    return m+chr(16-len(m)%16)*(16-len(m)%16)

class Login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://192.168.100.223:8443/CEMS/welcomeAction_welcome.do?request_locale=zh_CN',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'cems.s.enlink.top:9443',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://cems.s.enlink.top:9443',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Mode': 'cors',
            'Content-Type':  'application/x-www-form-urlencoded; charset=UTF-8',
            'Sec-Fetch-Site': 'same-origin',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.login_url = 'https://192.168.100.223:8443/CEMS/welcomeAction_welcome.do?request_locale=zh_CN'
        self.post_url = 'https://192.168.100.223:8443/CEMS/welcomeAction_login.do'
        self.session = requests.Session()

    def token(self):
        response = self.session.get(self.login_url, headers=self.headers, verify=False)
        soup = BeautifulSoup(response.content,'html.parser')
        for tag in soup.find_all(attrs={"name": "randSession"}):
            return tag["value"]
        '''
        selector = etree.HTML(response.text)
        token = selector.xpath('//*[@id="new_user"]/input[2]/@value')[0]
        return token
        '''
        return None

    def login(self, account, password, ip):
        randSession = self.token()
        #randSession = "0f4947e145db432e8edb3593359f3c9c"
        if not randSession:
            print("Get randSession failed!")
            return
            
        #generate random key
        key = ""
        for i in range(16):
            key += str(random.randint(0,9))
        key = "8144329957154132"
        print(key)
        print(pad(password))
        aes = AES.new(key, AES.MODE_CBC, key)
        print(aes.encrypt(pad(password).encode('utf8')))
        password = base64.b64encode(aes.encrypt(pad(password)))
        print(password)
        code=urllib.parse.unquote("%E9%AA%8C%E8%AF%81%E7%A0%81+")
        t = time.time()
        nowTime = lambda:int(round(t * 1000))
        token1=nowTime()
        
        #计算token
        vctoken="__post.token1=" + str(token1) + "&account=" + account + "&code=" + "验证码" + "&password=" + password + "&randSession=" + randSession
        vctoken=re.sub(r'\+', ' ', vctoken)
        vctoken=re.sub(r'\s*', '', vctoken)
        #print(vctoken)
    
        m1 = md5.new()
        m1.update(vctoken.encode(encoding='utf-8'))
        post_data = {
            'randSession' : randSession,
            'account' : account,
            'password' : password,
            'code' : code,
            '__post.token1' : token1,
            '__post.token' : m1.hexdigest()
        }
        
        args = "?key=" + key + "&ip=" + ip
        #print(args)
        response = self.session.post(self.post_url + args, data=post_data, headers=self.headers, allow_redirects=False, verify=False)

        # print response body.
        #print(response.text)

        # get cookie
        #print(response.json())
        cookies = response.cookies
        for ck in cookies:
            if ck.name == 'SESSION':
                return ck.value
        return ''

def loginCems(account, password, ip):
    login = Login()
    cookie = login.login(account, password, ip)
    return cookie
    
# 输入自己的账号和密码
if __name__ == "__main__":
    account = sys.argv[1]
    password = sys.argv[2]
    ip = sys.argv[3]
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    cookie = loginCems(account, password, ip)
    print(cookie)
import requests
import random
import time
import math
import hashlib

class Youdao:
    def __init__(self):
        #请求的头部
        self.headers={
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
'Referer': 'https://fanyi.youdao.com/',
'Cookie':'OUTFOX_SEARCH_USER_ID=-819609993@10.168.11.18; _ga=GA1.2.1410148357.1570445398; _ntes_nnid=2db5463356bad40ed3983f0e1bdccefb,1590054446138; OUTFOX_SEARCH_USER_ID_NCOO=87810024.08230878; STUDY_SESS="woYrZy9CMa+FWFEaF7mWjLE7y5ihdvn+KqrilCa5zbQLYKETFIoxcephKq/jVsE8L6Yh2xOgd97YSGDeYDev3XqdZrLMoR6AQkLnHC1mf34sbk75YKbNtWXs43LboXcBZVSU5t+dJ6RG+KZDS2+Dv8h33YxjmDYrJLPBtq6dVsPKYP+x96gU5YBIdRj+bud8"; STUDY_INFO="m18301582279@163.com|-1|1137041332|1636777591747"; DICT_SESS=v2|DWVq8nDv5WQFnLPykfg40Y5PMJyn4gLRlmOfqBh4pBRTB0LqSO4wS0zMRLkMnMUA0UWhMgFnfUl0YYOLOEO4UERUmOf6BnLz5R; DICT_LOGIN=1||1636777591813; JSESSIONID=aaalkeuBI9dxZfLTXLx0x; ___rl__test__cookies=1636785753105'
}
        # 返回秒数，乘以1000转换为毫秒数
        self.lts=math.floor(time.time()*1000)
        # 要查询的词语
        self.e = input('请输入你要查询的单词:')
        # 返回一个1-10的整数转换为字符串，与上面毫秒数时间戳进行连接
        self.salt=str(int(random.random()*10))+str(self.lts)
        # 利用md5算法对以上字符串进行加密，绿色为固定字符
        self.sign=hashlib.md5(("fanyideskweb" + self.e + self.salt + "Y2FYu%TNSbMCxc3t2u^XT").encode('utf8')).hexdigest()
        #构造请求参数
        self.data= {
            'i': self.e ,
            'from': 'AUTO',
            'to': 'AUTO',
            'client': 'fanyideskweb',
            'salt': self.salt,
            'sign': self.sign,
            'lts':  self.lts,
            'bv': hashlib.md5(self.headers['User-Agent'].encode('utf8')).hexdigest(),
            'doctype': 'json',
            'version': 2.1,
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CLICKBUTTION'
        }
        self.run()
    #运行爬虫
    def run(self):
        #请求网页
        html=requests.post('https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule',
                             headers=self.headers,
                             data=self.data)
        #输出结果
        print(html.json()['translateResult'][0][0]['tgt'])

# print(Youdao('考研').run())

from tkinter import *
import tkinter

class Trans:
    #初始化
    def __init__(self):
        #初始化界面
        self.window=Tk()
        #添加标题
        self.window.title('Translate')
        #设置大小以及摆放位置
        self.window.geometry('500x500+400+300')
        #设置不允许修改窗口大小
        self.window.resizable(False,False)
        #初始化界面
        self.setup_UI()
        #显示图形
        self.show()

    #构建UI界面
    def setup_UI(self):
        #中英文问题标签
        self.ques=tkinter.Label(self.window,text='请输入中文或者英文')
        self.ques.place(x=10, y=10, width=120, height=20)
        #中英文标签放置位置
        self.entryQues = tkinter.Entry(self.window)
        self.entryQues.place(x=140, y=10, width=150, height=20)
        #中英文答案标签
        self.answ = tkinter.Label(self.window, text='翻译结果')
        self.answ.place(x=10, y=40, width=120, height=20)
        #标签绑定变量
        self.content=tkinter.StringVar(self.window,'')
        #中英文答案标签放置位置
        self.entryAnsw = tkinter.Entry(self.window,textvariable=self.content)
        self.entryAnsw.place(x=140, y=40, width=250, height=20)
        #翻译按钮
        self.buttonQuery = tkinter.Button(self.window, text='翻译',
                            command=self.buttonQueryClick)
        #按钮放置位置
        self.buttonQuery.place(x=70, y=80, width=80, height=20)


    #给按钮添加click事件
    def buttonQueryClick(self):
        #获取输入值
        self.value=self.entryQues.get().strip()
        #给文本框进行填充值
        self.content.set(Youdao(self.value).run())

    def show(self):
        #主循环
        self.window.mainloop()
if __name__ == '__main__':
    #调用程序
    Trans()
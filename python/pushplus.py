import requests

def send_wechat(msg):
    token = '06229c5635114b0292d6a136db29e096'#前边复制到那个token
    title = 'test'
    content = msg
    template = 'html'
    url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
    print(url)
    r = requests.get(url=url)
    print(r.text)

if __name__ == '__main__':
    msg = 'Life is short I use python'
    send_wechat(msg)

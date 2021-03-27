package main

import (
    "errors"
    "fmt"
    "github.com/Albert-Zhan/httpc"
    "github.com/tidwall/gjson"
)

func Send(title,msg string) error {
    client:=httpc.NewHttpClient()
    req:=httpc.NewRequest(client)
    url:=fmt.Sprintf("http://sc.ftqq.com/%s.send?text=%s&desp=%s", "SCU158650T62000825c439e9943dec882afcd51314601e0c3e70306", title, msg)
    fmt.Println(url)
    req.SetHeader("User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36")
    
    fmt.Println("正在发送通知...")
    _,body,_:=req.SetUrl(url).SetMethod("get").Send().End()
    fmt.Println(body)
    if gjson.Get(body,"errno").Int()!=0 {
        fmt.Println("微信推送失败，返回错误:"+gjson.Get(body,"errmsg").String())
        return errors.New("微信推送失败，返回错误:"+gjson.Get(body,"errmsg").String())
    }
    fmt.Println("微信推送成功")

    return nil
}

func main() {
    Send("abc", "def")
}
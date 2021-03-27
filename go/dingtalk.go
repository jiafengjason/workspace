package main

import (
    "github.com/blinkbean/dingtalk"
    "fmt"
    "regexp"
)

func Send(title, msg, at string) error {
    cli := dingtalk.InitDingTalk([]string{"c55fdf04890babaeafd7ad9593b45ca4f6f051e126dde274916f37813c4e5ab8"}, "mt")
    markdown := []string{
        "### " + title,
        "---------",
        msg,
    }

    var err error

    if at == "all" {
        err = cli.SendMarkDownMessageBySlice(title, markdown, dingtalk.WithAtAll())
    } else {
        reg := regexp.MustCompile(`(\d{11})`)
        mobiles := reg.FindAllString(at, -1)
        if len(mobiles) > 0 {
            err = cli.SendMarkDownMessageBySlice(title, markdown, dingtalk.WithAtMobiles(mobiles))
        } else {
            err = cli.SendMarkDownMessageBySlice(title, markdown)
        }
    }

    if err != nil {
        fmt.Println(err)
        return err
    }

    fmt.Println("钉钉机器人推送成功")
    return nil
}

func main() {
    Send("MT", "Success", "1377066xxxx")
    //Send("MT", "Success", "all")
}

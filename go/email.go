package main

import (
    "fmt"
    "gopkg.in/gomail.v2"
)

func Send(mailTo []string,subject,body string) error {
    m:=gomail.NewMessage()
    m.SetHeader("From", "<476828502@qq.com>")
    m.SetHeader("To", mailTo...)
    m.SetHeader("Subject",subject)
    m.SetBody("text/html",body)
    //pop3发送失败
    //d := gomail.NewDialer("pop.qq.com",995,"476828502@qq.com","jubeoyhccukvbibc")
    d := gomail.NewDialer("smtp.qq.com",465,"476828502@qq.com","bymqcakdgeocbhhi")
    fmt.Println("正在发送通知...")
    err:=d.DialAndSend(m)
    if err!=nil {
        fmt.Println("邮件发送失败，返回错误:"+err.Error())
    }else{
        fmt.Println("邮件发送成功")
    }
    return err
}

func main() {
    Send([]string{"jiafeng@enlink.cn"}, "Test", "Hello world!")
}
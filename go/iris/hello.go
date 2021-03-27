package main

import (
    "github.com/kataras/iris/v12"
    "github.com/kataras/iris/v12/middleware/logger"
    "github.com/kataras/iris/v12/middleware/recover"
)

func main() {
    app := iris.New()
    app.Use(recover.New())
    app.Use(logger.New())
    
    //输出html
    // 请求方式: GET
    // 访问地址: http://localhost:8080/welcome
    app.Handle("GET", "/welcome", func(ctx iris.Context) {
        ctx.HTML("<h1>Welcome</h1>")
    })
    //输出字符串
    // 类似于 app.Handle("GET", "/ping", [...])
    // 请求方式: GET
    // 请求地址: http://localhost:8080/ping
    app.Get("/ping", func(ctx iris.Context) {
        ctx.WriteString("pong")
    })
    //输出json
    // 请求方式: GET
    // 请求地址: http://localhost:8080/hello
    app.Get("/hello", func(ctx iris.Context) {
        ctx.JSON(iris.Map{"message": "Hello Iris!"})
    })
    
    app.Run(iris.Addr(":9090"))
    //app.Run(iris.TLS("127.0.0.1:443", "mycert.cert", "mykey.key"))
}
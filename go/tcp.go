package main

import (
    "fmt"
    "crypto/tls"
    "time"
    "net"
    "flag"
    "strings"
)


var (
    SuccessCnt int
    SuccChan = make(chan int, 10000)
    c int
    Host string
    interval  int
)

func dailSSL() {
    for {
        conf := &tls.Config{
            InsecureSkipVerify: true, //这里是跳过证书验证，因为证书签发机构的CA证书是不被认证的
        }

        conn, err := tls.Dial("tcp", Host + ":443", conf)
        if err != nil {
            fmt.Println("err :", err)
            continue
        }
        SuccChan <- 1
        conn.Close()
        //fmt.Println("Client Connect To ", conn.RemoteAddr())
        //status := conn.ConnectionState()
        //fmt.Printf("%#v\n", status)
        time.Sleep(time.Duration(interval) * time.Microsecond)
    }
}

func dailApp() {
    for {
        conn, err := net.Dial("tcp", Host + ":80")
        if err != nil {
            fmt.Println("err :", err)
            continue
        }
        SuccChan <- 1
        conn.Close()

        time.Sleep(time.Duration(interval) * time.Millisecond)
    }
}

func dailServer(conn *tls.Conn) {
    var jsonStr = []byte(`
{ "policySpaceID": "cAzX3IEBRp22bDFgWtdu", "uniqueID": "61a4762a-a900-45f5-bee4-ae1150f506b3", "request": { "username": "jiafeng", "sip": "192.168.101.62", "dip": "180.101.49.11", "dport": "443" } }\n
`)

    for {
        _, err := conn.Write(jsonStr) // 发送数据
        if err != nil {
            continue
        }

        buf := [4096]byte{}
        //buf := make([]byte, 1024)
        // 读取服务端发送的数据
        n, err := conn.Read(buf[:])
        if err != nil {
            fmt.Println("recv failed, err:", err)
            continue
        }

        if n > 0 {
            count := len(strings.Split(strings.TrimSpace(string(buf[:n])), "\n"))
            if count>1 {
                //fmt.Println(fmt.Sprintf("recv:%d buf:%s", count, string(buf[:n])))
            }
            SuccChan <- count
        }

        time.Sleep(time.Duration(interval) * time.Millisecond)
    }
}

func tunnelStat() {
    var lastSuccessCnt int
    ticker := time.NewTicker(1 * time.Second)
    for {
        select {
        case <-ticker.C:
            fmt.Println("Speed: ", SuccessCnt - lastSuccessCnt, "/s")
            lastSuccessCnt = SuccessCnt
        case count:=<-SuccChan:
            SuccessCnt = SuccessCnt + count
        }
    }
}

func main() {
    flag.IntVar(&c, "c", 0, "parallel threads")
    flag.IntVar(&interval, "i", 1000, "sleep interval")
    flag.StringVar(&Host, "d", "", "app ip")
    flag.Parse()

    conf := &tls.Config{
        InsecureSkipVerify: true, //这里是跳过证书验证，因为证书签发机构的CA证书是不被认证的
    }
    // 连接到服务端建立的tcp连接
    conn, err := tls.Dial("tcp", "192.168.100.102:10911", conf)
    // 输出当前建Dial函数的返回值类型, 属于*net.TCPConn类型
    if err != nil {
        // 连接的时候出现错误
        fmt.Println("err :", err)
        return
    }
    // 当函数返回的时候关闭连接
    defer conn.Close()

    go tunnelStat()

    for i := 0; i < c; i++ {
        //go dailApp()
        go dailServer(conn)
    }
    select {}
}
package main

import (
    "fmt"
    "crypto/tls"
	"flag"
    "github.com/google/uuid"
    "math/rand"
    "net"
    "strconv"
    "sync"
    "time"
)

var total = 0
var wg sync.WaitGroup

var (
    Count             int
	Speed             int
)

func randomString(length int) string {
    rand.Seed(time.Now().UnixNano())

    // 随机字符串中允许出现的字符集
    chars := []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")

    // 生成随机字符串
    str := make([]rune, length)
    for i := range str {
        str[i] = chars[rand.Intn(len(chars))]
    }

    return string(str)
}

func randomPort() string {
    rand.Seed(time.Now().UnixNano())

    // 生成随机 IP 地址
    port := rand.Intn(65535)

    return strconv.Itoa(port)
}

func randomIp() string {
    rand.Seed(time.Now().UnixNano())

    // 生成随机 IP 地址
    ip := net.IPv4(byte(rand.Intn(255)), byte(rand.Intn(255)), byte(rand.Intn(255)), byte(rand.Intn(255)))

    return ip.String()
}

func connectTcp(conn *tls.Conn) {
    defer wg.Done()

    id := uuid.New()
    request := fmt.Sprintf("{ \"policySpaceID\": \"cAzX3IEBRp22bDFgWtdu\", \"uniqueID\": \"%s\", \"request\": { \"sessionid\":\"%s\", \"username\": \"%s\", \"sip\": \"%s\", \"dip\": \"%s\", \"dport\": \"%s\" } }\n", id.String(), randomString(10), randomString(10), randomIp(), randomIp(), randomPort())
    //fmt.Println("request:", request)

    var jsonStr = []byte(request)

    _, err := conn.Write(jsonStr) // 发送数据
    if err != nil {
        return
    }

    buf := [2048]byte{}
    //buf := make([]byte, 1024)
    // 读取服务端发送的数据
    n, err := conn.Read(buf[:])
    if err != nil {
        fmt.Println("recv failed, err:", err)
        return
    }
    fmt.Println(fmt.Sprintf("recv:%d buf:%s", n, string(buf[:n])))
    if n>0 {
        total += 1
    }
}

func main() {
	flag.IntVar(&Count, "c", 1, "Count")
	flag.IntVar(&Speed, "s", 1, "Speed")
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

    fmt.Println("Client Connect To ", conn.RemoteAddr())
    //status := conn.ConnectionState()
    //fmt.Printf("%#v\n", status)

    interval := time.Duration(1000000/Speed)
    wg.Add(Count)
    start := time.Now()
    for i := 0; i < Count; i++ {
        go connectTcp(conn)
        time.Sleep(interval * time.Microsecond)
    }
	sendDur := time.Since(start).Seconds()
    wg.Wait()
    dur := time.Since(start).Seconds()
	fmt.Println(sendDur, "s")
    fmt.Println(dur, "s")
    fmt.Println(total, "request")
    fmt.Println(float64(total)/dur, "rps")
}
package main

import (
    "fmt"
    //"runtime"
    "unicode/utf8"
    //"log"
    //"io/ioutil" //io 工具包
    "./guacd"
    //"github.com/spf13/viper"
    //"github.com/astaxie/beego"
)

var specialBytes [16]byte

func special(b byte) bool {
    return b < utf8.RuneSelf && specialBytes[b%16]&(1<<(b/16)) != 0
}

func QuoteMeta(s string) string {
    // A byte loop is correct because all metacharacters are ASCII.
    var i int
    for i = 0; i < len(s); i++ {
        if special(s[i]) {
            break
        }
    }
    // No meta characters found, so return original string.
    if i >= len(s) {
        return s
    }

    b := make([]byte, 2*len(s)-i)
    copy(b, s[:i])
    j := i
    for ; i < len(s); i++ {
        if special(s[i]) {
            b[j] = '\\'
            j++
        }
        b[j] = s[i]
        j++
    }
    return string(b[:j])
}

/*
func getConfig() {
    viper.SetConfigName("config")
    viper.SetConfigType("yml")
    viper.AddConfigPath(".")
    viper.SetDefault("redis.port", 6381)
    err := viper.ReadInConfig()
    if err != nil {
        fmt.Println(err)
    }
    
    fmt.Println(viper.Get("server.addr"))
}
*/

func guacdTunnel() error {
    fmt.Println("guacdTunnel")
    
    configuration := guacd.NewConfiguration()

    configuration.SetParameter("width", "1024")
    configuration.SetParameter("height", "768")
    configuration.SetParameter("dpi", "96")
    configuration.SetParameter(guacd.RecordingPath, "/home/workspace/go")
    configuration.SetParameter(guacd.RecordingName, "test")
    configuration.SetParameter(guacd.CreateRecordingPath, "true")
    configuration.SetParameter(guacd.CreateIncludeKeys, "true")
    configuration.Protocol = "ssh"
    configuration.SetParameter("username", "root")
    configuration.SetParameter("password", "enlink")
    configuration.SetParameter("hostname", "168.168.168.77")
    configuration.SetParameter("port", "22")

    tunnel, err := guacd.NewTunnel("127.0.0.1:4822", configuration)
    if err != nil {
        msg := fmt.Sprintf("建立连接失败: %v", err.Error())
        fmt.Println(msg)
        return err
    }
    fmt.Println("NewTunnel")
    
    //go func() {
        for true {
            message, err := tunnel.Read()
            if err != nil {
                break
            }
            fmt.Println(string(message))
            var instruction guacd.Instruction
            instruction = instruction.Parse(string(message))
            if instruction.Opcode == "sync" {
                //connected
                fmt.Println("sync")
            } else if instruction.Opcode == "disconnect" {
                //disconnected
                fmt.Println("disconnect")
            }
        }
    //}()
    
    return nil
}

func main() {
    fmt.Println("main")
    guacdTunnel()
    //beego.Router("/web-terminal", &controllers.Terminal{})
}
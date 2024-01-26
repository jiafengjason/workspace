package main

import (
    "fmt"
    mqtt "github.com/eclipse/paho.mqtt.golang"
    logrus "github.com/sirupsen/logrus"
    "log"
    "os"
    "crypto/tls"
    "crypto/x509"
    "io/ioutil"
)

func init() {
    mqtt.ERROR = log.New(os.Stdout, "[ERROR] ", 0)
    mqtt.CRITICAL = log.New(os.Stdout, "[CRIT] ", 0)
    mqtt.WARN = log.New(os.Stdout, "[WARN]  ", 0)
    mqtt.DEBUG = log.New(os.Stdout, "[DEBUG] ", 0)
    
    // 设置日志格式为json格式
    logrus.SetFormatter(&logrus.JSONFormatter{})

    // 设置将日志输出到标准输出（默认的输出为stderr，标准错误）
    // 日志消息输出可以是任意的io.writer类型
    logrus.SetOutput(os.Stdout)

    // 设置日志级别为warn以上
    logrus.SetLevel(logrus.WarnLevel)
}

var messagePubHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
    fmt.Printf("Received message: %s from topic: %s\n", msg.Payload(), msg.Topic())
}

var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
    fmt.Println("Connected")
}

var connectLostHandler mqtt.ConnectionLostHandler = func(client mqtt.Client, err error) {
    fmt.Printf("Connect lost: %v", err)
}

func NewTlsConfig() *tls.Config {
    certpool := x509.NewCertPool()
    ca, err := ioutil.ReadFile("ca_certificate.pem")
    if err != nil {
        log.Fatalln(err.Error())
    }
    certpool.AppendCertsFromPEM(ca)
    // Import client certificate/key pair
    clientKeyPair, err := tls.LoadX509KeyPair("client_ensbrain_certificate.pem", "client_key.pem")
    if err != nil {
        panic(err)
    }
    return &tls.Config{
        RootCAs: certpool,
        ClientAuth: tls.NoClientCert,
        ClientCAs: nil,
        InsecureSkipVerify: true,
        Certificates: []tls.Certificate{clientKeyPair},
    }
}

func main() {
    //var broker = "168.168.168.96"
    var broker = "168.168.168.77"
    opts := mqtt.NewClientOptions()
    //opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, 1883))
    opts.AddBroker(fmt.Sprintf("ws://%s:%d/ws", broker, 15675))
    //nginx代理15675
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/ws", broker, 443))
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/ws", broker, 15676))
    //nginx代理15676
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/wss", broker, 443))
    tlsConfig := NewTlsConfig()
    opts.SetTLSConfig(tlsConfig)
    opts.SetClientID("ensbrain")
    opts.SetUsername("ensbrain_plus:root")
    opts.SetPassword("Enlink@123")
    opts.SetDefaultPublishHandler(messagePubHandler)
    opts.OnConnect = connectHandler
    opts.OnConnectionLost = connectLostHandler
    client := mqtt.NewClient(opts)
    if token := client.Connect(); token.Wait() && token.Error() != nil {
        fmt.Println(token.Error())
    }
    fmt.Println("connetc ok!")

    token :=client.Publish("d41d8cd98f00b204e9800998ecf8427e",0,false,"{\"ip\":\"192.168.100.8:443||192.168.100.8:443||443\"}")
    token.Wait()
    if token.Error() != nil{
        fmt.Println(token.Error())
    }
    fmt.Println("publish ok!")

    for true {
    }
    
    client.Disconnect(250)
}

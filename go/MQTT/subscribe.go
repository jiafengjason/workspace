package main

import (
    "fmt"
    mqtt "github.com/eclipse/paho.mqtt.golang"
    //logrus "github.com/sirupsen/logrus"
    "log"
    //"os"
    "crypto/tls"
    "crypto/x509"
    "io/ioutil"
    "strconv"
    "time"
)

var total = 0

/*
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
*/

func sub(client mqtt.Client) {
    //var filters = map[string]byte {"$SYS/broker/clients/connected": 0, "$SYS/broker/messages/received": 0, "d41d8cd98f00b204e9800998ecf8427e" : 0}
    
    filters := make(map[string]byte)
    filters["$SYS/broker/clients/connected"] = 0
    filters["$SYS/broker/messages/received"] = 0
    filters["d41d8cd98f00b204e9800998ecf8427e"] = 0
    
    //token := client.Subscribe("$SYS/broker/clients/connected", 0, nil)
    token := client.SubscribeMultiple(filters, nil)
    token.Wait()
    if token.Error() != nil {
        fmt.Println(fmt.Sprintf("Subscribe err: %v", token.Error()))
    }
}

var messagePubHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
    fmt.Println(fmt.Sprintf("Received message: %s from topic: %s", msg.Payload(), msg.Topic()))
}

var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
    total += 1
    fmt.Println(fmt.Sprintf("Connected, total: %d", total))
    
    sub(client)
}

var connectLostHandler mqtt.ConnectionLostHandler = func(client mqtt.Client, err error) {
    total -= 1
    fmt.Println(fmt.Sprintf("Connect lost: %v, total: %d", err, total))
}

var reconnectHandler mqtt.ReconnectHandler = func(client mqtt.Client, opts *mqtt.ClientOptions) {
    total += 1
    fmt.Println(fmt.Sprintf("Reconnect: %s, total: %d", opts.ClientID, total))
    sub(client)
    //connectMqttServer(opts.ClientID)
}

func NewTlsCertConfig() *tls.Config {
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

func NewTlsConfig() *tls.Config {
    certpool := x509.NewCertPool()
    ca, err := ioutil.ReadFile("ca_certificate.pem")
    if err != nil {
        log.Fatalln(err.Error())
    }
    certpool.AppendCertsFromPEM(ca)
    return &tls.Config{
        RootCAs: certpool,
        InsecureSkipVerify: true,
    }
}

func connectMqttServer(clientId string) {
    fmt.Println("Connecting:"+clientId)
    //var broker = "168.168.168.96"
    var broker = "168.168.168.77"
    opts := mqtt.NewClientOptions()
    //opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, 1883))
    opts.AddBroker(fmt.Sprintf("ws://%s:%d/ws", broker, 15675))
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/ws", broker, 443))
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/ws", broker, 443))
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/ws", broker, 15676))
    //opts.AddBroker(fmt.Sprintf("wss://%s:%d/wss", broker, 443))
    //tlsConfig := NewTlsConfig()
    //opts.SetTLSConfig(tlsConfig)
    opts.SetClientID(clientId)
    opts.SetUsername("ensbrain_plus:root")
    opts.SetPassword("Enlink@123")
    opts.SetKeepAlive(15 * time.Second)
    opts.SetPingTimeout(60 * time.Second)
    opts.SetAutoReconnect(true)
    opts.SetDefaultPublishHandler(messagePubHandler)
    opts.OnConnect = connectHandler
    opts.OnConnectionLost = connectLostHandler
    opts.OnReconnecting = reconnectHandler
    client := mqtt.NewClient(opts)
    if token := client.Connect(); token.Wait() && token.Error() != nil {
        fmt.Println(fmt.Sprintf("Connect err:%v", token.Error()))
        time.Sleep(100 * time.Millisecond)
        connectMqttServer(clientId)
    }
    
    //client.Disconnect(250)
}

func main() {
    for n := 1; n <= 10000; n++ {
        go connectMqttServer(strconv.Itoa(n))
    }
    
    for true {
        
    }
}

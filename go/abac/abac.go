package main

import (
    "fmt"
    "log"
    "os"
    "strings"
    "crypto/tls"
    "time"
    "net"
    "flag"
    "sync"
    "encoding/json"
    "abac/ipset"
    "abac/iptables"
)

type (
    AbacCfg struct {
        Proto           string      `json:"proto"`
        Sip      	    string      `json:"sip"`
        Sport      		string      `json:"sport"`
        Dip     	    string      `json:"dip"`
        Dport      	    string      `json:"dport"`
        Type      	    int         `json:"type"`
        Timeout  	    int         `json:"timeout"`
        Isdelete	    int         `json:"isDelete"`
    }
)

var (
    Method              string
    Server              string
    LogFilePath         string
    Timeout             int
    TcpConn             net.Conn
    TlsConn             *tls.Conn
    BlackSip            ipset.IPSet
    BlackDip            ipset.IPSet
    BlackSipDip         ipset.IPSet
    BlackDipDport       ipset.IPSet
    BlackSipDportDip    ipset.IPSet
    IptClient           *iptables.IPTables
    Lock                sync.Mutex
)

func iptablesNew() {
    log.Println("IptablesNew")
    var err error
    IptClient, err = iptables.New()
    if err != nil {
        log.Println("Iptables New failed:", err)
    }
}

func iptablesAppendUnique(tableName, chainName string, args ...string) error {
    if IptClient == nil {
        iptablesNew()
    }

    Lock.Lock()
    defer Lock.Unlock()

    log.Println("IptablesAppendUnique:", tableName, chainName, strings.Join(args, " "))
    exists, err := IptClient.Exists(tableName, chainName, args...)
    if err != nil {
        log.Println("Iptables Exists failed:", err)
        return err
    }

    if !exists {
        err = IptClient.Append(tableName, chainName, args...)
        if err != nil {
            log.Println("Iptables Append failed:", err)
            return err
        }
    }else {
        log.Println("IptablesAppendUnique: duplicate!")
    }

    return nil
}

func iptablesDelete(tableName, chainName string, args ...string) error {
    if IptClient == nil {
        iptablesNew()
    }

    Lock.Lock()
    defer Lock.Unlock()

    log.Println("IptablesDeleteIfExists:", tableName, chainName, strings.Join(args, " "))
    exists, err := IptClient.Exists(tableName, chainName, args...)
    if err != nil {
        log.Println("Iptables Exists failed:", err)
    }

    if err == nil && exists {
        err = IptClient.Delete(tableName, chainName, args...)
    }

    return err
}

func iptablesNewChain(tableName, chainName, subChainName string) error {

    if IptClient == nil {
        iptablesNew()
    }

    log.Println("IptablesNewChain:", tableName, chainName, subChainName)
    err := IptClient.NewChain(tableName, subChainName)
    if err != nil {
        log.Println("Iptables NewChain failed:", err)
    }

    err = iptablesAppendUnique(tableName, chainName, "-j", subChainName)
    if err != nil {
        log.Println("Iptables AppendUnique failed:", err)
    }

    return nil
}

func initIpset() {
    var err error
    if err = ipset.Check(); err != nil {
        log.Println("ipset.Check err:", err)
    }

    BlackSip, err = ipset.New("black_sip", ipset.HashIp, ipset.Exist(true), ipset.Counters(true), ipset.Timeout(0))
    if err!=nil {
        log.Println("ipset.New err:", err)
    }
    BlackDip, err = ipset.New("black_dip", ipset.HashIp, ipset.Exist(true), ipset.Counters(true), ipset.Timeout(0))
    if err!=nil {
        log.Println("ipset.New err:", err)
    }
    BlackSipDip, err = ipset.New("black_sip_dip", ipset.HashNetNet, ipset.Exist(true), ipset.Counters(true), ipset.Timeout(0))
    if err!=nil {
        log.Println("ipset.New err:", err)
    }
    BlackDipDport, err = ipset.New("black_dip_dport", ipset.HashIpPort, ipset.Exist(true), ipset.Counters(true), ipset.Timeout(0))
    if err!=nil {
        log.Println("ipset.New err:", err)
    }
    BlackSipDportDip, err = ipset.New("black_sip_dport_dip", ipset.HashIpPortIp, ipset.Exist(true), ipset.Counters(true), ipset.Timeout(0))
    if err!=nil {
        log.Println("ipset.New err:", err)
    }
    iptablesNewChain("filter", "FORWARD", "ABAC")
    iptablesAppendUnique("filter", "ABAC", "-m", "set", "--match-set", "black_sip", "src", "-j", "DROP")
    iptablesAppendUnique("filter", "ABAC", "-m", "set", "--match-set", "black_dip", "dst", "-j", "DROP")
    iptablesAppendUnique("filter", "ABAC", "-m", "set", "--match-set", "black_sip_dip", "src,dst", "-j", "DROP")
    iptablesAppendUnique("filter", "ABAC", "-m", "set", "--match-set", "black_dip_dport", "dst,dst", "-j", "DROP")
    iptablesAppendUnique("filter", "ABAC", "-m", "set", "--match-set", "black_sip_dport_dip", "src,dst,dst", "-j", "DROP")
}

func clearIpset() {
    iptablesDelete("filter", "ABAC", "-m", "set", "--match-set", "black_sip", "src", "-j", "DROP")
    iptablesDelete("filter", "ABAC", "-m", "set", "--match-set", "black_dip", "dst", "-j", "DROP")
    iptablesDelete("filter", "ABAC", "-m", "set", "--match-set", "black_sip_dip", "src,dst", "-j", "DROP")
    iptablesDelete("filter", "ABAC", "-m", "set", "--match-set", "black_dip_dport", "dst,dst", "-j", "DROP")
    iptablesDelete("filter", "ABAC", "-m", "set", "--match-set", "black_sip_dport_dip", "src,dst,dst", "-j", "DROP")
    err := BlackSip.Destroy()
    if err != nil {
        log.Println("err :", err)
    }
    err = BlackDip.Destroy()
    if err != nil {
        log.Println("err :", err)
    }
    err = BlackSipDip.Destroy()
    if err != nil {
        log.Println("err :", err)
    }
    err = BlackDipDport.Destroy()
    if err != nil {
        log.Println("err :", err)
    }
    err = BlackSipDportDip.Destroy()
    if err != nil {
        log.Println("err :", err)
    }
}

func ipsetUpdateEntry(set ipset.IPSet, entry string, cfg *AbacCfg) {
    if cfg.Isdelete == 0 {
        log.Println(set.Name(), ": add", entry, "timeout", cfg.Timeout)
        err := set.Add(entry, ipset.Exist(true), ipset.Timeout(time.Duration(cfg.Timeout)*time.Minute))
        if err != nil {
            log.Println("err :", err)
            return
        }
    } else {
        ok, _ := set.Test(entry)
        if ok {
            log.Println(set.Name(), ": del", entry)
            err := set.Del(entry)
            if err != nil {
                log.Println("Del err :", err)
                return
            }
        }
    }
}

func abacProcess(cfg *AbacCfg) {
    switch cfg.Type {
    case 0:
    case 1:
        ipsetUpdateEntry(BlackSip, cfg.Sip, cfg)
    case 2:
        ipsetUpdateEntry(BlackDip, cfg.Dip, cfg)
    case 3:
        ipsetUpdateEntry(BlackSipDip, cfg.Sip+","+cfg.Dip, cfg)
    case 4:
        ipsetUpdateEntry(BlackDipDport, cfg.Dip+","+cfg.Dport, cfg)
    case 5:
        ipsetUpdateEntry(BlackSipDportDip, cfg.Sip+","+cfg.Dport+","+cfg.Dip, cfg)
    }
}

func processBuf(buf string) {
    var args AbacCfg

    contents := strings.Split(strings.TrimSpace(buf), "\n")
    for _, content := range contents {
        if err := json.Unmarshal([]byte(content), &args); err != nil {
            log.Println(fmt.Sprintf("Unmarshal(%s)err: %s", content, err))
            continue
        }

        //args.Sip = "192.168.100.8"
        //args.Dip = "192.168.100.9"
        //args.Timeout = 1
        //args.Isdelete = 0
        //args.Type = 3
        abacProcess(&args)
    }
}

func tcpProcess() {
    var n int
    var err error
    var buf = make([]byte, 1000)

    c, err := net.Dial("tcp", Server)
    if err != nil {
        log.Println("err :", err)
        time.Sleep(10 * time.Second)
        return
    }

    _, err = c.Write([]byte(`{ "type": "nta" }\n`))
    if err != nil {
        log.Printf("Write  error: %s", err)
        time.Sleep(10 * time.Second)
        return
    }

    for {
        for i:=0;i<len(buf);i++{
            buf[i]=0
        }

        c.SetReadDeadline(time.Now().Add(time.Duration(Timeout) * time.Second))
        n, err = c.Read(buf)
        if err != nil {
            if nerr, ok := err.(net.Error); ok && nerr.Timeout() {
                continue
            }
            log.Printf("conn read %d bytes,  error: %s", n, err)
            time.Sleep(10 * time.Second)
            return
        }

        log.Println(fmt.Sprintf("read:%d bytes:%s", n, string(buf[:n])))

        //buf = []byte(`{"proto":"TCP","sip":"10.10.10.10","sport":"9090","dip":"20.20.20.20","dport":"8080","type":1,"timeout":0,"isDelete":0}\n`)

        processBuf(string(buf[:n]))
    }

    c.Close()
}

func tlsProcess() {
    var n int
    var err error
    var buf = make([]byte, 1000)

    conf := &tls.Config{
        InsecureSkipVerify: true,
    }
    c, err := tls.Dial("tcp", Server, conf)
    if err != nil {
        log.Println("err :", err)
        time.Sleep(10 * time.Second)
        return
    }

    _, err = c.Write([]byte(`{ "type": "nta" }\n`))
    if err != nil {
        log.Printf("Write  error: %s", err)
        time.Sleep(10 * time.Second)
        return
    }

    for {
        for i:=0;i<len(buf);i++{
            buf[i]=0
        }

        c.SetReadDeadline(time.Now().Add(time.Duration(Timeout) * time.Second))
        n, err = c.Read(buf)
        if err != nil {
            if nerr, ok := err.(net.Error); ok && nerr.Timeout() {
                continue
            }
            time.Sleep(10 * time.Second)
            log.Printf("conn read %d bytes,  error: %s", n, err)
            return
        }

        log.Println(fmt.Sprintf("read:%d bytes:%s", n, string(buf[:n])))

        //buf = []byte(`{"proto":"TCP","sip":"10.10.10.10","sport":"9090","dip":"20.20.20.20","dport":"8080","type":1,"timeout":0,"isDelete":0}\n`)

        processBuf(string(buf[:n]))
    }

    c.Close()
}

func main() {
    flag.StringVar(&Method, "m", "tls", "tcp/tls")
    flag.StringVar(&Server, "s", "192.168.100.102:10911", "host:port")
    flag.IntVar(&Timeout, "t", 5, "Timeout seconds")
    flag.StringVar(&LogFilePath, "l", "./abac.log", "log file path")
    flag.Parse()

    logFile, err := os.OpenFile(LogFilePath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
    if err != nil {
        fmt.Println("open log file failed, err:", err)
        return
    }
    log.SetOutput(logFile)

    initIpset()

    for {
        if Method == "tls" {
            tlsProcess()
        } else {
            tcpProcess()
        }
    }

    //clearIpset()
}
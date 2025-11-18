package main

import (
    "crypto/x509"
    "encoding/pem"
    "fmt"
    "io/ioutil"
    "log"

)

func parseCertificateFromFile(filename string) (*x509.Certificate, error) {
    // 读取证书文件
    data, err := ioutil.ReadFile(filename)
    if err != nil {
        return nil, err
    }

    // 解码PEM格式的证书
    block, _ := pem.Decode(data)
    if block == nil {  
        return nil, fmt.Errorf("failed to decode PEM block containing the certificate")
    }
  
    // 解析证书
    cert, err := x509.ParseCertificate(block.Bytes)
    if err != nil {
        return nil, err
    }

    return cert, nil
}

func main() {
    cert, err := parseCertificateFromFile("server.crt")
    if err != nil {
        log.Fatalf("Failed to parse certificate: %v", err)
    }
  
    // 打印证书的一些基本信息  
    fmt.Printf("Issuer: %s\n", cert.Issuer.String())
    fmt.Printf("Subject: %s\n", cert.Subject)
    fmt.Printf("SerialNumber: %s\n", fmt.Sprintf("%x", cert.SerialNumber))
    fmt.Printf("SNI: %s\n", cert.Subject.CommonName)
    fmt.Printf("NotBefore: %s\n", cert.NotBefore)
    fmt.Printf("NotAfter: %s\n", cert.NotAfter)

    // 检查SAN
    for _, name := range cert.DNSNames {
        fmt.Printf("DNS Name: %s\n", name)
    }

    // 如果有IP地址在SAN中，也可以打印出来
    for _, ip := range cert.IPAddresses {
        fmt.Printf("IP Address: %s\n", ip.String())
    }
}

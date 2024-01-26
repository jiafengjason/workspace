package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "crypto/tls"
    "bytes"
    "io/ioutil"
)

func main() {
    url := "https://192.168.100.102:10911"
    fmt.Println("URL:>", url)

    var jsonStr = []byte(`
{ "policySpaceID": "cAzX3IEBRp22bDFgWtdu", "uniqueID": "61a4762a-a900-45f5-bee4-ae1150f506b3", "request": { "username": "jiafeng", "sip": "192.168.101.62", "dip": "180.101.49.11", "dport": "443" } }
`)

    var data map[string]json.RawMessage
    err := json.Unmarshal(jsonStr, &data)
    if err != nil {
        fmt.Println(err)
    }

    tr := &http.Transport{ TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, }
    client := &http.Client{Transport: tr}
    res, err := client.Post(url, "application/json;charset=utf-8", bytes.NewBuffer(jsonStr))
    if err != nil {
        fmt.Println(err.Error())
        return
    }
    defer res.Body.Close()

    content, err := ioutil.ReadAll(res.Body)
    if err != nil {
        fmt.Println("Fatal error ", err.Error())
    }

    fmt.Println("response Status:", res.StatusCode)
    fmt.Println(string(content))

}
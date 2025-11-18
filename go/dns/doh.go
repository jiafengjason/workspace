package main

import (
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"strings"
)

func isDoHRequest(r *http.Request) bool {
	return strings.HasPrefix(r.URL.Path, "/dns-query") ||
		strings.HasPrefix(r.URL.Path, "/resolve") ||
		r.Header.Get("Content-Type") == "application/dns-message"
}

func main() {
	proxy := &httputil.ReverseProxy{
		Director: func(req *http.Request) {
			if isDoHRequest(req) {
				// 重定向到本地DoH服务器
				req.URL.Scheme = "http"
				req.URL.Host = "localhost:8080"
			} else {
				// 放行普通HTTPS流量
				req.URL.Scheme = "https"
				req.URL.Host = req.Host
			}
		},
	}

	// 监听443端口的透明代理
	ln, err := net.Listen("tcp", ":443")
	if err != nil {
		log.Fatal(err)
	}
	log.Fatal(http.Serve(ln, proxy))
}
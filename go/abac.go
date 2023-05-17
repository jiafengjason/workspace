
package main

import (
	"fmt"
	"sync"
	"net/http"
	"time"
)

var count = 10000
var total = 0

var wg sync.WaitGroup

func curl() {
	resp, err := http.Get("https://www.baidu.com/")
    defer wg.Done()
	if err != nil {
        fmt.Println(err)
		return
	}

	defer resp.Body.Close()
	if resp.StatusCode==200 {
		total += 1
	}
}

func main() {

	wg.Add(count)
	start := time.Now()

	for i := 0; i < count; i++ {
		go curl()
	}
	wg.Wait()
	dur := time.Since(start).Seconds()
	fmt.Println(dur)
	fmt.Println(float64(total)/dur)
}
package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
    "fmt"
    "log"
    "os"
    "io"
)
 
func main(){
    
    router := gin.Default()
 
    router.GET("/", func(c *gin.Context) {
        c.String(http.StatusOK, "Hello World")
    })

    //http://168.168.168.77:8000/user/rsj217
    router.GET("/user/:name", func(c *gin.Context) {
        name := c.Param("name")
        c.String(http.StatusOK, "Hello %s", name)
    })

    //http://168.168.168.77:8000/user/rsj217/中国
    router.GET("/user/:name/*action", func(c *gin.Context) {
        name := c.Param("name")
        action := c.Param("action")
        message := name + " is " + action
        c.String(http.StatusOK, message)
    })

    //http://168.168.168.77:8000/welcome?firstname=中国&lastname=天朝
    router.GET("/welcome", func(c *gin.Context) {
        firstname := c.DefaultQuery("firstname", "Guest")
        lastname := c.Query("lastname")
 
        c.String(http.StatusOK, "Hello %s %s", firstname, lastname)
    })

    //curl -X POST http://127.0.0.1:8000/form_post -H "Content-Type:application/x-www-form-urlencoded" -d "message=hello&nick=rsj217" | python -m json.tool
    router.POST("/form_post", func(c *gin.Context) {
        message := c.PostForm("message")
        nick := c.DefaultPostForm("nick", "anonymous")
 
        c.JSON(http.StatusOK, gin.H{
            "status":  gin.H{
                "status_code": http.StatusOK,
                "status":      "ok",
            },
            "message": message,
            "nick":    nick,
        })
    })

    //curl -X POST http://168.168.168.77:8000/upload -F "upload=@/root/gin.txt" -H "Content-Type: multipart/form-data"
    router.POST("/upload", func(c *gin.Context) {
        name := c.PostForm("name")
        fmt.Println(name)
        file, header, err := c.Request.FormFile("upload")
        if err != nil {
            c.String(http.StatusBadRequest, "Bad request")
            return
        }
        filename := header.Filename
 
        fmt.Println(file, err, filename)
 
        out, err := os.Create(filename)
        if err != nil {
            log.Fatal(err)
        }
        defer out.Close()
        _, err = io.Copy(out, file)
        if err != nil {
            log.Fatal(err)
        }
        c.String(http.StatusCreated, "upload successful")
    })
    
    router.Run("0.0.0.0:8000")
}


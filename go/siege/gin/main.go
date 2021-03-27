package main

import "github.com/gin-gonic/gin"

func main() {
    gin.SetMode(gin.ReleaseMode)
    r := gin.Default()
    r.GET("/", func(c *gin.Context) {
            c.JSON(200, gin.H{
            "message": "pong",
        })
    })
    r.Run(":9292")
}



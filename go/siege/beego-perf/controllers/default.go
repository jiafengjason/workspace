package controllers

import (
	"github.com/astaxie/beego"
)

type MainController struct {
	beego.Controller
}

func (c *MainController) Get() {
    c.Data["json"] = map[string]string{"ObjectId": "123"}
    c.ServeJSON()
}
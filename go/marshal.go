package main  
  
import (  
	"encoding/json"  
	"fmt"  
)  
  
type Person struct {  
	Name    string	`json:"name"`
	Age     int
	Ignored string  `json:"ignored"`
}  
  
// MarshalJSON 自定义序列化方法  
func (p Person) MarshalJSON() ([]byte, error) {  
	type Alias Person // 定义一个与Person具有相同字段的别名，但不包含MarshalJSON方法  
	// 根据条件决定是否包含Age字段  
	if p.Age == 0 {  
		return json.Marshal(struct {  
			*Alias  
		}{  
			Alias: (*Alias)(&p),  
		})  
	}
	fmt.Println(p.Age)
	return json.Marshal(struct {
		Age int `json:"AGE,omitempty"` // 仍然使用omitempty来忽略零值
	}{
		Age:   p.Age,  
	})  
}  
  
func main() {  
	// 创建一个Person实例，Age字段为零值  
	person := Person{  
		Name: "John",  
		Age:  1,
	}  
  
	// 将结构体转换成JSON  
	jsonData, err := json.Marshal(person)  
	if err != nil {  
		fmt.Println("Error:", err)  
		return  
	}  
  
	// 打印JSON结果  
	fmt.Println(string(jsonData))  
}

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn

app = FastAPI()

# 定义一个Pydantic模型来表示Webhook请求的数据结构
class Autoheal(BaseModel):
    containerName: str
    containerId: str
    success: str

@app.post("/autoHeal/webhook")
#async def webhook_endpoint(data: Any = Body(...)):
async def webhook_endpoint(autoheal: Autoheal = Body(...)):
    try:
        # 在这里处理Webhook请求的数据
        # 例如，你可以将数据存储到数据库，发送通知等
        # {'containerName': 'webterminal', 'containerId': 'd793ddd5b95d', 'success': 'true'}
        #print(data)
        print(f"Received containerName: {autoheal.containerName} containerId: {autoheal.containerId} success: {autoheal.success}")
  
        # 返回成功响应  
        return {"status": "success", "message": "Webhook received and processed"}  
    except Exception as e:
        # 如果发生异常，返回错误响应
        raise HTTPException(status_code=500, detail=str(e))
  
# 运行FastAPI应用
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)

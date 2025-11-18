import websocket
import json
import time
import datetime
import threading

class GoldWebSocketClient:
    def __init__(self):
        self.ws_url = "wss://ws.goldapi.io/ws/XAUUSD"  # 示例WebSocket地址
        self.api_key = "goldapi-5qxnjsmf4zdvg8-io"
        self.current_price = None
        
    def on_message(self, ws, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            price = data.get('price', {}).get('XAUUSD', {}).get('price')
            if price:
                self.current_price = price
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"📊 [{timestamp}] 实时价格: ${price}")
                
        except Exception as e:
            print(f"消息解析错误: {e}")

    def on_error(self, ws, error):
        """处理错误"""
        print(f"WebSocket错误: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        print("WebSocket连接关闭")

    def on_open(self, ws):
        """连接建立"""
        print("WebSocket连接建立")
        # 发送认证消息
        auth_msg = json.dumps({"api_key": self.api_key})
        ws.send(auth_msg)

    def start_monitor(self):
        """启动WebSocket监控"""
        ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws.on_open = self.on_open
        
        # 在后台线程中运行WebSocket
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ws.close()
            print("监控已停止")

# 使用示例
if __name__ == "__main__":
    client = GoldWebSocketClient()
    client.start_monitor()

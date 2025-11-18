import websocket
import json
import threading
import time
from datetime import datetime

class TwelveDataWebSocket:
    def __init__(self, api_key):
        self.api_key = api_key
        self.ws_url = f"wss://ws.twelvedata.com/v1/quotes/price?apikey={api_key}"
        self.ws = None
        self.connected = False
        
    def on_message(self, ws, message):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            print(f"📊 收到数据: {data}")
            
            # 解析黄金价格
            if data.get('event') == 'price':
                symbol = data.get('symbol')
                price = data.get('price')
                timestamp = data.get('timestamp')
                dt = datetime.fromtimestamp(timestamp)
                
                if symbol == 'XAU/USD' and price:
                    print(f"💰 {dt}[ ${price} ]")
                    
        except json.JSONDecodeError:
            print(f"❌ JSON解析错误: {message}")
        except Exception as e:
            print(f"❌ 处理消息错误: {e}")

    def on_error(self, ws, error):
        """处理错误"""
        print(f"❌ WebSocket错误: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        print("🔌 WebSocket连接关闭")
        self.connected = False

    def on_open(self, ws):
        """连接建立"""
        print("✅ WebSocket连接建立")
        self.connected = True
        
        # 订阅伦敦金价格
        subscribe_message = {
            "action": "subscribe",
            "params": {
                "symbols": "XAU/USD"
            }
        }
        ws.send(json.dumps(subscribe_message))
        print("📡 subscribe success")

    def connect(self):
        """建立WebSocket连接"""
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        
        # 在后台线程中运行
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        
        print("🔄 正在连接WebSocket...")

    def disconnect(self):
        """断开连接"""
        if self.ws:
            self.ws.close()
            print("👋 已断开WebSocket连接")

if __name__ == "__main__":
    API_KEY = "1535b2a8bed2484780fa47ee9b635540"
    
    client = TwelveDataWebSocket(API_KEY)
    client.connect()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
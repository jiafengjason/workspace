import akshare as ak
import pandas as pd
import schedule
import time
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class StockMonitor:
    def __init__(self, watch_list=None):
        self.watch_list = watch_list or ['sz002475', 'sz002389', 'sh600749']
        self.alert_threshold = 5.0
        
    def get_specific_stocks_realtime(self):
        data = None
        try:
            data = ak.stock_zh_a_spot()
        except Exception as e:
            logging.error(f"stock_zh_a_spot fail: {e}")
            try:
                data = ak.stock_zh_a_spot_em()
            except Exception as e:
                logging.error(f"stock_zh_a_spot_em fail: {e}")
                return None
            
        watched_stocks = data[data['代码'].isin(self.watch_list)]
        print(watched_stocks)
        columns = ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '最高', '最低']
        result = watched_stocks[columns].copy()
        
        # 添加时间戳
        current_time = datetime.now()
        result['更新时间'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
        result['时间戳'] = current_time
        
        return result
    
    def check_price_alert(self, data):
        """
        检查价格警报
        """
        if data is None:
            return
            
        for _, row in data.iterrows():
            change_percent = row['涨跌幅']
            if abs(change_percent) >= self.alert_threshold:
                logging.warning(
                    f"🚨 价格警报！{row['名称']}({row['代码']}) "
                    f"涨跌幅: {change_percent:.2f}%, 当前价: {row['最新价']}"
                )
    
    def save_to_database(self, data):
        if data is not None:
            filename = f"stock_data_{datetime.now().strftime('%Y%m%d')}.csv"
            header = not pd.io.common.file_exists(filename)
            data.to_csv(filename, mode='a', header=header, index=False)
    
    def display_current_status(self, data):
        if data is not None:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n📊 股票监控状态 ({current_time})")
            print("=" * 60)
            for _, row in data.iterrows():
                change_icon = "📈" if row['涨跌幅'] > 0 else "📉" if row['涨跌幅'] < 0 else "➡️"
                print(f"{change_icon} {row['名称']:6}({row['代码']}): "
                      f"{row['最新价']:7.2f}元 "
                      f"{row['涨跌幅']:7.2f}%")
            print("=" * 60)

def main():
    monitor = StockMonitor()
    
    def monitoring_job():
        logging.info("执行监控任务...")
        
        data = monitor.get_specific_stocks_realtime()
        
        if data is not None:
            monitor.check_price_alert(data)
            monitor.display_current_status(data)
            monitor.save_to_database(data)
    
    schedule.every(300).seconds.do(monitoring_job)
    
    # 只在交易时间运行 (9:30-11:30, 13:00-15:00)
    # schedule.every(30).seconds.between("09:30", "11:30").do(monitoring_job)
    # schedule.every(30).seconds.between("13:00", "15:00").do(monitoring_job)
    
    # 立即执行一次
    monitoring_job()
    
    while True:
        current_time = datetime.now().time()
        
        if ((current_time.hour == 9 and current_time.minute >= 30) or
            (current_time.hour >= 10 and current_time.hour < 11) or
            (current_time.hour == 11 and current_time.minute <= 30) or
            (current_time.hour >= 13 and current_time.hour < 18)):
            
            schedule.run_pending()
        
        time.sleep(1)

if __name__ == "__main__":
    main()
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

client = ApiClient()

# 示例：获取贵州茅台 (600519.SS) 的日K线数据，最近一个月
stock_chart_data = client.call_api('YahooFinance/get_stock_chart', query={
    'symbol': '600519.SS', 
    'region': 'CN',  # 虽然API文档中没有CN，但通常A股数据源会支持中国区域，或者此参数可能被忽略
    'interval': '1d', 
    'range': '1mo',
    'includeAdjustedClose': True
})

if stock_chart_data:
    print("贵州茅台 (600519.SS) 日K线数据 (最近一月):")
    # print(stock_chart_data) # 原始数据较多，仅打印部分关键信息或提示保存
    if stock_chart_data.get('chart', {}).get('result'):
        meta = stock_chart_data['chart']['result'][0].get('meta', {})
        print(f"  货币: {meta.get('currency')}, 股票代码: {meta.get('symbol')}, 交易所: {meta.get('exchangeName')}")
        timestamps = stock_chart_data['chart']['result'][0].get('timestamp', [])
        indicators = stock_chart_data['chart']['result'][0].get('indicators', {}).get('quote', [{}])[0]
        adjclose_list = stock_chart_data['chart']['result'][0].get('indicators', {}).get('adjclose', [{}])[0].get('adjclose', []) 
        if timestamps and indicators.get('open') and adjclose_list:
            print(f"  获取到 {len(timestamps)} 条数据点")
            print(f"  最新交易日开盘价: {indicators.get('open')[-1]}, 收盘价: {indicators.get('close')[-1]}, 最高价: {indicators.get('high')[-1]}, 最低价: {indicators.get('low')[-1]}, 成交量: {indicators.get('volume')[-1]}, 复权收盘价: {adjclose_list[-1]}")
        else:
            print("  未能获取到完整的K线数据。")
    else:
        print(f"  未能获取到K线数据，错误信息: {stock_chart_data.get('chart', {}).get('error')}")
else:
    print("调用YahooFinance/get_stock_chart API失败")

print("\n" + "-"*50 + "\n")

# 示例：获取贵州茅台 (600519.SS) 的公司洞察数据
stock_insights_data = client.call_api('YahooFinance/get_stock_insights', query={'symbol': '600519.SS'})

if stock_insights_data:
    print("贵州茅台 (600519.SS) 公司洞察数据:")
    # print(stock_insights_data) # 原始数据较多，仅打印部分关键信息或提示保存
    if stock_insights_data.get('finance', {}).get('result'):
        result = stock_insights_data['finance']['result']
        print(f"  股票代码: {result.get('symbol')}")
        if result.get('instrumentInfo', {}).get('technicalEvents', {}).get('shortTermOutlook'):
            short_term = result['instrumentInfo']['technicalEvents']['shortTermOutlook']
            print(f"  短期展望: {short_term.get('stateDescription')}, 方向: {short_term.get('direction')}")
        if result.get('companySnapshot', {}).get('company'):
            company_snapshot = result['companySnapshot']['company']
            print(f"  公司创新性: {company_snapshot.get('innovativeness')}, 可持续性: {company_snapshot.get('sustainability')}")
        if result.get('recommendation'):
            recommendation = result['recommendation']
            print(f"  机构评级: {recommendation.get('rating')}, 目标价: {recommendation.get('targetPrice')}")
        if result.get('sigDevs') and len(result.get('sigDevs')) > 0:
            print(f"  重要动态: {result.get('sigDevs')[0].get('headline')}")
    else:
        print(f"  未能获取到公司洞察数据，错误信息: {stock_insights_data.get('finance', {}).get('error')}")
else:
    print("调用YahooFinance/get_stock_insights API失败")

# 将获取的数据保存到文件，实际应用中应根据需要选择合适的格式（如CSV, JSON等）
import json
with open("/home/ubuntu/stock_chart_600519SS.json", "w", encoding='utf-8') as f:
    json.dump(stock_chart_data, f, ensure_ascii=False, indent=4)
print("\nK线数据已保存到 /home/ubuntu/stock_chart_600519SS.json")

with open("/home/ubuntu/stock_insights_600519SS.json", "w", encoding='utf-8') as f:
    json.dump(stock_insights_data, f, ensure_ascii=False, indent=4)
print("公司洞察数据已保存到 /home/ubuntu/stock_insights_600519SS.json")


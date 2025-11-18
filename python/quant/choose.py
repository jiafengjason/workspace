import time
import akshare as ak
import pandas as pd
import os
import baostock as bs
from datetime import datetime, timedelta
import numpy as np

if os.path.isfile("data.pkl"):
    stock_zh_a_spot_df = pd.read_pickle("data.pkl")
else:
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    stock_zh_a_spot_df.to_pickle(path="data.pkl")

#print(stock_zh_a_spot_df)

df_stock = stock_zh_a_spot_df[['代码','名称']][:]
anyData = {'stock':'00','name':'name_test','指标1':'var1','指标1':'var1','指标2':'var2','指标3':'var3','指标4':'var4','综合评估':'varAll'}
dfResult = pd.DataFrame(anyData,index=[0])

class Baostock:
    def __init__(self):
        self.lg = bs.login()
        print(f'login status: {self.lg.error_code} - {self.lg.error_msg}')
    
    def __del__(self):
        try:
            bs.logout()
        except (ImportError, AttributeError):
            pass
    
    def get_financial_data(self, code):
        """获取过去5年的财务数据"""
        # 构建结果数据框
        columns = ['日期', '净资产收益率(%)', '每股经营性现金流(元)', '扣除非经常性损益后的净利润(元)']
        result_df = pd.DataFrame(columns=columns)
        
        # 获取最近5年的数据
        current_year = datetime.now().year
        for year in range(current_year - 4, current_year + 1):
            # 获取年报数据(第四季度)
            profit_list = []
            rs_profit = bs.query_profit_data(code=code, year=year, quarter=4)
            while (rs_profit.error_code == '0') & rs_profit.next():
                profit_list.append(rs_profit.get_row_data())
            
            if profit_list:
                profit_df = pd.DataFrame(profit_list, columns=rs_profit.fields)
                
                # 获取现金流数据
                cash_flow_list = []
                rs_cash_flow = bs.query_cash_flow_data(code=code, year=year, quarter=4)
                while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
                    cash_flow_list.append(rs_cash_flow.get_row_data())
                
                cash_flow_df = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)
                
                # 提取需要的数据
                date_str = f"{year}-12-31"
                
                # 获取净资产收益率
                roe = profit_df['roeAvg'].values[0] if 'roeAvg' in profit_df.columns and len(profit_df) > 0 else '0'
                
                # 获取每股经营性现金流 - 使用实际存在的字段计算
                cash_flow_per_share = '0'
                # 使用CFOToNP(经营活动产生的现金流量净额/净利润)比率和净利润计算
                if 'CFOToNP' in cash_flow_df.columns and len(cash_flow_df) > 0 and 'netProfit' in profit_df.columns and 'totalShare' in profit_df.columns:
                    try:
                        # 获取现金流与净利润比率
                        cf_ratio = float(cash_flow_df['CFOToNP'].values[0]) if cash_flow_df['CFOToNP'].values[0] else 0
                        # 获取净利润(元)
                        net_profit = float(profit_df['netProfit'].values[0]) if profit_df['netProfit'].values[0] else 0
                        # 获取总股数(股)
                        total_share = float(profit_df['totalShare'].values[0]) if profit_df['totalShare'].values[0] else 0
                        
                        if total_share > 0 and net_profit > 0:
                            # 计算经营活动产生的现金流量净额 = 净利润 * 比率
                            operating_cash_flow = net_profit * cf_ratio
                            # 计算每股经营性现金流(元/股)
                            cash_flow_per_share = str(operating_cash_flow / total_share)
                    except (ValueError, TypeError):
                        cash_flow_per_share = '0'
                
                # 获取扣除非经常性损益后的净利润
                net_profit_after_non_recurring = '0'
                # 使用实际存在的netProfit字段作为替代
                if 'netProfit' in profit_df.columns and len(profit_df) > 0:
                    net_profit_after_non_recurring = profit_df['netProfit'].values[0]
                
                # 确保数据不为空字符串，设置默认值
                if cash_flow_per_share == '':
                    cash_flow_per_share = '0'
                if net_profit_after_non_recurring == '':
                    net_profit_after_non_recurring = '0'
                
                # 添加到结果数据框
                new_row = {
                    '日期': date_str,
                    '净资产收益率(%)': roe,
                    '每股经营性现金流(元)': cash_flow_per_share,
                    '扣除非经常性损益后的净利润(元)': net_profit_after_non_recurring
                }
                result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
        
        return result_df
    
    def get_pe(self, code, start_date):
        """获取指定日期范围内的平均市盈率"""
        # 查询历史K线数据，包含PE字段
        rs = bs.query_history_k_data_plus(
            code=code,
            fields="date,peTTM",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            frequency="d",
            adjustflag="3"
        )
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            # 转换PE为浮点数并过滤无效值
            df['peTTM'] = pd.to_numeric(df['peTTM'], errors='coerce')
            df = df[df['peTTM'] > 0]  # 只保留大于0的PE值
            
            if not df.empty:
                return df['peTTM'].mean()
        
        return None

if __name__ == "__main__":
    stock = Baostock()

    for row_index, row in df_stock.iterrows():
        try:
            # print(row['code'])
            # print(row['name'])
            r_code = row['代码'][2:]
            r_name = row['名称']
            
            # 转换为baostock格式的代码
            if r_code.startswith('9'):
                continue
            if r_code.startswith('0') or r_code.startswith('3'):
                bs_code = f"sz.{r_code}"
            else:
                bs_code = f"sh.{r_code}"
            
            ##指标1 - 过去5年来平均净资产收益率高于14%
            df = stock.get_financial_data(bs_code)
            df = df.set_index(df['日期'])
            #print(df.head())
            df1 = df[df.index>'2015-01-01']['净资产收益率(%)']
            df1_sum = df1.replace('--',0).astype(float).sum(axis = 0, skipna = True)
            df1_count = df1.count()
            var1 = (df1_sum / df1_count)>0.14 if df1_count > 0 else False
            
            ##指标2- 市盈率低于30 并且大于0
            day = (datetime.now() - timedelta(days=30))
            dateStart = datetime(day.year, day.month, day.day)
            pe_mean = stock.get_pe(bs_code, dateStart)
            var2 = pe_mean is not None and pe_mean > 0 and pe_mean < 30
            #print(pe_mean)
            
            #指标3：经营现金流为正,财务指标数据
            var3 = False
            if len(df) > 1:
                try:
                    cash_flow = float(df['每股经营性现金流(元)'].iloc[0])
                    var3 = cash_flow > 0
                except (ValueError, TypeError):
                    var3 = False
            
            #指标4：新期的净利润大于前5年的净利润 取万元
            var4 = False
            if len(df) > 1:
                try:
                    var4_1 = float(df['扣除非经常性损益后的净利润(元)'].iloc[0]) / 10000
                    # 获取前5年的最大值
                    max_prev_value = 0
                    for i in range(1, min(len(df), 6)):
                        try:
                            val = float(df['扣除非经常性损益后的净利润(元)'].iloc[i])
                            if val > max_prev_value:
                                max_prev_value = val
                        except (ValueError, TypeError):
                            continue
                    var4_2 = max_prev_value / 10000
                    var4 = var4_1 > var4_2
                except (ValueError, TypeError):
                    var4 = False
            
            ##综合评估
            varAll = var1 and var2 and var3 and var4
            if varAll == True:
                print(row)
            anyData = {'stock':r_code,'name':r_name,'指标1':var1,'指标1':var1,'指标2':var2,'指标3':var3,'指标4':var4,'综合评估':varAll}
            df_idex = row_index+1
            dfResult.loc[df_idex] = anyData
            print(anyData)
        except Exception as e:
            print(f"error: {e}")
            continue
            #time.sleep(7)
    # 筛选出综合评估为True的数据
    filtered_result = dfResult[dfResult['综合评估'] == True]
    # 输出筛选结果
    print("符合条件的股票:")
    print(filtered_result)
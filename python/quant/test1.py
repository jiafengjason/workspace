import akshare as ak
import yfinance as yf
import tushare as ts
import baostock as bs
import pandas as pd
import os
from datetime import datetime

ts.set_token('f34de100f0f8f4a4cf9eb5ef6473430ccdafd41320e2168d84585dd3')
pro = ts.pro_api()

def ak_get_financial_data(symbol):
    # 方法1: 尝试获取财务指标数据
    try:
        # 获取财务报表数据
        stock_financial_report_df = ak.stock_financial_report_sina(stock="000001", symbol="资产负债表")
        print("资产负债表:")
        print(stock_financial_report_df.head())
    except Exception as e:
        print(f"获取资产负债表失败: {e}")

    # 方法2: 获取主要财务指标
    try:
        stock_financial_abstract_df = ak.stock_financial_abstract(symbol="000001")
        print("\n主要财务指标:")
        print(stock_financial_abstract_df.head())
    except Exception as e:
        print(f"获取主要财务指标失败: {e}")

    # 方法3: 获取实时行情数据（包含部分估值因子）
    try:
        stock_info = ak.stock_individual_info_em(symbol="000001")
        print("\n股票基本信息:")
        print(stock_info)
    except Exception as e:
        print(f"获取股票信息失败: {e}")

def yf_get_financial_data(symbol):
    try:
        # A股格式：000001.SZ, 600000.SS
        if symbol.startswith('0') or symbol.startswith('3'):
            symbol_with_suffix = symbol + '.SZ'
        else:
            symbol_with_suffix = symbol + '.SS'
        
        stock = yf.Ticker(symbol_with_suffix)
        
        # 获取财务报表
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        print(f"{symbol} 利润表:")
        print(income_stmt.head())
        print(f"\n{symbol} 资产负债表:")
        print(balance_sheet.head())
        print(f"\n{symbol} 现金流量表:")
        print(cash_flow.head())
        
        return income_stmt, balance_sheet, cash_flow
        
    except Exception as e:
        print(f"获取 {symbol} 财务数据失败: {e}")
        return None, None, None

def ts_get_financial_data(ts_code):
    """
    使用tushare获取财务因子
    """
    try:
        # 获取财务指标数据
        fina_indicator = pro.fina_indicator(ts_code=ts_code, start_date='20250101')
        print("财务指标数据:")
        print(fina_indicator[['ann_date', 'roe', 'roa', 'net_profit_margin', 'gross_profit_margin']].head())
        
        # 获取估值数据
        daily_basic = pro.daily_basic(ts_code=ts_code, start_date='20230101')
        print("\n估值指标:")
        print(daily_basic[['trade_date', 'pe', 'pb', 'ps', 'total_mv']].head())
        
        return fina_indicator, daily_basic
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None, None

def bs_get_financial_data(code, year = None, quarter = None):
    lg = bs.login()
    print(f'登录状态: {lg.error_code} - {lg.error_msg}')
    
    if year is None:
        year = datetime.now().year
    if quarter is None:
        month = datetime.now().month
        quarter = (month - 1) // 3 - 1
    print(year, quarter)
    try:
        # 查询财务指标数据 - 使用正确的接口名称
        profit_list = []
        # 使用query_profit_data而不是query_profit_data
        rs_profit = bs.query_profit_data(code=code, year=year, quarter=quarter)
        while (rs_profit.error_code == '0') & rs_profit.next():
            profit_list.append(rs_profit.get_row_data())
        
        result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
        
        # 查询成长性数据
        growth_list = []
        rs_growth = bs.query_growth_data(code=code, year=year, quarter=quarter)
        while (rs_growth.error_code == '0') & rs_growth.next():
            growth_list.append(rs_growth.get_row_data())
        
        result_growth = pd.DataFrame(growth_list, columns=rs_growth.fields)
        
        # 查询估值数据 - 使用正确的接口
        valuation_list = []
        # 使用query_daily_data或其他可用接口
        rs_daily = bs.query_history_k_data_plus(
            code=code,
            fields="date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
            start_date=f"{year}-01-01",
            end_date=f"{year}-12-31",
            frequency="d",
            adjustflag="3"
        )
        while (rs_daily.error_code == '0') & rs_daily.next():
            valuation_list.append(rs_daily.get_row_data())
        
        result_valuation = pd.DataFrame(valuation_list, columns=rs_daily.fields)
        
        return result_profit, result_growth, result_valuation
        
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None, None, None
    finally:
        # 退出系统
        bs.logout()

def bs_get_financial_data_debug(code, year, quarter):
    """
    调试版本 - 先查看数据结构
    """
    # 登录系统
    lg = bs.login()
    print(f'登录状态: {lg.error_code} - {lg.error_msg}')
    
    try:
        # 1. 获取盈利能力数据
        print("=== 盈利能力数据 ===")
        profit_list = []
        rs_profit = bs.query_profit_data(code=code, year=year, quarter=quarter)
        print(rs_profit)
        print(f"盈利能力查询状态: {rs_profit.error_code} - {rs_profit.error_msg}")
        print(f"盈利能力字段: {rs_profit.fields}")
        
        while (rs_profit.error_code == '0') & rs_profit.next():
            profit_list.append(rs_profit.get_row_data())
        
        result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
        print("盈利能力数据:")
        print(result_profit)
        print("\n")
        
        # 2. 获取成长性数据
        print("=== 成长性数据 ===")
        growth_list = []
        rs_growth = bs.query_growth_data(code=code, year=year, quarter=quarter)
        print(f"成长性查询状态: {rs_growth.error_code} - {rs_growth.error_msg}")
        print(f"成长性字段: {rs_growth.fields}")
        
        while (rs_growth.error_code == '0') & rs_growth.next():
            growth_list.append(rs_growth.get_row_data())
        
        result_growth = pd.DataFrame(growth_list, columns=rs_growth.fields)
        print("成长性数据:")
        print(result_growth)
        print("\n")
        
        # 3. 获取运营能力数据
        print("=== 运营能力数据 ===")
        operation_list = []
        rs_operation = bs.query_operation_data(code=code, year=year, quarter=quarter)
        print(f"运营能力查询状态: {rs_operation.error_code} - {rs_operation.error_msg}")
        print(f"运营能力字段: {rs_operation.fields}")
        
        while (rs_operation.error_code == '0') & rs_operation.next():
            operation_list.append(rs_operation.get_row_data())
        
        result_operation = pd.DataFrame(operation_list, columns=rs_operation.fields)
        print("运营能力数据:")
        print(result_operation)
        print("\n")
        
        # 4. 获取偿债能力数据
        print("=== 偿债能力数据 ===")
        balance_list = []
        rs_balance = bs.query_balance_data(code=code, year=year, quarter=quarter)
        print(f"偿债能力查询状态: {rs_balance.error_code} - {rs_balance.error_msg}")
        print(f"偿债能力字段: {rs_balance.fields}")
        
        while (rs_balance.error_code == '0') & rs_balance.next():
            balance_list.append(rs_balance.get_row_data())
        
        result_balance = pd.DataFrame(balance_list, columns=rs_balance.fields)
        print("偿债能力数据:")
        print(result_balance)
        print("\n")
        
        # 5. 获取现金流数据
        print("=== 现金流数据 ===")
        cash_flow_list = []
        rs_cash_flow = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
        print(f"现金流查询状态: {rs_cash_flow.error_code} - {rs_cash_flow.error_msg}")
        print(f"现金流字段: {rs_cash_flow.fields}")
        
        while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
            cash_flow_list.append(rs_cash_flow.get_row_data())
        
        result_cash_flow = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)
        print("现金流数据:")
        print(result_cash_flow)
        print("\n")
        
        return result_profit, result_growth, result_operation, result_balance, result_cash_flow
        
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None, None, None, None, None
    finally:
        # 退出系统
        bs.logout()

if __name__ == "__main__":
    profit, growth, valuation = bs_get_financial_data("sz.000001")
    #profit, growth, operation, balance, cash_flow = bs_get_financial_data_debug("sz.000001", 2025, 2)
    
    print("盈利能力指标:")
    print(profit[['code', 'statDate', 'roeAvg', 'npMargin', 'gpMargin']])
    
    print("\n成长性指标:")
    print(growth[['code', 'statDate', 'YOYEquity', 'YOYAsset', 'YOYNI', 'YOYEPSBasic']])

import baostock as bs
import pandas as pd

def calculate_avg_roe_baostock(stock_code, years=5):
    """
    使用Baostock计算平均ROE
    """
    # 登录系统
    lg = bs.login()
    
    try:
        # 查询盈利能力数据
        end_year = pd.Timestamp.now().year
        start_year = end_year - years
        
        all_roe_data = []
        
        for year in range(start_year, end_year + 1):
            for quarter in [1, 2, 3, 4]:
                rs_profit = bs.query_profit_data(code=stock_code, year=year, quarter=quarter)
                
                profit_list = []
                while (rs_profit.error_code == '0') & rs_profit.next():
                    profit_list.append(rs_profit.get_row_data())
                
                if profit_list:
                    profit_df = pd.DataFrame(profit_list, columns=rs_profit.fields)
                    # 查找ROE字段
                    if 'roeAvg' in profit_df.columns:
                        try:
                            roe_value = float(profit_df.iloc[0]['roeAvg'])
                            all_roe_data.append({
                                'year': year,
                                'quarter': quarter,
                                'roe': roe_value
                            })
                        except (ValueError, TypeError):
                            continue
        
        if not all_roe_data:
            print("未找到ROE数据")
            return None
        
        # 转换为DataFrame
        roe_df = pd.DataFrame(all_roe_data)
        
        # 计算年度平均ROE
        annual_roe = roe_df.groupby('year')['roe'].mean().sort_index(ascending=False).head(years)
        
        if len(annual_roe) < 3:
            print(f"数据不足，只有 {len(annual_roe)} 年数据")
            return None
        
        avg_roe = annual_roe.mean()
        
        print(f"股票 {stock_code} 过去{len(annual_roe)}年平均ROE: {avg_roe:.2f}%")
        for year, roe in annual_roe.items():
            print(f"  {year}年: {roe:.2f}%")
        
        return avg_roe
        
    except Exception as e:
        print(f"计算ROE时出错: {e}")
        return None
    finally:
        # 退出系统
        bs.logout()

# 使用示例
calculate_avg_roe_baostock("sz.000001")

#！/usr/bin/envpython
# -*-coding:utf-8 -*-
# Date: 19/04/2020


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts


'''学习链接
Python金融量化分析
https://www.bilibili.com/video/BV1i741147LS?p=41
'''
# 简单的股票数据分析
def tushare_basic():
    '''
    任务：股票数据分析
    1 获取某股票的历史行情数据
    2 输出该股票所有收盘比开盘上涨3%的日期
    3 输出该股票所有开盘比前日收盘跌幅超过2%的日期
    4 假如从2010-01-01开始，每月第一个交易日买入一手(100股为一手)股票，每年最后一个交易日卖出，到今天为止，我的收益如何
    :return:
    '''
    # # 1 获取某股票的历史行情数据
    # df = ts.get_k_data('600519', start='1988-01-01')  # 茅台
    # # print(df)
    # df.to_csv('./stock_data/600519.csv')
    # 把 date列设置为索引
    df_maotai = pd.read_csv('practice1/600519.csv', index_col='date', parse_dates=['date'])[['open', 'close', 'high', 'low']]
    # print(df_maotai)

    # 2 输出该股票所有收盘比开盘上涨3%的日期
    rise_ratio = (df_maotai['close'] - df_maotai['open']) / df_maotai['open']  # 每个上涨的条件
    df_rise3_date = df_maotai[rise_ratio >= 0.03].index  # 输出上涨>3%的日期
    # print(df_rise3_date)
    # 3 输出该股票所有开盘比前日收盘跌幅超过2%的日期
    decrease_ratio = (df_maotai['open'] - df_maotai['close'].shift(1)) / df_maotai['close'].shift(1)   # 今日开盘与前日收盘
    dr_decrease2_date = df_maotai[decrease_ratio <= -0.02].index
    # print(dr_decrease2_date)

    # 4 假如从2010-01-01开始，每月第一个交易日买入一手股票，每年最后一个交易日卖出，到今天为止，我的收益如何
    df_new = df_maotai['2001-09': '2017-11']  # 剔除首尾无用的数据
    # df_new.resample('M').first()  # 按月来统计,以第一天显示
    # df_new2 = df_new.resample('M').last()  # 按月来统计,以最后一天显示
    df_monthly = df_new.resample('M').first()
    # print(df_monthly)
    df_yearly = df_new.resample('A').last()[: -1]  # 按年来统计,以最后一天显示, 并剔掉最后一个
    # print(df_yearly)
    cost_money = 0  # 花的钱
    hold = 0  # 股票持有量
    price_last = df_new['open'][-1]  # 最后一天的开盘价
    for year in range(2001, 2018):
        cost_money += df_monthly[str(year)]['open'].sum() * 100  # += 每年的每个月初花的钱的总和
        hold += len(df_monthly[str(year)]['open']) * 100
        if year != 2017:
            cost_money -= df_yearly[str(year)]['open'][0] * hold  # 每年年底清仓
            hold = 0
        # print(cost_money)  # 计算每年花的钱 负数代表赚了
    cost_money -= hold * price_last
    print(-cost_money)  # 加负号，则结果为正 -> 代表赚了

    return None


# 双均线分析
def k_xian_index():
    '''
    查找历史金叉死叉日期
    均线：每个交易日前N天的移动平均值连成的线就叫N日移动平均线
    日均线指标： 5，10天
    季均线指标：30， 60天
    年均线指标：120， 240天
    金叉：短期均线上穿长期均线 -> 买入信号
    死叉：短期均线下穿长期均线 -> 卖出信号

    任务：
    1 获取某股票的历史行情数据
    2 计算历史数据的5日均线和30日均线
    3 可视化历史数据的收盘价和两条均线
    4 分析输出所有的金叉和死叉日期
    5 假如从2010-01-01开始初始资金10万，金叉尽量买入，死叉全部卖出，到今天为止的炒股收益率如何
    :return:
    '''
    # 1 获取某股票的历史行情数据
    # df = ts.get_k_data('002069', start='2000-01-01')  # 茅台
    # # print(df)
    # df.to_csv('./stock_data/002069.csv')
    # 1 获取好的数据保存下来，方便读取操作
    df = pd.read_csv('practice1/002069.csv', index_col='date', parse_dates=['date'])[['open', 'close', 'high', 'low']]
    # print(df)

    # 2 计算历史数据的5日均线和30日均线
    # 2.1 方法一：相当于先创建两个空的列
    # df['ma5'] = np.nan
    # df['ma30'] = np.nan
    # # print(df)
    # for i in range(4, len(df)):
    #     df.loc[df.index[i], 'ma5'] = df['close'][i-4: i+1].mean()  # 指定你行列索引的某个值等于什么
    # for j in range(29, len(df)):
    #     df.loc[df.index[j], 'ma30'] = df['close'][j-29: j+1].mean()  # 指定你行列索引的某个值等于什么
    # print(df[20:40])
    # 2.2 方法2 使用  rolling方法，往回滚一定行的数据
    df['ma5'] = df['open'].rolling(5).mean()
    df['ma30'] = df['open'].rolling(30).mean()
    # print(df[20:40])

    # 3 可视化历史数据的收盘价和两条均线
    # df_temp = df[:200]
    # df_temp[['close', 'ma5', 'ma30']].plot()
    # plt.show()

    # 4 分析输出所有的金叉和死叉日期
    df = df.dropna()
    df = df['2010-01-01':]  # 从2010 年开始
    # 4.1 方法1：for循环
    # golden_cross = []
    # death_cross = []
    # for i in range(1, len(df)):
    #     if (df['ma5'][i-1] < df['ma30'][i-1]) and (df['ma5'][i] >= df['ma30'][i]):  # 短线从低走高，上穿长线 -> 金叉
    #         golden_cross.append(df.index[i].to_pydatetime())  # 获取到金叉的日期
    #     if (df['ma5'][i-1] > df['ma30'][i-1]) and (df['ma5'][i] <= df['ma30'][i]):  # 短线从高走低，下穿长线 -> 死叉
    #         death_cross.append(df.index[i].to_pydatetime())  # 获取到死叉的日期
    # print('金叉日期如下：%s\n死叉日期如下：%s' % (golden_cross, death_cross))
    # 4.2 方法2 使用true, false索引
    sr1 = df['ma5'] < df['ma30']
    sr2 = df['ma5'] >= df['ma30']
    golden_cross = df[ -(sr1 | sr2.shift(1))].index
    death_cros = df[sr1 & sr2.shift(1)].index  # 按位与
    # print("金叉日期", golden_cross)
    # print('死叉日期', death_cross)

    # 5 假如从2010-01-01开始初始资金10万，金叉尽量买入，死叉全部卖出，到今天为止的炒股收益率如何
    initial_money = 100000
    money = initial_money
    hold_amount = 0  # 持有股票数
    sr1 = pd.Series(1, index=golden_cross)
    sr2 = pd.Series(0, index=death_cros)
    # sr = sr1.add(sr2, fill_value=0)  # 合并金叉和死叉日期到一个series中，因为索引日期完全不同，所以1 和0 即可分辨开两种不同的日期
    sr = sr1.append(sr2).sort_index()
    # print(sr)
    for i in range(len(sr)):
        price_open = df['open'][sr.index[i]]
        if sr.iloc[i] == 1:  # 金叉
            buy_amount = (money // (100 * price_open))
            hold_amount += buy_amount * 100
            money -= buy_amount * 100 * price_open
        else:  # 死叉
            money += hold_amount * price_open
            hold_amount = 0
    price_end = df['open'][-1]
    money_now = hold_amount * price_end + money
    print("赚的钱数为:%.2f" % (money_now-initial_money))

    return None






if __name__=='__main__':
    # tushare_basic()
    k_xian_index()
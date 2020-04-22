import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts


'''对某一只股票数据的分析
'''
def get_basic_data(security):
    '''固定交易策略
    1 获取某股票的历史行情数据
    2 输出该股票所有收盘比开盘上涨3%的日期
    3 输出该股票所有开盘比前日收盘跌幅超过2%的日期
    4 假如从2012-01-01开始，每月第一个交易日买入一手(100股为一手)股票，每年最后一个交易日卖出，到今天为止，我的收益如何
    :param security: 股票代码
    :return:
    '''
    # # 1 获取某股票的历史行情数据
    # df = ts.get_k_data(security, start='2010-01-01')
    # # 1.1 以该股票代码命名，保存在股票数据文件夹下
    # df.to_csv('./stock_datas/'+ security + '.csv')
    # 1.2 获取完成后，选择打开文件，方便后续操作 -> 设置索引，并指定选取特定的几列内容
    df = pd.read_csv(('./stock_datas/'+ security +'.csv'), index_col='date', parse_dates=['date'])[['open', 'close', 'high', 'low']]
    # print(df.head())
    # 2 输出该股票所有收盘比开盘上涨3%的日期
    # 2.1 先确定上涨的条件，
    rise_ratio = (df['close'] - df['open']) / df['open']
    # 2.2 使用布尔型条件判断来获得内容，再获得相应的索引
    df_rise3_date = df[rise_ratio >= 0.03].index
    # print(df_rise3_date)
    # 3 输出该股票所有开盘比前日收盘跌幅超过2%的日期
    # 3.1 获取前日收盘价，需要把数组整体下移一行，即可把今日的open和昨日close放到一行中计算
    decrease_ratio = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
    df_dfcrease2_date = df[decrease_ratio <= -0.02].index
    # print(df_dfcrease2_date)

    # 4 假如从2025-01-01开始，每月第一个交易日买入一手(100股为一手)股票，每年最后一个交易日卖出，到今天为止，我的收益如何
    # 4.1 剔除首尾无用的数据
    df_new = df['2012-01-01': '2020-01-01']
    # 4.2 按月来统计,以第一天来显示整个月的股价情况
    df_monthly = df_new.resample('M').first()
    # 4.3 按年来统计,以最后一天显示全年的股价情况, 并剔掉最后一个
    df_yearly = df_new.resample('A').last()[: -1]
    # 4.4 进行买卖操作
    money_cost = 0  # 花的钱
    stock_holds = 0  # 股票持有量
    price_last = df_new['open'][-1]  # 最后一个交易日的开盘价
    for year in range(2012, 2020):
        # 4.4.1 str(year) 索引是为了获取到 date索引中含有 year 的月份，并获取到开盘价，并组成一个list列表
        year_month_list = df_monthly[str(year)]['open']
        # 4.4.2 一年内花的钱是每个月花的钱的总和，乘以100是因为每次最少买100股
        money_cost += year_month_list.sum() * 100
        stock_holds += len(year_month_list) * 100
        if year != 2019:
            # 4.4.3 每年年底清仓
            money_cost -= df_yearly[str(year)]['open'][0] * stock_holds
            stock_holds = 0
    money_cost -= stock_holds * price_last
    print('从2012-01-01开始，每月第一个交易日买入一手(100股为一手)股票，每年最后一个交易日卖出，到今天为止，我的收益为：%.2f' % (-money_cost))


def double_ma_strategies(security):
    ''' 双均线策略（短期操作）
     任务：
    1 获取某股票的历史行情数据
    2 计算历史数据的5日均线和30日均线
    3 可视化历史数据的收盘价和两条均线
    4 分析输出所有的金叉和死叉日期：(金叉：短期均线上穿长期均线 -> 买入信号) \（死叉：短期均线下穿长期均线 -> 卖出信号）
    5 假如从2016-01-01开始初始资金50万，金叉尽量买入，死叉全部卖出，到今天为止的炒股收益率如何
    :param security: 股票代码
    :return:
    '''
    # 1 获取某股票的历史行情数据
    df = pd.read_csv(('./stock_datas/'+ security +'.csv'), index_col='date', parse_dates=['date'])[['open', 'close', 'high', 'low']]
    # 2 计算历史数据的5日均线和30日均线: -> 使用  rolling方法，往回滚一定行的数据
    df['ma5'] = df['open'].rolling(5).mean()
    df['ma30'] = df['open'].rolling(30).mean()
    # 3 可视化历史数据的收盘价和两条均线
    # df_newest = df[-200: ]
    # df_newest[['close', 'ma5', 'ma30']].plot()
    # plt.show()

    # 4 分析输出所有的金叉和死叉日期
    # 4.1 节选16年以后的数据，剔掉缺失值，
    df = df['2016-01-01': ].dropna()
    # 4.2 使用条件判断索引
    choice1 = df['ma5'] < df['ma30']
    choice2 = df['ma5'] >= df['ma30']
    # 4.2.2 使用shift操作，数据下移一行
    # 4.3.1 金叉日期：前一交易日：5均线值小，后一交易日 5均线值大
    golden_cross_date = df[-(choice1 | choice2.shift(1))].index
    # 4.3.2 死叉日期：前一交易日：5均线值大，后一交易日 5均线值小
    dead_cross_date = df[choice1 & choice2.shift(1)].index
    # print("金叉日期", golden_cross_date)
    # print('死叉日期', dead_cross_date)

    # 5 假如从2016-01-01开始初始资金50万，金叉尽量买入，死叉全部卖出，到今天为止的炒股收益率如何
    initial_money = 500000
    current_money = initial_money
    stock_holds = 0
    # 5.1 设置两个序列，并给定0 ，1 值来填充
    sr1 = pd.Series(1, index=golden_cross_date)
    sr2 = pd.Series(0, index=dead_cross_date)
    # 5.2 两个数据列完全不同，因此append不会相加，再排序，即可把两个序列放成一个0，1值序列
    new_sr = sr1.append(sr2).sort_index()
    for i in range(len(new_sr)):
        price_open = df['open'][new_sr.index[i]]
        # 5.3 金叉:尽量买入
        if new_sr.iloc[i] == 1:
            to_buy = (current_money // (100 * price_open)) * 100
            stock_holds += to_buy
            current_money -= to_buy * price_open
        # 5.4 死叉: 全部卖出
        if new_sr.iloc[i] == 0:
            current_money += stock_holds * price_open
            stock_holds = 0
    price_end = df['open'][-1]
    money_earned = stock_holds * price_end + current_money - initial_money
    print('从2016-01-01开始初始资金50万，金叉尽量买入，死叉全部卖出，到今天为止的炒股收益为: %.2f' % money_earned)


if __name__ =='__main__':
    # get_basic_data(security='002069')
    double_ma_strategies(security='002069')


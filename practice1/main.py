import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
import dateutil, datetime

CASH = 500000
START_DATE = '2019-09-10'
END_DATE = '2019-12-31'



# trade_cal = ts.trade_cal()
# # print(trade_cal)
# trade_cal.to_csv('trade_cal.csv')

trade_cal = pd.read_csv('trade_cal.csv')

# 上下文信息的存储
class Context:
    def __init__(self, cash, start_date, end_date):
        self.cash = cash
        self.start_date = start_date
        self.end_date = end_date
        self.positions = {}  # 持仓信息
        self.benchmark = None  # 参考基准
        # 获取交易日范围 ->使用布尔型索引,
        # 再对dataframe形式取某一列的值 -> 即可得到一个列表
        self.date_range = trade_cal[(trade_cal['isOpen'] == 1)&(trade_cal['calendarDate'] >= start_date)\
                                    &(trade_cal['calendarDate'] <= end_date)]['calendarDate'].values
        # self.dt = dateutil.parser.parse(start_date)  # TODO start_date后一个交易日
        self.dt = None

context = Context(cash=CASH, start_date=START_DATE, end_date=END_DATE)
# print(context.date_range)

class G:
    pass

g = G()

def set_benchmark(security):  # 只支持一只股票作为基准
    context.benchmark = security


# 获取历史数据
def attribute_history(security, count, fields=('open', 'close', 'high', 'low', 'volume')):
    '''

    :param security: 股票代码
    :param count: 统计前N日的数据
    :param fields: 想要的列
    :return:
    '''
    end_date = (context.dt - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = trade_cal[(trade_cal['isOpen'] == 1) & (trade_cal['calendarDate'] <= end_date)][-count:].iloc[0, :]['calendarDate']
    # print(start_date, end_date)
    return attribute_daterange_history(security, start_date, end_date, fields)

# attribute_history('601318', 10)

def attribute_daterange_history(security, start_date, end_date, fields=('open', 'close', 'high', 'low', 'volume')):
    try:
        f = open(security+'.csv', 'r')
        df = pd.read_csv(f, index_col='date', parse_dates=['date']).loc[start_date: end_date, :]
    except FileNotFoundError:
        df = ts.get_k_data(security, start_date, end_date)

    return df[list(fields)]


# 获取股票的今日数据
def get_today_data(security):
    today = context.dt.strftime('%Y-%m-%d')
    try:
        f = open(security + '.csv', 'r')
        data = pd.read_csv(f, index_col='date', parse_dates=['date']).loc[today, :]
    except FileNotFoundError:
        data = ts.get_k_data(security, today, today).iloc[0, :]
    except KeyError:  # 说明此股票在当前交易日不正常，比如 涨跌停牌、出问题被暂停交易之类的
        data = pd.Series()
    return data


def _order(today_data, security, amount):
    p = today_data['close']
    if len(today_data) == 0:
        print('今日停牌')
        return
    if context.cash - amount * p < 0:
        amount = int(context.cash / p)
        print('现金不足，已调整为 %d' % amount)
    if amount % 100 != 0:
        if amount != -context.positions.get(security, 0):  # 如果金额不等于持有股票数量
            amount = int(amount / 100) * 100
            print('不是100的整数倍，已调整为%d' % amount)
    # 300   -(-400)
    if context.positions.get(security, 0) < - amount:
        amount = -context.positions.get(security, 0)  # 全仓卖出
        print('卖出股票不能超过持仓数，已调整为%d' % amount)

    context.positions[security] = context.positions.get(security, 0) + amount
    context.cash -= amount * p  # 更新我的钱
    if context.positions[security] == 0:
        del context.positions[security]


def order(security, amount):
    today_data = get_today_data(security)
    _order(today_data, security, amount)

def order_target(security, amount):
    if amount <0:
        print('卖出数量不能为负，已调整为0')
        amount = 0
    today_data = get_today_data(security)
    hold_amount = context.positions.get(security, 0)  # TODO: T+ 1 closeable, total
    delta_amount = amount - hold_amount
    _order(today_data, security, delta_amount)

def order_value(security, value):
    today_data = get_today_data(security)
    amount = int(value / today_data['open'])
    _order(today_data, security, amount)

def order_target_value(security, value):
    today_data = get_today_data(security)
    if value < 0:
        print('价值不能为负，调整为0')
        value = 0
    hold_value = context.positions.get(security, 0) * today_data['open']
    delta_value = value - hold_value
    order_value(security, delta_value)

def run():
    plt_df = pd.DataFrame(index=pd.to_datetime(context.date_range), columns=['value'])
    init_value = context.cash
    initialize(context)
    last_price = {}
    for dt in context.date_range:
        context.dt = dateutil.parser.parse(dt)
        handle_data(context)
        value = context.cash
        for stock in context.positions:
            # 考虑停牌的情况
            today_data = get_today_data(stock)
            if len(today_data) == 0:
                p =last_price[stock]
            else:
                p = today_data['open']
                last_price[stock] = p
            value += p * context.positions[stock]
        plt_df.loc[dt, 'value'] = value
    plt_df['ratio'] = (plt_df['value'] - init_value) / init_value
    # print(plt_df['ratio'])
    bm_df = attribute_daterange_history(context.benchmark, context.start_date, context.end_date)
    bm_init = bm_df['open'][0]
    plt_df['benchmark_ratio'] = (bm_df['open'] - bm_init) / bm_init
    # print(plt_df)
    plt_df[['ratio', 'benchmark_ratio']].plot()
    plt.show()


def initialize(context):
    set_benchmark('002069')
    g.p1 = 5
    g.p2 = 60
    g.security = '002069'

def handle_data(context):
    hist = attribute_history(g.security, g.p2)
    ma5 = hist['close'][-5: ].mean()
    ma60 = hist['close'].mean()
    if ma5 > ma60 and g.security not in context.positions:
        order_value(g.security, context.cash)
    elif ma5 < ma60 and g.security in context.positions:
        order_target(g.security, 0)




if __name__=='__main__':
    # print(attribute_daterange_history('600519', '2018-01-01', '2019-12-31'))
    # print(get_today_data('002069'))
    # _order(get_today_data('600519'), '600519', 3070)
    # print(context.positions )
    # order_target('600519', 520)
    # order_value('002069', 30000)
    # print(context.positions)
    run()
"""
Created by x2h1z on 2021/2/25.
"""
import pandas as pd
import os

from typing import Union
from datetime import datetime, timedelta
from glob import glob
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

NAMES = ["BeginTime", "EndTime", "OpenPrice", "HighPrice", "LowPrice", "ClosePrice", "ThisVolume", "ThisTurnover",
         "PreClose", "UpLimit", "DropLimit", "Volume", "Turnover"]

# 资源数据路径
source_path = "/Users/x2h1z/Data/SZ"


class A:

    def __init__(self):
        self._buy_time = ...
        self._b_T = ...
        self._sell_time = ...
        self._s_T = ...

        self._top_limit = ...

        self._encoding = ...

        self._top: dict = {}

    def _c(self, filepath, date):
        symbol_code = os.path.split(filepath)[1].split('.')[0]
        df = pd.read_csv(filepath, encoding=self._encoding, names=NAMES, index_col=False)
        # self.condition(symbol_code, date, df)
        if self.condition(symbol_code, date, df):
            self._top[symbol_code] = df

    def init(self, buy_time: int, buy_time_end: int, sell_time: int, sell_time_end: int, encoding: str = "utf-8"):
        """
        初始化参数配置

        :param buy_time:买入时间
        :param buy_time_end:买入结束时长(秒)
        :param sell_time:卖出时间
        :param sell_time_end:卖出结束时长(秒)
        :param encoding:文件的编码格式. 作用于程序的所有读取和写入
        :return:
        """
        self._buy_time = buy_time
        self._b_T = buy_time_end
        self._sell_time = sell_time
        self._s_T = sell_time_end
        self._encoding = encoding

    @staticmethod
    def _calc_average_price(df: pd.DataFrame) -> float:
        turnover = df['Turnover'].iloc[-1] - df['Turnover'].iloc[0]
        volume = df['Volume'].iloc[-1] - df['Volume'].iloc[0]
        average_price = turnover / volume
        return average_price

    def _rate_of_return_calc(self, date: str):
        """计算收益率"""
        average_weight = 1 / len(self._top)

        for symbol_code, df in self._top.items():
            buy_time_end = datetime.strptime(str(self._buy_time), "%H%M%S") + timedelta(seconds=self._b_T)
            buy_time_end = int(buy_time_end.strftime("%H%M%S"))
            b_interval_df = df[(df['EndTime'] >= self._buy_time) & (df['EndTime'] <= buy_time_end)]
            buy_price = self._calc_average_price(b_interval_df)

            next_date = self.get_next_day(date).strftime("%Y%m%d")
            files = glob(os.path.join(source_path, next_date, f"{symbol_code}*"))
            if len(files) <= 0:
                print(f"找不到下一个交易日. date:{date}, next_date:{next_date}, symbol_code:{symbol_code}")
                continue

            s_df = pd.read_csv(files[0], encoding=self._encoding, names=NAMES, index_col=False)
            sell_time_end = datetime.strptime(str(self._sell_time), "%H%M%S") + timedelta(seconds=self._s_T)
            sell_time_end = int(sell_time_end.strftime("%H%M%S"))
            s_interval_df = s_df[
                (s_df['EndTime'] >= self._sell_time) & (s_df['EndTime'] <= sell_time_end)]
            sell_price = self._calc_average_price(s_interval_df)

            #
            pnl = (sell_price - buy_price) / buy_price
            s = round(average_weight * pnl * 100, 3)
            print(f"symbol:{symbol_code}, date:{date}, 个股收益率:{s}%")

    @staticmethod
    def get_next_day(date: Union[str, datetime]) -> datetime:
        """
        获取下一个交易日

        :param date: 日期
        :return: 下一个交易日的datetime对象
        """
        global dt
        if isinstance(date, str):
            dt = datetime.strptime(date, '%Y%m%d')
        while True:
            dt = dt + timedelta(days=1)
            # 过滤掉周末
            if dt.weekday() < 5:
                break
        return dt

    def start(self, date: str = "*"):
        """
        启动回测

        :param date: 回测日期. 默认目录下所有日期
        :return:
        """
        path = os.path.join(source_path, date)
        if date == '*':
            date_paths = glob(path)
        else:
            date_paths = [path]

        for date_path in date_paths:
            # clean cache
            self._top.clear()

            for filepath in glob(os.path.join(date_path, '*')):
                self._c(filepath, date)

            # wait for result
            symbol_codes = [str(i) for i in self.day_result()]
            self._top = {code: self._top[code] for code in symbol_codes}

            self._rate_of_return_calc(date)

    def day_result(self) -> list:
        """
        当遍历完一天的个股时会调用这个函数
        :return: 选择的股票代码list
        """
        pass

    def condition(self, symbol_code: str, date: str, stock_df: pd.DataFrame) -> bool:
        """
        some desc...

        :param symbol_code: 当前股票代码
        :param date: 当前日期
        :param stock_df: 数据DataFrame对象
        :return:
        """
        pass


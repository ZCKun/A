"""
Created by x2h1z on 2021/2/25.
"""
import pandas as pd
import os

from enum import Enum
from typing import Union
from datetime import datetime, timedelta
from glob import glob
from concurrent.futures import ThreadPoolExecutor


class Market(Enum):
    SH = 0
    SZ = 1


class A:
    """ A Backtesting Framework

    通常你只需要继承 :class:`A` 然后实现它的两个方法即可, Simple Example::

        class Demo(A):
            def __init__(self):
                self.date = datetime.today()
                # 设置回测所用到的数据所在路径
                self.set_source_path("<source/path>")
                # 设置买入时段和卖出时段
                self.init(143000, 30 * 60, 93000, 30 * 60)

            def on_day_stock(self, symbol_code: str, date: str, stock_df: pd.DataFrame) -> bool:
                # 因子计算等操作
                pass

            def on_day_result(self):
                # 对回测结果的分析. 比如计算收益率
                result = self.rate_of_return_calc(self.date, ["000001"])


        if __name__ == '__main__':
            d = Demo()
            # 启动回测
            d.start()

    """

    COLUMNS = ["BeginTime", "EndTime", "OpenPrice", "HighPrice", "LowPrice", "ClosePrice", "ThisVolume", "ThisTurnover",
               "PreClose", "UpLimit", "DropLimit", "Volume", "Turnover"]

    def __init__(self):
        self.__buy_time = ...
        self.__b_T = ...
        self.__sell_time = ...
        self.__s_T = ...

        self.__top_limit = ...

        self.__encoding = ...

        self.__source_path = ""

        self.__thread_workers = 50

        self.__top: dict = {}
        self.__market: Market = ...
        self.__symbol_filter: list = []

    def _c(self, filepath, date):
        symbol_code = os.path.split(filepath)[1].split('.')[0]
        df = pd.read_csv(filepath, encoding=self.__encoding, names=self.COLUMNS, index_col=False)
        # self.condition(symbol_code, date, df)
        if self.on_day_stock(symbol_code, date, df):
            self.__top[symbol_code] = df

    def set_source_path(self, source_path: str):
        """设置资源路径

        Args:
            source_path: 资源路径

        Returns:

        """
        if not os.path.exists(source_path):
            print(f"source path {source_path} not exists.")
            return
        self.__source_path = source_path

    def init(self, buy_time: int, buy_time_end: int, sell_time: int, sell_time_end: int, encoding: str = "utf-8") -> None:
        """初始化参数配置

        Args:
            buy_time: 买入时间
            buy_time_end: 买入时长(秒)
            sell_time: 卖出时间
            sell_time_end: 卖出时长(秒)
            encoding: 文件的编码格式. 作用于程序的所有读取和写入

        Returns: None

        """
        self.__buy_time = buy_time
        self.__b_T = buy_time_end
        self.__sell_time = sell_time
        self.__s_T = sell_time_end
        self.__encoding = encoding

    @staticmethod
    def _calc_average_price(df: pd.DataFrame) -> float:
        """计算均价"""
        turnover = df['Turnover'].iloc[-1] - df['Turnover'].iloc[0]
        volume = df['Volume'].iloc[-1] - df['Volume'].iloc[0]
        average_price = turnover / volume
        return average_price

    def _rate_of_return_calc(self, date: str):
        """计算收益率"""
        # 权重
        average_weight = 1 / len(self.__top)

        for symbol_code, df in self.__top.items():
            buy_time_end = datetime.strptime(str(self.__buy_time), "%H%M%S") + timedelta(seconds=self.__b_T)
            buy_time_end = int(buy_time_end.strftime("%H%M%S"))
            b_interval_df = df[(df['EndTime'] >= self.__buy_time) & (df['EndTime'] <= buy_time_end)]
            buy_price = self._calc_average_price(b_interval_df)

            next_date = self.get_next_day(date).strftime("%Y%m%d")
            files = glob(os.path.join(self.__source_path, next_date, f"{symbol_code}*"))
            if len(files) <= 0:
                print(f"找不到下一个交易日, 跳过. date:{date}, next_date:{next_date}, symbol_code:{symbol_code}")
                continue

            s_df = pd.read_csv(files[0], encoding=self.__encoding, names=self.COLUMNS, index_col=False)
            sell_time_end = datetime.strptime(str(self.__sell_time), "%H%M%S") + timedelta(seconds=self.__s_T)
            sell_time_end = int(sell_time_end.strftime("%H%M%S"))
            s_interval_df = s_df[
                (s_df['EndTime'] >= self.__sell_time) & (s_df['EndTime'] <= sell_time_end)]
            sell_price = self._calc_average_price(s_interval_df)

            pnl = (sell_price - buy_price) / buy_price
            s = average_weight * pnl

            rate = round(s * 100, 3)
            yield {
                "symbol": symbol_code,
                "pnl": pnl,
                "weight": average_weight,
                # 可能出现 -0.0
                "rate": 0.0 if rate == 0 else rate
            }

    @staticmethod
    def get_next_day(date: Union[str, datetime]) -> datetime:
        """获取下一个交易日

        Args:
            date: 日期

        Returns: 下一个交易日的datetime对象

        """
        global dt
        if isinstance(date, str):
            dt = datetime.strptime(date, '%Y%m%d')
        else:
            dt = date
        while True:
            dt = dt + timedelta(days=1)
            # 过滤掉周末
            if dt.weekday() < 5:
                break
        return dt

    @property
    def market(self):
        assert(isinstance(self.__market, Market))
        return self.__market

    @market.setter
    def market(self, market: Market):
        """设置市场

        Args:
            market: 市场

        Returns:

        """
        self.__market = market
        if market == Market.SZ:
            self.__symbol_filter = ['000', '002', '3']
        else:
            self.__symbol_filter = []

    def start(self, date: str = "*"):
        """启动回测

        Args:
            date: 回测日期. 默认目录下所有日期

        Returns:

        """
        path = os.path.join(self.__source_path, date)
        if date == '*':
            date_paths = glob(path)
        else:
            date_paths = [path]

        for date_path in date_paths:
            # clean cache
            self.__top.clear()

            with ThreadPoolExecutor(max_workers=self.__thread_workers) as e:
                for filepath in glob(os.path.join(date_path, '*')):
                    filename = os.path.split(filepath)[-1]
                    # symbol_code = os.path.splitext(filename)[0]
                    if len(self.__symbol_filter) > 0:
                        if filename[0] in self.__symbol_filter or filename[:3] in self.__symbol_filter:
                            e.submit(self._c, filepath, date)

            self.on_day_result()

            # # wait for result
            # symbol_codes = [str(i) for i in self.day_result()]
            # self._top = {code: self._top[code] for code in symbol_codes}

            # self._rate_of_return_calc(date)

    def rate_of_return_calc(self, date: str, symbol_codes: Union[list, set, tuple]):
        """收益率计算

        Args:
            date: 日期
            symbol_codes: 要计算的股票代码

        Returns:

        """
        self.__top = {code: self.__top[code] for code in symbol_codes}
        return self._rate_of_return_calc(date)

    def on_day_result(self):
        """当遍历完一天的个股时会调用这个函数
        ``子类必须实现``

        Returns:

        Raises: NotImplementedError

        """
        raise NotImplementedError

    def on_day_stock(self, symbol_code: str, date: str, stock_df: pd.DataFrame) -> bool:
        """当遍历完个股一天行情时会调用这个函数
        ``子类必须实现``
        ``该方法会运行在子线程``

        Args:
            symbol_code: 股票代码
            date: 日期
            stock_df: 行情数据

        Returns: 是否缓存当前 stock_df. 返回 true 会将当前 stock_df 缓存
            ``该缓存的数据会在计算收益率中使用, 无特殊需求, 返回True即可``

        Raises: NotImplementedError

        """
        raise NotImplementedError

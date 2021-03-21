"""
Created by x2h1z on 2021/2/26.
"""
import time
import pandas as pd

from A import A, Market


class Impl(A):
    """Example"""

    def __init__(self):
        super().__init__()
        # 设置数据路径
        self.set_source_path("/Users/x2h1z/Data/SZ")
        # 配置买入、卖出时间范围
        # 这里设置的是143000 - 150000时间段买入. 第二天的93000 - 100000时间段卖出
        self.init(143000, 30 * 60, 93000, 30 * 60)
        self.factor_result = {}
        self.date = ...
        self.result = []

    def on_day_result(self):
        # 选取排名前五支股票
        a = dict(sorted(self.factor_result.items(), key=lambda x: x[1], reverse=True))
        symbol_codes = list(a.keys())

        # 计算收益率
        # rate_of_return_calc 方法会返回一个 generator
        for result in self.rate_of_return_calc(self.date, symbol_codes):
            symbol_code = result['symbol']
            pnl = result['pnl']
            rate = result['rate']
            weight = result['weight']
            print(f"Date:{self.date}, SymbolCode:{symbol_code}, Weight:{weight}, Pnl:{pnl}, Rate of return:{rate}%")
            self.result.append({
                "code": symbol_code,
                "pnl": pnl,
                "rate": rate,
                "f1": self.factor_result[symbol_code]
            })

    def on_day_stock(self, symbol_code: str, date: str, stock_df: pd.DataFrame) -> bool:
        df = stock_df[(stock_df['EndTime'] >= 93000) & (stock_df['EndTime'] <= 143000)]
        # F1 = 阳线数 / 分钟线数
        F1 = len(df[df['OpenPrice'] < df['ClosePrice']]) / len(df)
        self.factor_result[symbol_code] = F1
        return True

    def get_result(self) -> list:
        return self.result

    def main(self, date: str):
        self.date = date
        # 市场选择
        self.set_market(Market.SZ)
        self.start(date)


if __name__ == "__main__":
    s = time.time()

    impl = Impl()
    impl.main("20200102")
    r = impl.get_result()

    df = pd.DataFrame(r)
    df.to_csv("20200102_result.csv", index=False)

    # with Pool() as p:
    #     for i in ["20200102"]:
    #         impl = Impl()
    #         p.apply_async(impl.main, (i,))
    #     p.close()
    #     p.join()

    print(f"consuming: {time.time() - s}")

import pandas as pd

from typing import List


def vwap_calc(df: pd.DataFrame, period: List[int]) -> float:
    """计算给定时段的成交量加权平均价

    Args:
        df: 格式: open high low close volume
        period: 时段

    Returns: vwap

    """
    start = period[0]
    end = period[1]

    p = df[start:end].apply(lambda x: (x['high'] + x['low']) / 2 * x['volume'], axis=1)
    vwap = p.sum() / df['volume'].sum()

    return vwap

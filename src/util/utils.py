import os
import re

from .holiday import get_holiday
from datetime import datetime
from typing import Union, Optional


def traverse_path(path: str) -> list:
    """遍历路径下的所有文件, ``包含子目录``

    :param path: 需要遍历的路径
    :return: 路径下的所有文件
    """
    r = []
    if os.path.isdir(path):
        for i in os.listdir(path):
            r += traverse_path(os.path.join(path, i))
    else:
        r.append(path)
    return r


def is_symbol_code(code: str) -> bool:
    """检查 code 是不是合法有效的 A 股股票代码

    :param code: 代码
    :return:
    """
    r = re.findall(r"(\d{6})", code)
    return len(code) <= 9 and len(r) > 0


def is_sz_symbol_code(code: str) -> bool:
    """检查股票代码是不是属于深交所

    :param code: 待检查的股票代码
    :return:
    """
    if '.' in code:
        a, b = code.split('.')
        return a.upper() == 'SZ' or b.upper() == 'SZ'
    else:
        return is_symbol_code(code) and code[:3] in ['000', '002', '300']


def is_sh_symbol_code(code: str) -> bool:
    """检查股票代码是不是属于上交所

    :param code: 待检查的股票代码
    :return:
    """
    if '.' in code:
        a, b = code.split('.')
        return a.upper() == 'SH' or b.upper() == 'SH'
    else:
        return is_symbol_code(code) and code[:3] in ['600', '603', '601']


def get_all_stock(root_path: str, date: Optional[datetime] = None) -> list:
    """获取数据路径下的所有股票代码

    :param root_path: 数据路径
    :param date: 日期. 可选,默认全部
    :return: 去重后的所有股票代码
    """
    if date:
        date_s = date.strftime('%Y%m%d')
        path = os.path.join(root_path, date_s[:4], date_s[:6], date_s)
    else:
        path = root_path

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not exists.")

    stocks = []
    for i in traverse_path(path):
        s = os.path.splitext(os.path.split(i)[-1])[0]
        # 检查一下是不是 A 股股票代码
        if is_sz_symbol_code(s) or is_sh_symbol_code(s):
            stocks.append(s)

    return stocks


def get_trading_day(start: Union[datetime, str], end: Optional[Union[str, datetime]] = None) -> list:
    """获取指定时间范围内的所有交易日,排除节假日和周末

    :param start: 开始时间. str 或 datetime 类型; ``需要注意的是 str 必须要是 YYYYMMDD 格式``
    :param end: 结束时间. 可选; str 或 datetime 类型; ``需要注意的是 str 必须要是 YYYYMMDD 格式``
    :return: 所有交易日
    """
    start_dt = start

    if isinstance(start, str):
        start_dt = datetime.strptime(start, "%Y%m%d")

    if end is not None:
        end_dt = end
        if isinstance(end, str):
            end_dt = datetime.strptime(end, "%Y%m%d")
    else:
        end_dt = datetime.today()

    trading_day = []

    holidays = get_holiday(start_dt, end_dt)

    while start_dt <= end_dt:
        # 排除周末和节假日
        if start_dt.weekday() > 4 or start_dt.strftime("%Y%m%d") in holidays:
            continue

        trading_day.append(start_dt)
        start_dt += timedelta(days=1)

    return trading_day

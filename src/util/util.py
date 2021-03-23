import os

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
    return len(code.split('.')[-1]) == 6


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
    :param date: 日期. 可选, 默认所有日期
    :return: 去重后的所有股票代码
    """
    stocks = []

    if date:
        date_s = date.strftime('%Y%m%d')
        path = os.path.join(root_path, date_s[:4], date_s[4:6], date_s)
    else:
        path = os.path.join(root_path, )

    if not os.path.exists(path):
        raise FileNotFoundError(f"Date {date} Data does not exist on this day.")

    return stocks

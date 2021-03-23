import unittest

from src.core import A, Market
from datetime import datetime


class TestStringMethods(unittest.TestCase):

    def test_get_next_day(self):
        next_day = A.get_next_day("20210323").strftime("%Y%m%d")
        self.assertEqual(next_day, "20210324")
        next_day = A.get_next_day(datetime.strptime("20210323", "%Y%m%d")).strftime("%Y%m%d")
        self.assertEqual(next_day, "20210324")

    def test_set_market(self):
        a = A()
        a.market = Market.SZ
        self.assertEqual(a.market, Market.SZ)


if __name__ == '__main__':
    unittest.main()

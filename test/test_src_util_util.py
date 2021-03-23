import unittest

from src.util import *
from datetime import timedelta


class TestUtil(unittest.TestCase):

    def test_is_sz_symbol_code(self):
        self.assertEqual(is_sz_symbol_code("000008"), True)
        self.assertEqual(is_sz_symbol_code("600010"), False)
        self.assertEqual(is_sz_symbol_code("SZ.000008"), True)
        self.assertEqual(is_sz_symbol_code("SH.600010"), False)
        self.assertEqual(is_sz_symbol_code("000008.SZ"), True)
        self.assertEqual(is_sz_symbol_code("600010.SH"), False)

    def test_is_sh_symbol_code(self):
        self.assertEqual(is_sh_symbol_code("000008"), False)
        self.assertEqual(is_sh_symbol_code("600010"), True)
        self.assertEqual(is_sh_symbol_code("SZ.000008"), False)
        self.assertEqual(is_sh_symbol_code("SH.600010"), True)
        self.assertEqual(is_sh_symbol_code("000008.SZ"), False)
        self.assertEqual(is_sh_symbol_code("600010.SH"), True)

    def test_is_symbol_code(self):
        self.assertEqual(is_symbol_code("000001"), True)
        self.assertEqual(is_symbol_code("00000"), False)
        self.assertEqual(is_symbol_code("ABCDEF"), False)

    def test_traverse_path(self):
        self.assertEqual(traverse_path(".").__len__(), 2)
        self.assertEqual(traverse_path("../src").__len__(), 7)
        self.assertEqual(traverse_path("../exmaple/data").__len__(), 6)

    def test_get_all_stock(self):
        self.assertEqual(get_all_stock("../exmaple/data").__len__(), 6)
        self.assertEqual(get_all_stock("../exmaple/data", datetime.today()).__len__(), 4)
        self.assertEqual(get_all_stock("../exmaple/data", datetime.today() - timedelta(days=1)).__len__(), 2)

    def test_get_trading_day(self):
        self.assertEqual(get_trading_day("20210101", "20210201").__len__(), 20)


if __name__ == '__main__':
    unittest.main()

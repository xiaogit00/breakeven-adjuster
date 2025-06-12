from src.services import db
import unittest
import asyncio
from src.utils import stoploss_adjuster
from src.tests import sample_SL_orders


class TestSLAdjuster(unittest.TestCase):
    # def test_check_for_SL_adjustment(self):
    #     open_sl_orders = db.get_open_SL_orders()
    #     adjustments = stoploss_adjuster.check_for_SL_adjustments(open_sl_orders, 175.1)
    #     print(adjustments)
    def test_adjust_SL_orders(self):
        open_sl_orders = db.get_open_SL_orders()
        stoploss_adjuster.adjust_SL_orders(open_sl_orders)
        



if __name__ == '__main__':
    asyncio.run(unittest.main())
from src.services import db
import unittest
import asyncio


class TestDB(unittest.TestCase):
    def test_get_open_SL_orders(self):
        res = db.get_open_SL_orders()
        print(res)


if __name__ == '__main__':
    asyncio.run(unittest.main())
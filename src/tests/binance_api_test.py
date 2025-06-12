from src.services import binanceREST
from src.services import db
import unittest
import asyncio


class TestDB(unittest.TestCase):
    def test_bianance(self):
        res = binanceREST.set_stop_loss('SOLUSDT', "SELL", 150, 0.09)
        print(res)


if __name__ == '__main__':
    asyncio.run(unittest.main())
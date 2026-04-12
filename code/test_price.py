# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from analysis.fetcher import StockFetcher

f = StockFetcher()
codes = ['601166', '600519', '601318', '600036']

for code in codes:
    r = f.get_a_stock_price(code)
    if r:
        pe = r.get('pe', 0)
        print(f'{code}: price={r.get("price")}, pe={pe}, source={r.get("source")}')
    else:
        print(f'{code}: failed')

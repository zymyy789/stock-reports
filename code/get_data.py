# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from analysis.fetcher import StockFetcher
from analysis.fund_fetcher import FundFetcher, FUND_CODE_LIST

sf = StockFetcher()
ff = FundFetcher()

print('=== 股票 ===')
stocks = ['601166', '600036', '601318', '600030', '600887', '000858', '000333', '600519', '600276', '601888']
for c in stocks:
    d = sf.get_a_stock_price(c)
    if d:
        pe = d.get('pe', 0)
        change = d.get('change_pct', 0)
        print(f'{c}|{d["name"]}|{d["price"]}|{pe}|{change}')

print('=== 基金 ===')
for c in FUND_CODE_LIST[:10]:
    d = ff.get_fund_basic_info(c)
    if d:
        print(f'{c}|{d["name"]}|{d["net_value"]}|{d["daily_change"]}')
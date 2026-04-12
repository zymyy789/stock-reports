# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
from analysis.fund_fetcher import FundFetcher

f = FundFetcher()
r = f.get_fund_basic_info('510050')
print(f"名称: {r['name']}")
print(f"净值: {r['net_value']}")
print(f"涨跌: {r['daily_change']}%")
print(f"来源: {r['source']}")

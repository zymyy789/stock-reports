# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from analysis.fund_fetcher import FundFetcher, FUND_CODE_LIST

ff = FundFetcher()
print("获取基金数据:")
for code in FUND_CODE_LIST[:5]:
    d = ff.get_fund_basic_info(code)
    if d:
        print(f"{code}: {d['name']}, nav={d['net_value']}, change={d['daily_change']}%")
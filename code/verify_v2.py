# -*- coding: utf-8 -*-
import urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://zymyy789.github.io/stock-reports/web/index.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(url, timeout=10)
html = resp.read().decode('utf-8')

checks = [
    ('Web App v2', '智能投资分析' in html),
    ('真实数据', '上证指数' in html and '兴业银行' in html),
    ('模拟持仓', '兴业银行' in html and '招商银行' in html),
    ('买入信号', '五粮液' in html or '信号' in html),
    ('交易功能', 'doTrade' in html),
]

print('=== Web App 验证 ===')
for name, ok in checks:
    print(f'  [{("OK" if ok else "FAIL")}] {name}')

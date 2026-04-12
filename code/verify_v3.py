# -*- coding: utf-8 -*-
import urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://zymyy789.github.io/stock-reports/web/index.html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(url, timeout=10)
html = resp.read().decode('utf-8')

checks = [
    ('Web App v3', '智能投资分析' in html),
    ('10只股票', html.count('兴业银行') > 0 and html.count('贵州茅台') > 0),
    ('10只基金', html.count('上证50ETF') > 0 and html.count('沪深300ETF') > 0),
    ('市场指数', html.count('上证指数') > 0),
    ('买入信号', html.count('五粮液') > 0),
    ('模拟持仓', html.count('兴业银行') > 0 and html.count('招商银行') > 0),
    ('交易功能', 'executeBuy' in html and 'executeSell' in html),
    ('弹窗关闭', 'closeModal' in html and 'closeTrade' in html),
    ('点击事件', 'onclick=' in html),
]

print('=== Web App v3 验证 ===')
all_ok = True
for name, ok in checks:
    if not ok:
        all_ok = False
    print(f'  [{("OK" if ok else "FAIL")}] {name}')
print()
print('结果:', '全部通过' if all_ok else '存在问题')
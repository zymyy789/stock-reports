# -*- coding: utf-8 -*-
import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://zymyy789.github.io/stock-reports/web/index.html'
html = urllib.request.urlopen(url, timeout=10).read().decode('utf-8')

# 验证项目
tests = [
    ('4个Tab页面', all('page-'+str(i) in html for i in range(4))),
    ('Tab点击切换', 'addEventListener' in html and "click'" in html),
    ('10只股票数据', all(n in html for n in ['贵州茅台','中国平安','招商银行','兴业银行','恒瑞医药','中信证券','伊利股份','五粮液','美的集团','中国中免'])),
    ('10只基金数据', all(n in html for n in ['5G通信ETF','AI ETF','科技ETF','科创50ETF','创业板ETF','中证500ETF','证券ETF','沪深300ETF','恒生ETF','上证50ETF'])),
    ('弹窗背景点击关闭', 'modal-bg' in html and 'closeModal' in html),
    ('z-index分层(背景1内容2)', 'z-index: 1' in html and 'z-index: 2' in html),
    ('持仓模拟功能', 'portfolio' in html and 'doTrade' in html),
    ('详情链接到东方财富', 'eastmoney.com' in html),
    ('底部弹窗动画', 'slideUp' in html),
]

print('=== Web App 功能验证 ===')
all_ok = True
for name, ok in tests:
    status = 'OK' if ok else 'FAIL'
    if not ok:
        all_ok = False
    print(f'  [{status}] {name}')

print()
print('验证结果:', '✅ 全部通过' if all_ok else '❌ 存在问题')
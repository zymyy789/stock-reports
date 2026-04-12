# -*- coding: utf-8 -*-
import urllib.request, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

# 腾讯接口获取指数
indices = [('上证指数','sh000001'),('深证成指','sh399001'),('沪深300','sh000300'),('创业板指','sz399006'),('恒生指数','hkHSI')]
print('=== 实时指数 ===')
for name, code in indices:
    try:
        url = f'https://qt.gtimg.cn/q={code}'
        req = urllib.request.Request(url, headers={'Referer':'https://gu.qq.com/'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('gbk')
        parts = data.split('~')
        if len(parts) > 3 and parts[3]:
            price = parts[3]
            change_pct = parts[32] if len(parts) > 32 else 'N/A'
            print(f'{name}: {price} ({change_pct}%)')
    except Exception as e:
        print(f'{name}: 获取失败 {e}')

# 个股
stocks = [('贵州茅台','sh600519'),('中国平安','sh601318'),('招商银行','sh600036'),('五粮液','sz000858'),('美的集团','sz000333'),('兴业银行','sh601166'),('中信证券','sh600030'),('伊利股份','sh600887'),('恒瑞医药','sh600276'),('中国中免','sh601888')]
print()
print('=== 个股行情 ===')
for name, code in stocks:
    try:
        url = f'https://qt.gtimg.cn/q={code}'
        req = urllib.request.Request(url, headers={'Referer':'https://gu.qq.com/'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('gbk')
        parts = data.split('~')
        if len(parts) > 3 and parts[3]:
            price = parts[3]
            change_pct = parts[32]
            pe = parts[39] if len(parts) > 39 else 'N/A'
            print(f'{name}: {price} ({change_pct}%) PE:{pe}')
    except Exception as e:
        print(f'{name}: 失败 {e}')

# 基金估值
print()
print('=== 基金估值 ===')
funds = [('510050','上证50ETF'),('510300','沪深300ETF'),('510500','中证500ETF'),('159915','创业板ETF'),('588000','科创50ETF'),('512880','证券ETF'),('515000','科技ETF'),('159819','AI ETF'),('159920','恒生ETF'),('515050','5G ETF')]
for code, name in funds:
    try:
        url = f'https://fundgz.1234567.com.cn/js/{code}.js'
        req = urllib.request.Request(url, headers={'Referer':'https://fund.eastmoney.com/'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8')
        m1 = re.search(r'"gsz":"([^"]+)"', data)
        m2 = re.search(r'"gszzl":"([^"]+)"', data)
        m3 = re.search(r'"dwjz":"([^"]+)"', data)
        if m1 and m2 and m3:
            print(f'{name}({code}): 估值{m1.group(1)} 涨跌{m2.group(1)}% 净值{m3.group(1)}')
    except Exception as e:
        print(f'{name}({code}): 失败 {e}')

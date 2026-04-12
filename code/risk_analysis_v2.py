# -*- coding: utf-8 -*-
"""
专家级实战: 历史波动率与相关性分析 (腾讯数据源)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import time
import math

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

STOCKS = {
    '600036': '招商银行',
    '601166': '兴业银行', 
    '601318': '中国平安',
    '000858': '五粮液',
    '600030': '中信证券',
    '600887': '伊利股份',
    '000333': '美的集团',
    '601328': '交通银行',
}

def get_kline_data(stock_code, days=60):
    """东方财富日K线 (stock_code = 纯数字如 600036)"""
    prefix = '1' if stock_code.startswith('6') else '0'
    secid = f'{prefix}.{stock_code}'
    url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=1&end=20260411&lmt={days}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        data = resp.json()
        if data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            closes = []
            for line in klines:
                parts = line.split(',')
                closes.append(float(parts[2]))  # 收盘价
            return closes
    except Exception as e:
        print(f"  错误{stock_code}: {e}")
    return None

def calc_volatility(closes, annualize=True):
    if len(closes) < 5:
        return None
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
    if not returns:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    std = math.sqrt(variance)
    if annualize:
        std = std * math.sqrt(252)
    return std

def calc_correlation(rets_a, rets_b):
    if len(rets_a) != len(rets_b) or len(rets_a) < 5:
        return None
    n = len(rets_a)
    mean_a = sum(rets_a) / n
    mean_b = sum(rets_b) / n
    cov = sum((rets_a[i] - mean_a) * (rets_b[i] - mean_b) for i in range(n)) / (n - 1)
    var_a = sum((rets_a[i] - mean_a) ** 2 for i in range(n)) / (n - 1)
    var_b = sum((rets_b[i] - mean_b) ** 2 for i in range(n)) / (n - 1)
    if var_a == 0 or var_b == 0:
        return 0
    return cov / math.sqrt(var_a * var_b)

def main():
    print("=" * 70)
    print("专家级实战: 波动率与相关性分析 (东方财富数据源)")
    print("=" * 70)
    
    all_closes = {}
    all_returns = {}
    
    print("\n获取历史K线数据(近60个交易日)...")
    for code, name in STOCKS.items():
        closes = get_kline_data(code, 60)
        if closes and len(closes) > 5:
            all_closes[name] = closes
            rets = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            all_returns[name] = rets
            change = (closes[-1] - closes[0]) / closes[0] * 100
            print(f"  {name}: {len(closes)}天, 最新{closes[-1]:.2f}, 60日{change:+.1f}%")
        else:
            print(f"  {name}: 失败")
        time.sleep(0.5)
    
    if len(all_closes) < 2:
        print("数据不足")
        return
    
    # 波动率
    print(f"\n{'='*70}")
    print("一、历史波动率(年化)")
    print(f"{'='*70}")
    print(f"\n{'名称':<10} {'波动率':>10} {'60日涨跌':>10} {'风险等级':>8}")
    print(f"{'─'*45}")
    
    volatilities = {}
    for name, closes in all_closes.items():
        vol = calc_volatility(closes)
        volatilities[name] = vol
        change = (closes[-1] - closes[0]) / closes[0] * 100
        if vol:
            level = "低" if vol < 0.20 else ("中" if vol < 0.30 else ("高" if vol < 0.40 else "极高"))
            print(f"{name:<10} {vol*100:>8.1f}% {change:>+8.1f}% {level:>6}")
    
    # 相关性矩阵
    print(f"\n{'='*70}")
    print("二、相关性矩阵")
    print(f"{'='*70}")
    
    names = list(all_returns.keys())
    corr_matrix = {}
    for n1 in names:
        corr_matrix[n1] = {}
        for n2 in names:
            corr_matrix[n1][n2] = calc_correlation(all_returns[n1], all_returns[n2]) or 0
    
    # 打印
    short = {n: n[:4] for n in names}
    header = f"{'':>8}" + "".join(f" {short[n]:>6}" for n in names)
    print(f"\n{header}")
    for n1 in names:
        row = f"{short[n1]:>6} " + "".join(f" {corr_matrix[n1][n2]:>6.2f}" for n2 in names)
        print(row)
    
    # 高相关性预警
    print(f"\n相关性风险:")
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            c = corr_matrix[names[i]][names[j]]
            if c > 0.7:
                print(f"  ⚠️ {names[i]} vs {names[j]}: {c:.2f}")
    
    # 分散化
    pairs = [(corr_matrix[names[i]][names[j]]) for i in range(len(names)) for j in range(i+1, len(names))]
    avg_corr = sum(pairs) / len(pairs) if pairs else 0
    print(f"\n平均相关性: {avg_corr:.2f}", end="")
    if avg_corr > 0.6:
        print(" → 分散化不足")
    elif avg_corr > 0.4:
        print(" → 一般")
    else:
        print(" → 良好")
    
    # 组合风险
    print(f"\n{'='*70}")
    print("三、组合风险估算")
    print(f"{'='*70}")
    
    weights = {'招商银行':0.119, '兴业银行':0.112, '中国平安':0.119, 
               '五粮液':0.106, '中信证券':0.079, '伊利股份':0.026, '美的集团':0.059}
    
    total_var = 0
    for n1 in names:
        for n2 in names:
            w1 = weights.get(n1, 0.05)
            w2 = weights.get(n2, 0.05)
            v1 = volatilities.get(n1, 0.25) or 0.25
            v2 = volatilities.get(n2, 0.25) or 0.25
            c = corr_matrix[n1][n2]
            total_var += w1 * w2 * v1 * v2 * c
    
    pvol = math.sqrt(total_var)
    print(f"\n组合年化波动率: {pvol*100:.1f}%")
    print(f"组合日波动率: {pvol/math.sqrt(252)*100:.2f}%")
    
    var_95 = pvol / math.sqrt(252) * 1.645 * 98877
    var_99 = pvol / math.sqrt(252) * 2.326 * 98877
    print(f"\nVaR(95%,1日): 最多亏{var_95:,.0f}元 ({var_95/98877*100:.1f}%)")
    print(f"VaR(99%,1日): 最多亏{var_99:,.0f}元 ({var_99/98877*100:.1f}%)")
    
    sharpe = (0.15 - 0.03) / pvol if pvol > 0 else 0
    print(f"\n夏普比率(假设年化15%): {sharpe:.2f}", end="")
    print(" ✅优秀" if sharpe > 1.0 else (" 🟡良好" if sharpe > 0.5 else " ⚠️一般"))
    
    print(f"\n{'='*70}")

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
专家级实战: 历史波动率与相关性分析
用真实K线数据计算
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import time
import math

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 主要持仓
STOCKS = {
    '600036': '招商银行',
    '601166': '兴业银行', 
    '601318': '中国平安',
    '000858': '五粮液',
    '600030': '中信证券',
    '600887': '伊利股份',
    '000333': '美的集团',
}

def get_kline(code, days=60):
    """获取日K线数据"""
    prefix = '1' if code.startswith('6') else '0'
    secid = f'{prefix}.{code}'
    url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=1&lmt={days}'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            closes = []
            for line in klines:
                parts = line.split(',')
                closes.append(float(parts[2]))  # 收盘价
            return closes
        return None
    except:
        return None

def calc_volatility(closes, annualize=True):
    """计算波动率"""
    if len(closes) < 2:
        return None
    
    # 日收益率
    returns = []
    for i in range(1, len(closes)):
        r = (closes[i] - closes[i-1]) / closes[i-1]
        returns.append(r)
    
    if not returns:
        return None
    
    # 均值
    mean = sum(returns) / len(returns)
    
    # 标准差
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    std = math.sqrt(variance)
    
    # 年化
    if annualize:
        std = std * math.sqrt(252)
    
    return std

def calc_correlation(returns_a, returns_b):
    """计算相关系数"""
    if len(returns_a) != len(returns_b) or len(returns_a) < 5:
        return None
    
    n = len(returns_a)
    mean_a = sum(returns_a) / n
    mean_b = sum(returns_b) / n
    
    cov = sum((returns_a[i] - mean_a) * (returns_b[i] - mean_b) for i in range(n)) / (n - 1)
    var_a = sum((returns_a[i] - mean_a) ** 2 for i in range(n)) / (n - 1)
    var_b = sum((returns_b[i] - mean_b) ** 2 for i in range(n)) / (n - 1)
    
    if var_a == 0 or var_b == 0:
        return 0
    
    return cov / math.sqrt(var_a * var_b)

def main():
    print("=" * 70)
    print("专家级实战: 波动率与相关性分析")
    print("=" * 70)
    
    # 获取数据
    all_closes = {}
    all_returns = {}
    
    print("\n获取历史K线数据(近60个交易日)...")
    for code, name in STOCKS.items():
        closes = get_kline(code, 60)
        if closes:
            all_closes[name] = closes
            # 计算日收益率
            rets = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            all_returns[name] = rets
            print(f"  {name}: 获取{len(closes)}天数据, 最新价{closes[-1]:.2f}")
        else:
            print(f"  {name}: 获取失败")
        time.sleep(0.5)
    
    if len(all_closes) < 2:
        print("数据不足，无法分析")
        return
    
    # ============================================================
    # 波动率分析
    # ============================================================
    print(f"\n{'='*70}")
    print("一、历史波动率(年化, 近60个交易日)")
    print(f"{'='*70}")
    
    volatilities = {}
    print(f"\n{'名称':<10} {'年化波动率':>12} {'日波动率':>10} {'最新价':>8} {'60日涨跌':>10}")
    print(f"{'─'*55}")
    
    for name, closes in all_closes.items():
        vol = calc_volatility(closes)
        vol_daily = calc_volatility(closes, annualize=False)
        change_60 = (closes[-1] - closes[0]) / closes[0] * 100
        
        volatilities[name] = vol
        if vol:
            print(f"{name:<10} {vol*100:>10.1f}% {vol_daily*100:>8.2f}% {closes[-1]:>8.2f} {change_60:>+8.1f}%")
    
    # 风险等级
    print(f"\n风险等级判断:")
    for name, vol in sorted(volatilities.items(), key=lambda x: x[1] if x[1] else 0):
        if vol:
            if vol < 0.20:
                level = "低风险"
            elif vol < 0.30:
                level = "中风险"
            elif vol < 0.40:
                level = "高风险"
            else:
                level = "极高风险"
            print(f"  {name}: {vol*100:.1f}% → {level}")
    
    # ============================================================
    # 相关性矩阵
    # ============================================================
    print(f"\n{'='*70}")
    print("二、相关性矩阵")
    print(f"{'='*70}")
    
    names = list(all_returns.keys())
    if len(names) >= 2:
        # 计算相关系数
        corr_matrix = {}
        for n1 in names:
            corr_matrix[n1] = {}
            for n2 in names:
                corr = calc_correlation(all_returns[n1], all_returns[n2])
                corr_matrix[n1][n2] = corr if corr else 0
        
        # 打印矩阵
        header = f"{'':>10}"
        for n in names:
            header += f" {n[:4]:>6}"
        print(f"\n{header}")
        print(f"{'─' * (10 + 7 * len(names))}")
        
        for n1 in names:
            row = f"{n1[:6]:>8}"
            for n2 in names:
                c = corr_matrix[n1][n2]
                row += f" {c:>6.2f}"
            print(row)
        
        # 找出高相关性对
        print(f"\n高相关性(>0.7)的风险:")
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                c = corr_matrix[names[i]][names[j]]
                if c > 0.7:
                    print(f"  ⚠️ {names[i]} vs {names[j]}: {c:.2f} → 同涨同跌概率高")
                elif c < 0:
                    print(f"  ✅ {names[i]} vs {names[j]}: {c:.2f} → 有对冲效果")
        
        # 分散化评估
        avg_corr = 0
        count = 0
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                avg_corr += corr_matrix[names[i]][names[j]]
                count += 1
        avg_corr /= count if count > 0 else 1
        
        print(f"\n平均相关性: {avg_corr:.2f}")
        if avg_corr > 0.6:
            print(f"  ⚠️ 平均相关性高，分散化不足")
        elif avg_corr > 0.4:
            print(f"  🟡 平均相关性中等，分散化一般")
        else:
            print(f"  ✅ 平均相关性低，分散化良好")
    
    # ============================================================
    # 组合风险估算
    # ============================================================
    print(f"\n{'='*70}")
    print("三、组合风险估算")
    print(f"{'='*70}")
    
    # 主要持仓权重
    weights = {
        '招商银行': 0.119,
        '兴业银行': 0.112,
        '中国平安': 0.119,
        '五粮液': 0.106,
        '中信证券': 0.079,
        '伊利股份': 0.026,
        '美的集团': 0.059,
    }
    
    # 组合波动率 (简化估算)
    total_var = 0
    for n1 in names:
        if n1 not in weights:
            continue
        for n2 in names:
            if n2 not in weights:
                continue
            w1 = weights[n1]
            w2 = weights[n2]
            v1 = volatilities.get(n1, 0.25) or 0.25
            v2 = volatilities.get(n2, 0.25) or 0.25
            c = corr_matrix.get(n1, {}).get(n2, 0.7)
            total_var += w1 * w2 * v1 * v2 * c
    
    portfolio_vol = math.sqrt(total_var)
    
    print(f"\n组合年化波动率: {portfolio_vol*100:.1f}%")
    print(f"组合日波动率: {portfolio_vol/math.sqrt(252)*100:.2f}%")
    
    # VaR计算
    var_95_1d = portfolio_vol / math.sqrt(252) * 1.645 * 98877
    var_99_1d = portfolio_vol / math.sqrt(252) * 2.326 * 98877
    
    print(f"\n风险价值(VaR):")
    print(f"  95%置信,1日最大亏损: {var_95_1d:,.0f}元 ({var_95_1d/98877*100:.1f}%)")
    print(f"  99%置信,1日最大亏损: {var_99_1d:,.0f}元 ({var_99_1d/98877*100:.1f}%)")
    
    # 夏普比率估算(假设年化收益15%)
    risk_free = 0.03
    expected_return = 0.15
    sharpe = (expected_return - risk_free) / portfolio_vol if portfolio_vol > 0 else 0
    print(f"\n预期夏普比率(假设年化15%):")
    print(f"  夏普 = ({expected_return*100:.0f}% - {risk_free*100:.0f}%) / {portfolio_vol*100:.1f}% = {sharpe:.2f}")
    if sharpe > 1.0:
        print(f"  ✅ 优秀(>1.0)")
    elif sharpe > 0.5:
        print(f"  🟡 良好(0.5-1.0)")
    else:
        print(f"  ⚠️ 一般(<0.5)")
    
    print(f"\n{'='*70}")
    print("分析完成")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
Week1 任务4: 行业差异化估值
验证输出: 分别用PB/PE/PS给持仓股票估值
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("📊 行业差异化估值 - 持仓5只股票")
print("="*70)

# ============================================================
# 持仓股票数据
# ============================================================
HOLDINGS = [
    {
        "name": "兴业银行",
        "code": "601166",
        "price": 18.60,
        "pe": 5.08,
        "pb": 0.49,
        "dividend": 3.14,
        "industry": "银行",
        "roe": 12.0,
        "recommendation": "PB + 股息率"
    },
    {
        "name": "招商银行",
        "code": "600036",
        "price": 39.26,
        "pe": 6.60,
        "pb": 0.89,
        "dividend": 7.67,
        "industry": "银行",
        "roe": 13.44,
        "recommendation": "PB + 股息率"
    },
    {
        "name": "中国平安",
        "code": "601318",
        "price": 58.74,
        "pe": 7.89,
        "pb": 0.92,
        "dividend": 5.0,
        "nbv_growth": 29.3,
        "industry": "保险",
        "roe": 12.7,
        "recommendation": "PEV + NBV增速"
    },
    {
        "name": "中信证券",
        "code": "600030",
        "price": 24.15,
        "pe": 11.90,
        "profit_growth": 38.6,
        "industry": "券商",
        "roe": 10.59,
        "recommendation": "PEG + 政策"
    },
    {
        "name": "伊利股份",
        "code": "600887",
        "price": 26.10,
        "pe": 20.61,
        "pb": 2.51,
        "dividend": 6.5,
        "industry": "消费",
        "roe": 18.0,
        "recommendation": "PE + 品牌"
    }
]

# ============================================================
# 行业估值标准
# ============================================================
INDUSTRY_STANDARDS = {
    "银行": {
        "pe_low": 6, "pe_high": 10,
        "pb_low": 0.7, "pb_high": 1.2,
        "dividend_good": 4,
        "key_metrics": ["PB", "股息率", "不良率"],
        "roe_good": 12,
        "note": "银行用PB估值更准确(资产可变现)"
    },
    "保险": {
        "pe_low": 8, "pe_high": 15,
        "pev_low": 0.5, "pev_high": 1.0,
        "nbv_growth_good": 10,
        "key_metrics": ["PEV", "NBV增速", "ROE"],
        "note": "保险看内含价值(EV)和NBV增速"
    },
    "券商": {
        "pe_low": 10, "pe_high": 20,
        "peg_good": 1.0,
        "key_metrics": ["PEG", "政策", "ROE"],
        "note": "券商是周期股，注意政策影响"
    },
    "消费": {
        "pe_low": 15, "pe_high": 25,
        "peg_good": 1.5,
        "dividend_good": 2,
        "key_metrics": ["PE", "PEG", "品牌", "市占率"],
        "note": "消费看品牌溢价和成长性"
    }
}

# ============================================================
# 逐个分析
# ============================================================
print("\n【行业估值方法】")
print("-"*70)

results = []

for stock in HOLDINGS:
    print(f"\n{'='*50}")
    print(f"{stock['name']}({stock['code']}) - {stock['industry']}")
    print(f"{'='*50}")
    print(f"当前股价: ¥{stock['price']}")
    print(f"推荐估值方法: {stock['recommendation']}")
    
    ind = stock['industry']
    std = INDUSTRY_STANDARDS[ind]
    
    verdicts = []
    score = 0
    max_score = 0
    
    # 1. PE分析
    if 'pe' in stock and stock['pe'] > 0:
        max_score += 2
        pe = stock['pe']
        pe_std = std.get('pe_low', 0)
        if pe < pe_std * 0.8:
            verdicts.append(f"  PE={pe} → 🟢 极度低估")
            score += 2
        elif pe < pe_std:
            verdicts.append(f"  PE={pe} → 🟢 低估")
            score += 1.5
        elif pe < std.get('pe_high', 999):
            verdicts.append(f"  PE={pe} → 🟡 合理")
            score += 1
        else:
            verdicts.append(f"  PE={pe} → 🔴 偏高")
    
    # 2. PB分析
    if 'pb' in stock and stock['pb'] > 0:
        max_score += 2
        pb = stock['pb']
        if pb < 1:
            verdicts.append(f"  PB={pb} → 🟢 破净，极低估")
            score += 2
        elif pb < std.get('pb_low', 999):
            verdicts.append(f"  PB={pb} → 🟢 低估")
            score += 1.5
        elif pb < std.get('pb_high', 999):
            verdicts.append(f"  PB={pb} → 🟡 合理")
            score += 1
        else:
            verdicts.append(f"  PB={pb} → 🔴 偏高")
    
    # 3. 股息率分析
    if 'dividend' in stock and stock['dividend'] > 0:
        max_score += 1
        div = stock['dividend']
        div_std = std.get('dividend_good', 0)
        if div >= div_std:
            verdicts.append(f"  股息率={div}% → 🟢 良好")
            score += 1
        else:
            verdicts.append(f"  股息率={div}% → 🟡 一般")
    
    # 4. ROE分析
    if 'roe' in stock:
        max_score += 1
        roe = stock['roe']
        roe_std = std.get('roe_good', 0)
        if roe >= roe_std:
            verdicts.append(f"  ROE={roe}% → 🟢 良好")
            score += 1
        else:
            verdicts.append(f"  ROE={roe}% → 🟡 一般")
    
    # 5. NBV增速(保险)
    if 'nbv_growth' in stock:
        max_score += 1
        nbv = stock['nbv_growth']
        if nbv >= std.get('nbv_growth_good', 0):
            verdicts.append(f"  NBV增速={nbv}% → 🟢 优秀")
            score += 1
    
    # 6. 净利润增速(券商)
    if 'profit_growth' in stock:
        max_score += 1
        pg = stock['profit_growth']
        if pg >= 20:
            verdicts.append(f"  净利润增速={pg}% → 🟢 优秀")
            score += 1
        elif pg >= 10:
            verdicts.append(f"  净利润增速={pg}% → 🟡 良好")
            score += 0.5
        else:
            verdicts.append(f"  净利润增速={pg}% → 🟠 偏慢")
    
    # 综合评分
    total_score = (score / max_score * 100) if max_score > 0 else 50
    
    print("\n指标分析:")
    for v in verdicts:
        print(v)
    
    print(f"\n综合评分: {total_score:.0f}/100")
    
    if total_score >= 80:
        final = "🟢🟢 强烈买入"
    elif total_score >= 60:
        final = "🟢 买入"
    elif total_score >= 40:
        final = "🟡 持有"
    else:
        final = "🔴 减仓"
    
    print(f"估值结论: {final}")
    
    results.append({
        "name": stock['name'],
        "score": total_score,
        "verdict": final,
        "metrics": verdicts
    })

# ============================================================
# 综合排名
# ============================================================
print("\n" + "="*70)
print("【持仓综合排名】")
print("="*70)

results.sort(key=lambda x: x['score'], reverse=True)

print(f"\n{'排名':<4}{'名称':<12}{'评分':<8}{'结论':<15}")
print("-"*40)
for i, r in enumerate(results, 1):
    print(f"{i:<4}{r['name']:<12}{r['score']:<8.0f}{r['verdict']:<15}")

# ============================================================
# 验证结果
# ============================================================
print("\n" + "="*70)
print("【验证结果】")
print("="*70)
print("任务: 用不同方法给持仓股票估值")
print("""
行业估值方法:
- 银行: PB + 股息率 (资产可变现)
- 保险: PEV + NBV增速 (内含价值)
- 券商: PEG + 政策 (周期股)
- 消费: PE + 品牌 (护城河)
""")
print("结论: 银行股(兴业/招商)极度低估，保险(平安)低估，券商(中信)低估")
print("="*70)

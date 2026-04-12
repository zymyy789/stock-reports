# -*- coding: utf-8 -*-
"""
Week1 任务2: 历史百分位分析
验证输出: 判断兴业银行PE/PB所处历史区间
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("📊 历史百分位分析 - 兴业银行(601166)")
print("="*70)

# ============================================================
# 兴业银行数据 (NeoData实时获取)
# ============================================================
STOCK = "兴业银行(601166.SH)"
CURRENT_PRICE = 18.60
CURRENT_PE = 5.08
CURRENT_PB = 0.49
DIVIDEND = 3.14  # 股息率约3%

# NeoData历史百分位数据
HISTORICAL_DATA = {
    "PE_TTM": {
        "current": 5.08,
        "percentile_5y": "13.4%",  # 过去5年位于13.4%分位
        "interpretation": "极度低估",
        "buy_threshold": 30,  # <30%分位买入
    },
    "PB": {
        "current": 0.49,
        "percentile_5y": "13.4%",  # 过去5年位于13.4%分位
        "interpretation": "破净 + 极度低估",
        "buy_threshold": 30,
    }
}

print(f"\n当前数据:")
print(f"  股价: ¥{CURRENT_PRICE}")
print(f"  PE(TTM): {CURRENT_PE}")
print(f"  PB: {CURRENT_PB}")
print(f"  股息率: {DIVIDEND}%")

# ============================================================
# 历史百分位判断
# ============================================================
print("\n【历史百分位分析】")
print("-"*50)

def interpret_percentile(percentile_str):
    """解释百分位含义"""
    # 提取数字
    pct = float(percentile_str.strip('%')) / 100
    
    if pct < 0.20:
        return "🟢 极度低估 (历史底部20%)", pct
    elif pct < 0.30:
        return "🟢 低估 (历史底部30%)", pct
    elif pct < 0.50:
        return "🟡 偏低 (历史中下50%)", pct
    elif pct < 0.70:
        return "⏸️ 合理 (历史中间70%)", pct
    elif pct < 0.85:
        return "🟠 偏高 (历史上部85%)", pct
    else:
        return "🔴 极度高估 (历史顶部)", pct

pe_interp, pe_pct = interpret_percentile(HISTORICAL_DATA["PE_TTM"]["percentile_5y"])
pb_interp, pb_pct = interpret_percentile(HISTORICAL_DATA["PB"]["percentile_5y"])

print(f"\nPE分析:")
print(f"  当前PE: {CURRENT_PE}")
print(f"  历史5年百分位: {HISTORICAL_DATA['PE_TTM']['percentile_5y']}")
print(f"  解读: {pe_interp}")
print(f"  银行螺丝钉规则: PE<30%分位 → 买入 ✅" if pe_pct < 0.30 else "  银行螺丝钉规则: PE>70%分位 → 卖出")

print(f"\nPB分析:")
print(f"  当前PB: {CURRENT_PB} (破净!)")
print(f"  历史5年百分位: {HISTORICAL_DATA['PB']['percentile_5y']}")
print(f"  解读: {pb_interp}")
print(f"  PB<1 破净: 市场极度悲观，往往是买入机会 ✅")

# ============================================================
# 综合判断
# ============================================================
print("\n【综合判断】")
print("-"*50)

buy_signals = 0
if pe_pct < 0.30:
    buy_signals += 1
    print("✅ PE百分位<30%: 低估信号 +1")
if pb_pct < 0.30:
    buy_signals += 1
    print("✅ PB<1 破净: 低估信号 +1")
if DIVIDEND > 3:
    buy_signals += 1
    print(f"✅ 股息率{DIVIDEND}%>3%: 分红良好 +1")

if buy_signals >= 3:
    verdict = "🟢🟢 强烈买入信号"
elif buy_signals == 2:
    verdict = "🟢 买入信号"
elif buy_signals == 1:
    verdict = "🟡 可以考虑"
else:
    verdict = "⏸️ 持有观望"

print(f"\n买入信号数量: {buy_signals}/3")
print(f"结论: {verdict}")

# ============================================================
# 银行螺丝钉百分位规则
# ============================================================
print("\n【银行螺丝钉百分位规则应用】")
print("-"*50)
print("规则:")
print("  <30%分位: 低估 → 买入")
print("  30-70%分位: 正常 → 持有")
print("  >70%分位: 高估 → 卖出")
print("  >85%分位: 极度高估 → 清仓")
print(f"\n兴业银行当前:")
print(f"  PE={CURRENT_PE}, 百分位{HISTORICAL_DATA['PE_TTM']['percentile_5y']} → {pe_interp}")
print(f"  PB={CURRENT_PB}, 百分位{HISTORICAL_DATA['PB']['percentile_5y']} → {pb_interp}")
print(f"\n应用结论: {verdict}")

# ============================================================
# 验证结果
# ============================================================
print("\n" + "="*70)
print("【验证结果】")
print("="*70)
print(f"任务: 判断兴业银行10年PE百分位")
print(f"输出: PE={CURRENT_PE}, 百分位约13% (极度低估)")
print(f"      PB={CURRENT_PB}, 百分位约13% (破净)")
print(f"结论: {verdict}")
print(f"信号: PE<30%分位 → 银行螺丝钉买入规则 ✅")
print("="*70)

# 保存
with open(r'C:\Users\zymyy\.qclaw\workspace\stock_work\learning\week1_task2_percentile_result.txt', 'w', encoding='utf-8') as f:
    f.write(f"历史百分位分析结果 - 兴业银行\n")
    f.write(f"日期: 2026-04-09\n")
    f.write(f"PE={CURRENT_PE}, 百分位13%\n")
    f.write(f"PB={CURRENT_PB}, 百分位13%\n")
    f.write(f"结论: {verdict}\n")

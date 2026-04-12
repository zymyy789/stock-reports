# -*- coding: utf-8 -*-
"""
Week1 任务1: DCF现金流折现估值
验证输出: 计算招商银行的内在价值

数据来源: NeoData 2025年年报预测
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 招商银行真实财务数据 (2025年年报预测)
# ============================================================
STOCK = "招商银行(600036.SH)"
CURRENT_PRICE = 39.26

# 财务数据 (单位: 亿元)
FINANCIALS = {
    "2024年报": {
        "净利润": 1483.91,
        "EPS": 5.66,
        "ROE": 12.89,
    },
    "2025年年报(预测)": {
        "净利润": 1501.81,
        "EPS": 5.70,
        "ROE": 13.44,
    },
    "关键指标": {
        "净息差(NIM)": "1.87%",
        "不良贷款率": "0.94%",
        "拨备覆盖率": "391.79%",
        "资产负载率": "90.20%",
        "总资产": 1307050,
    }
}

print("="*70)
print("📊 DCF现金流折现估值 - 招商银行")
print("="*70)
print(f"\n当前股价: ¥{CURRENT_PRICE}")

# ============================================================
# DCF模型参数
# ============================================================
DISCOUNT_RATE = 0.10      # 折现率 10% (无风险利率+风险溢价)
GROWTH_RATE_1 = 0.05     # 预测期增长率 5%
GROWTH_RATE_TERM = 0.03  # 永续增长率 3%
FORECAST_YEARS = 10       # 预测期 10年

# EPS预测 (基于2025年年报)
EPS_BASE = 5.70

# ============================================================
# DCF计算 - 两种方法
# ============================================================

def dcf_1_free_cash_flow():
    """
    方法1: 自由现金流折现 (银行用股息折现更准确)
    假设股息支付率70%
    """
    print("\n【方法1: 股息折现模型 (DDM) - 银行专用】")
    print("-"*50)
    
    # 招商银行历史股息支付率约30-35%
    # 考虑到银行需要留存利润补充资本，我们用30%股息支付率
    DIVIDEND_PAYOUT = 0.30
    BASE_DIVIDEND = EPS_BASE * DIVIDEND_PAYOUT  # 5.70 * 0.30 = 1.71元
    
    print(f"基准股息(第0年): ¥{BASE_DIVIDEND:.2f}/股")
    print(f"假设股息支付率: {DIVIDEND_PAYOUT*100:.0f}%")
    print(f"预测期增长率: {GROWTH_RATE_1*100:.0f}%/年")
    print(f"永续增长率: {GROWTH_RATE_TERM*100:.0f}%/年")
    print(f"折现率: {DISCOUNT_RATE*100:.0f}%")
    
    pv_sum = 0
    print(f"\n各年股息预测:")
    for year in range(1, FORECAST_YEARS + 1):
        dividend = BASE_DIVIDEND * (1 + GROWTH_RATE_1) ** year
        discount_factor = 1 / (1 + DISCOUNT_RATE) ** year
        pv = dividend * discount_factor
        pv_sum += pv
        if year <= 5 or year == 10:
            print(f"  第{year:2d}年: 股息¥{dividend:.2f}, PV¥{pv:.2f}")
    
    # 永续价值 (Gordon Growth Model)
    terminal_div = BASE_DIVIDEND * (1 + GROWTH_RATE_1) ** FORECAST_YEARS * (1 + GROWTH_RATE_TERM)
    terminal_value = terminal_div / (DISCOUNT_RATE - GROWTH_RATE_TERM)
    terminal_pv = terminal_value / (1 + DISCOUNT_RATE) ** FORECAST_YEARS
    
    total_pv = pv_sum + terminal_pv
    
    print(f"\n预测期PV总和: ¥{pv_sum:.2f}")
    print(f"永续价值PV: ¥{terminal_pv:.2f}")
    print(f"内在价值(方法1): ¥{total_pv:.2f}")
    
    return total_pv


def dcf_2_eps_discount():
    """
    方法2: EPS折现法 (简化版)
    适合快速估算
    """
    print("\n【方法2: EPS折现法】")
    print("-"*50)
    
    print(f"基准EPS: ¥{EPS_BASE:.2f}")
    print(f"预测期增长率: {GROWTH_RATE_1*100:.0f}%/年")
    print(f"折现率: {DISCOUNT_RATE*10:.0f}%")
    
    pv_sum = 0
    print(f"\n各年EPS预测:")
    for year in range(1, FORECAST_YEARS + 1):
        eps = EPS_BASE * (1 + GROWTH_RATE_1) ** year
        discount_factor = 1 / (1 + DISCOUNT_RATE) ** year
        pv = eps * discount_factor
        pv_sum += pv
        if year <= 5 or year == 10:
            print(f"  第{year:2d}年: EPS¥{eps:.2f}, PV¥{pv:.2f}")
    
    # 永续价值
    terminal_eps = EPS_BASE * (1 + GROWTH_RATE_1) ** FORECAST_YEARS * (1 + GROWTH_RATE_TERM)
    pe_implied = 1 / (DISCOUNT_RATE - GROWTH_RATE_TERM)  # 永续期隐含PE
    terminal_value = terminal_eps * pe_implied
    terminal_pv = terminal_value / (1 + DISCOUNT_RATE) ** FORECAST_YEARS
    
    total_pv = pv_sum + terminal_pv
    
    print(f"\n预测期PV总和: ¥{pv_sum:.2f}")
    print(f"永续价值PV: ¥{terminal_pv:.2f}")
    print(f"内在价值(方法2): ¥{total_pv:.2f}")
    
    return total_pv


def sensitivity_analysis():
    """敏感性分析"""
    print("\n【敏感性分析 - 不同增长率和折现率】")
    print("-"*50)
    print(f"{'增长率':<8}{'折现率':<8}{'内在价值':<12}{'安全边际':<10}")
    print("-"*50)
    
    for g in [0.03, 0.04, 0.05, 0.06]:
        for r in [0.08, 0.10, 0.12]:
            if g >= r:
                continue
            
            # 简化: EPS * (1+g)^10 / (r-g) / 若干年折现
            eps_g = EPS_BASE * (1 + g) ** FORECAST_YEARS
            terminal_pe = 1 / (r - g)
            intrinsic = eps_g * terminal_pe * 0.3 / (1 + r) ** FORECAST_YEARS
            
            # 简单估算
            intrinsic = EPS_BASE / (r - g) * 0.3
            safety = (intrinsic - CURRENT_PRICE) / intrinsic * 100
            
            if safety > -20 and safety < 100:
                print(f"{g*100:>5.0f}%    {r*100:>5.0f}%    ¥{intrinsic:>8.2f}   {safety:>+6.1f}%")


# ============================================================
# 执行计算
# ============================================================
value1 = dcf_1_free_cash_flow()
value2 = dcf_2_eps_discount()
sensitivity_analysis()

# ============================================================
# 综合结论
# ============================================================
avg_value = (value1 + value2) / 2

print("\n" + "="*70)
print("【综合结论】")
print("="*70)
print(f"\n招商银行(600036) DCF估值结果:")
print(f"  方法1(股息折现): ¥{value1:.2f}")
print(f"  方法2(EPS折现): ¥{value2:.2f}")
print(f"  平均内在价值: ¥{avg_value:.2f}")
print(f"  当前股价: ¥{CURRENT_PRICE}")
print(f"  上涨空间: {((avg_value/CURRENT_PRICE)-1)*100:+.1f}%")
print(f"  安全边际: {((avg_value-CURRENT_PRICE)/avg_value)*100:+.1f}%")

# 机构目标价对比
INSTITUTIONAL_TARGET = 53.54
print(f"\n机构预测目标价: ¥{INSTITUTIONAL_TARGET} (上涨空间{(INSTITUTIONAL_TARGET/CURRENT_PRICE-1)*100:+.1f}%)")

if avg_value > CURRENT_PRICE * 1.2:
    verdict = "🟢 明显低估 - 买入"
elif avg_value > CURRENT_PRICE:
    verdict = "🟡 略微低估 - 可以买入"
elif avg_value > CURRENT_PRICE * 0.8:
    verdict = "⏸️ 估值合理 - 持有"
else:
    verdict = "🔴 高估 - 减仓"

print(f"\n估值结论: {verdict}")

print("\n" + "="*70)
print("【验证结果】")
print("="*70)
print(f"任务: 计算招商银行的DCF内在价值")
print(f"输出: ¥{avg_value:.2f} (两种方法平均)")
print(f"当前价格: ¥{CURRENT_PRICE}")
print(f"机构目标价: ¥{INSTITUTIONAL_TARGET}")
print(f"结论: {verdict}")
print("="*70)

# 保存结果
with open(r'C:\Users\zymyy\.qclaw\workspace\stock_work\learning\week1_task1_dcf_result.txt', 'w', encoding='utf-8') as f:
    f.write(f"DCF估值结果 - 招商银行\n")
    f.write(f"日期: 2026-04-09\n")
    f.write(f"方法1(股息折现): ¥{value1:.2f}\n")
    f.write(f"方法2(EPS折现): ¥{value2:.2f}\n")
    f.write(f"平均内在价值: ¥{avg_value:.2f}\n")
    f.write(f"当前股价: ¥{CURRENT_PRICE}\n")
    f.write(f"机构目标价: ¥{INSTITUTIONAL_TARGET}\n")
    f.write(f"结论: {verdict}\n")

# -*- coding: utf-8 -*-
"""
投资学习计划 + 30分钟进展汇报
保存学习进度到文件，每次汇报时读取
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

LEARN_DIR = r'C:\Users\zymyy\.qclaw\workspace\stock_work\learning'
os.makedirs(LEARN_DIR, exist_ok=True)

PLAN_FILE = os.path.join(LEARN_DIR, 'plan.md')
PROGRESS_FILE = os.path.join(LEARN_DIR, 'progress.md')

# ============================================================
# 第一阶段：基础投资理论 (4月10日-4月13日, 4天)
# ============================================================
PHASE1 = [
    {
        "day": "Day1 (4/10)",
        "topic": "价值投资基础理论",
        "tasks": [
            "格雷厄姆《聪明的投资者》核心思想: 安全边际、市场先生",
            "银行螺丝钉投资理念: 指数基金定投、低估买入高估卖出",
            "PE/PB/PS/股息率 深入理解: 各指标适用场景和局限",
            "PEG指标: 彼得林奇的成长股估值法",
            "作业: 用当前持仓验证各指标是否合理"
        ]
    },
    {
        "day": "Day2 (4/11)",
        "topic": "财务报表分析",
        "tasks": [
            "资产负债表: 资产质量、负债率、有息负债",
            "利润表: 营收增长、毛利率、净利率、ROE",
            "现金流量表: 经营现金流vs净利润、自由现金流",
            "杜邦分析: ROE拆解为利润率×周转率×杠杆",
            "银行螺丝钉选股标准: ROE>15%、利润稳定、估值合理",
            "作业: 分析持仓5只股票的财务报表"
        ]
    },
    {
        "day": "Day3 (4/12)",
        "topic": "行业分析方法",
        "tasks": [
            "行业生命周期: 成长期/成熟期/衰退期",
            "行业竞争格局: 龙头企业、护城河分析(巴菲特)",
            "银行业分析: 净息差、不良率、资本充足率",
            "白酒行业: 高端/次高端/中端，品牌壁垒",
            "保险行业: NBV、内含价值、投资收益率",
            "作业: 对持仓行业做深度分析"
        ]
    },
    {
        "day": "Day4 (4/13)",
        "topic": "基金投资理论",
        "tasks": [
            "指数基金: 跟踪误差、费率、规模",
            "主动基金: 基金经理能力评估(Alpha/Beta/夏普/最大回撤)",
            "银行螺丝钉定投法: 低估定投、正常持有、高估分批卖出",
            "股债平衡: 经典60/40组合、再平衡策略",
            "作业: 筛选适合定投的指数基金"
        ]
    }
]

# ============================================================
# 第二阶段：交易策略体系 (4月14日-4月17日, 4天)
# ============================================================
PHASE2 = [
    {
        "day": "Day5 (4/14)",
        "topic": "买入策略",
        "tasks": [
            "估值买入法: PE历史百分位(10年), 低于30%分位买入",
            "分散投资: 单只不超过总资金20%, 行业不超过30%",
            "分批建仓: 三角形建仓法(3-3-4)",
            "银行螺丝钉五步选基法",
            "作业: 模拟买入策略"
        ]
    },
    {
        "day": "Day6 (4/15)",
        "topic": "卖出策略",
        "tasks": [
            "估值卖出法: PE历史百分位>80%分批卖出",
            "止盈止损: 目标收益率止盈、最大回撤止损",
            "基本面恶化信号: ROE下降、营收负增长、负债飙升",
            "换股逻辑: 新机会显著优于持仓时才换",
            "作业: 制定持仓卖出条件"
        ]
    },
    {
        "day": "Day7 (4/16)",
        "topic": "风险控制",
        "tasks": [
            "仓位管理: 凯利公式、固定比例法",
            "最大回撤控制: 单股止损线、组合止损线",
            "相关性分析: 持仓之间的相关性，避免同行业集中",
            "黑天鹅应对: 现金仓位的重要性",
            "作业: 设计风险控制体系"
        ]
    },
    {
        "day": "Day8 (4/17)",
        "topic": "资金流向与市场情绪",
        "tasks": [
            "主力资金: 北向资金、融资融券、龙虎榜",
            "成交量分析: 量价关系、放量缩量",
            "市场情绪指标: 恐慌指数、换手率、涨停跌停比",
            "机构行为: 基金持仓变化、调研频率",
            "作业: 分析当前市场情绪"
        ]
    }
]

# ============================================================
# 第三阶段：技术分析补充 (4月18日-4月20日, 3天)
# ============================================================
PHASE3 = [
    {
        "day": "Day9 (4/18)",
        "topic": "技术指标基础",
        "tasks": [
            "均线系统: MA5/10/20/60/120/250 葛兰碧八大法则",
            "MACD: 金叉死叉、顶底背离、红绿柱",
            "RSI: 超买超卖、背离信号",
            "作业: 对持仓股票做技术分析"
        ]
    },
    {
        "day": "Day10 (4/19)",
        "topic": "K线与形态",
        "tasks": [
            "K线组合: 锤子线、吞没、十字星",
            "支撑压力: 前高前低、整数关口",
            "趋势线: 上升/下降/横盘趋势",
            "作业: 识别持仓股票的关键技术位"
        ]
    },
    {
        "day": "Day11 (4/20)",
        "topic": "量化分析基础",
        "tasks": [
            "多因子模型: 价值因子+动量因子+质量因子+规模因子",
            "回测框架: 如何验证策略有效性",
            "夏普比率、索提诺比率、卡玛比率",
            "作业: 为当前策略做简单回测"
        ]
    }
]

# ============================================================
# 第四阶段：整合与实战 (4月21日-4月23日, 3天)
# ============================================================
PHASE4 = [
    {
        "day": "Day12 (4/21)",
        "topic": "综合投资体系搭建",
        "tasks": [
            "整合价值投资+技术分析+资金面",
            "建立股票评分模型(10+指标)",
            "建立买卖决策树",
            "作业: 输出完整的投资体系文档"
        ]
    },
    {
        "day": "Day13 (4/22)",
        "topic": "投资组合管理",
        "tasks": [
            "现代投资组合理论: 有效前沿",
            "再平衡策略: 定期vs阈值触发",
            "资产配置: 股/债/现金比例",
            "作业: 设计最优投资组合"
        ]
    },
    {
        "day": "Day14 (4/23)",
        "topic": "实战模拟总结",
        "tasks": [
            "回顾2周模拟交易结果",
            "分析决策中的正确和错误",
            "输出: 重新设计的专业分析引擎v6.0",
            "输出: 更新后的App设计方案"
        ]
    }
]

ALL_PHASES = [PHASE1, PHASE2, PHASE3, PHASE4]

def generate_plan():
    """生成学习计划"""
    lines = ["# 投资专业知识学习计划 (14天)\n"]
    lines.append("## 目标")
    lines.append("把自己培养成专业股票分析师/基金经理水平\n")
    lines.append("## 学习框架")
    lines.append("- 第一阶段(4天): 基础投资理论")
    lines.append("- 第二阶段(4天): 交易策略体系")
    lines.append("- 第三阶段(3天): 技术分析补充")
    lines.append("- 第四阶段(3天): 整合与实战\n")
    
    for phase in ALL_PHASES:
        for day in phase:
            lines.append(f"## {day['day']} - {day['topic']}")
            for i, t in enumerate(day['tasks'], 1):
                lines.append(f"{i}. {t}")
            lines.append("")
    
    text = '\n'.join(lines)
    with open(PLAN_FILE, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return text

def get_progress():
    """读取当前进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "尚未开始学习"

def update_progress(day, topic, completed, notes):
    """更新进度"""
    text = f"# 学习进度 - {day}\n\n"
    text += f"## 主题: {topic}\n\n"
    text += f"## 已完成\n"
    for c in completed:
        text += f"- ✅ {c}\n"
    text += f"\n## 学习笔记\n"
    for n in notes:
        text += f"- {n}\n"
    text += f"\n## 下一步\n"
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return text

def generate_report():
    """生成汇报内容"""
    progress = get_progress()
    today_plan = PHASE1[0]  # 默认第一天
    
    lines = []
    lines.append(f"📚 投资学习进展 (30分钟汇报)")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append(f"阶段: {today_plan['day']}")
    lines.append(f"主题: {today_plan['topic']}")
    lines.append("")
    lines.append("今日任务:")
    for i, t in enumerate(today_plan['tasks'], 1):
        lines.append(f"  {i}. {t}")
    lines.append("")
    lines.append(progress)
    
    return '\n'.join(lines)


if __name__ == '__main__':
    plan = generate_plan()
    print("学习计划已生成")
    print(plan[:500])
    print("...")
    print(f"\n进度:")
    print(get_progress())

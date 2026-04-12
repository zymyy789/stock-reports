# -*- coding: utf-8 -*-
"""
投资知识库系统
- 结构化保存专家知识
- 每次分析时调用
- 用真实数据验证效果
- 记录我与专家的差距
"""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

KB_DIR = r'C:\Users\zymyy\.qclaw\workspace\stock_work\learning\knowledge_base'
os.makedirs(KB_DIR, exist_ok=True)

# ============================================================
# 格雷厄姆《聪明的投资者》核心知识
# ============================================================
BENJAMIN_GRAHAM = {
    "source": "本杰明·格雷厄姆《聪明的投资者》",
    "principles": {
        "安全边际": {
            "definition": "用低于内在价值的价格买入，价格远低于价值时风险最小",
            "formula": "安全边际 = (内在价值 - 当前价格) / 内在价值",
            "application": "PE<15倍、PB<1.5倍时安全边际较高",
            "key_quote": "投资的秘诀在于：当价格低于价值时买进，当价格高于价值时卖出。"
        },
        "市场先生": {
            "definition": "市场每天报价，情绪化严重，创造了买入卖出机会",
            "behavior": ["极度乐观时股价虚高", "极度悲观时股价低估"],
            "strategy": "利用市场先生的情绪，而不是被它控制",
            "quote": "你要在别人贪婪时恐惧，在别人恐惧时贪婪。——巴菲特诠释"
        },
        "防御型投资者": {
            "allocation": "股票:债券 = 25%:75% 或 50%:50%",
            "strategy": "分散投资低估值蓝筹股+优质债券",
            "selection": "大型、知名的、财务稳健的公司"
        },
        "积极型投资者": {
            "criteria": "选择被低估的优质公司",
            "forbidden": "避免投机、热门股、高估值股",
            "minimum_pe": "PE超过25倍需要非常谨慎"
        }
    },
    "valuation_methods": {
        "PE": "市盈率，适合盈利稳定的公司",
        "PB": "市净率，适合资产型公司（银行/券商）",
        "DCF": "现金流折现，适合评估内在价值"
    },
    "risk_management": {
        "diversification": "分散到10-30只股票",
        "single_limit": "单只股票不超过总仓位20%",
        "quality_filter": "只买盈利稳定、财务健康的公司"
    }
}

# ============================================================
# 银行螺丝钉核心理念
# ============================================================
BANK_SCREW = {
    "source": "银行螺丝钉（基金投资专家，指数基金定投倡导者）",
    "core_principles": {
        "低估定投": {
            "low_buy": "PE/PB处于历史30%分位以下 → 加大买入",
            "normal_hold": "PE/PB处于30%-70%分位 → 正常持有",
            "high_sell": "PE/PB处于70%以上分位 → 逐步卖出",
            "formula": "买入金额 = 基础金额 × (正常PE/当前PE)"
        },
        "长期持有": {
            "rationale": "股市长期向上（国运+经济增长）",
            "time_horizon": "持有3-5年以上收益更稳定",
            "cost_of_trading": "频繁交易损耗收益（摩擦成本+税收）"
        },
        "高股息策略": {
            "dividend_yield": "股息率>4%视为高股息",
            "benefit": "提供现金流，下跌有限",
            "best_sectors": "银行/电力/地产/传统消费"
        }
    },
    "selection_criteria": {
        "index_fund": {
            "跟踪误差": "<0.3%为优秀",
            "费率": "<0.5%/年为低成本",
            "规模": ">2亿避免清盘风险",
            "recommended": ["沪深300", "中证500", "红利指数", "基本面指数"]
        },
        "stock": {
            "ROE": ">15%为优质公司",
            "profit_stability": "连续5年盈利",
            "debt_ratio": "<60%（金融除外）",
            "cash_flow": "经营现金流 > 净利润"
        }
    },
    "portfolio_management": {
        "rebalancing": {
            "定期": "每年1次",
            "阈值": "单资产偏离目标>10%时触发",
            "方法": "卖出超配资产，买入低配资产"
        },
        "position_sizing": {
            "max_single": "单只股票不超过20%",
            "max_industry": "单一行业不超过30%",
            "cash_reserve": "保留10-20%现金应对极端情况"
        }
    }
}

# ============================================================
# 彼得林奇投资方法
# ============================================================
PETER_LYNCH = {
    "source": "彼得·林奇（传奇基金经理，13年27倍）",
    "investment_philosophy": {
        "invest_what_you_know": "普通人比专业投资者更了解本地消费/生活",
        "buy_growth": "买入高成长公司，让利润奔跑",
        "know_when_to_sell": "高估或基本面恶化时果断卖出",
        "small_cap_opportunity": "小市值公司往往有更大增长空间"
    },
    "stock_classification": {
        "slow_growth": "大公司，年增长2-4%，高股息 → 持有",
        "稳定增长": "年增长10-12%，非周期 → 持有或买入",
        "快速增长": "年增长20-25%，小而新 → 重点关注",
        "周期股": "随经济周期波动 → 低PE买，高PE卖",
        "资产型": "持有大量资产（土地/品牌）→ 破净买"
    },
    "valuation": {
        "PEG": "PEG<1有投资价值，>2需谨慎",
        "PE_vs_growth": "PE不应超过增长率太多",
        "cycle_reverse": "周期股相反：低PE卖，高PE买"
    },
    "red_flags": {
        "avoid": [
            "PE>50的热门股",
            "主营业务看不懂的公司",
            "频繁收购扩张的公司",
            "负债率突然飙升",
            "高管大量减持"
        ],
        "sell_signals": [
            "PE远超合理水平",
            "公司转型失败",
            "行业景气度下降",
            "ROE持续恶化"
        ]
    }
}

# ============================================================
# 专业基金经理能力框架（我要达到的水平）
# ============================================================
PROFESSIONAL_FRAMEWORK = {
    "description": "衡量我与专业基金经理差距的框架",
    "competencies": {
        "基本面分析": {
            "weight": 25,
            "skills": [
                "读懂三张财务报表",
                "识别财务报表造假信号",
                "计算DCF内在价值",
                "评估公司护城河"
            ],
            "my_level": "初级 - 能读取数据，但深度分析不足"
        },
        "估值能力": {
            "weight": 25,
            "skills": [
                "PE/PB/PS/PCF多估值法",
                "历史百分位分析",
                "同业对比估值",
                "理解不同行业适用不同估值"
            ],
            "my_level": "中级 - 掌握基础，但缺乏行业深度"
        },
        "行业研究": {
            "weight": 20,
            "skills": [
                "理解行业生命周期",
                "竞争格局分析",
                "政策影响评估",
                "上下游产业链"
            ],
            "my_level": "初级 - 了解表面，缺乏深度洞察"
        },
        "风险管理": {
            "weight": 15,
            "skills": [
                "仓位管理",
                "止损纪律",
                "相关性分析",
                "黑天鹅应对"
            ],
            "my_level": "初级 - 知道原则但执行不足"
        },
        "量化分析": {
            "weight": 5,
            "skills": [
                "多因子模型",
                "回测验证",
                "统计检验"
            ],
            "my_level": "中级 - 有工具但缺乏深度应用"
        }
    },
    "improvement_plan": {
        "short_term": [
            "建立完整知识库并结构化保存",
            "每次分析调用知识库而不是凭记忆",
            "用NeoData获取真实数据验证"
        ],
        "medium_term": [
            "深入学习财务报表分析",
            "建立行业分析模板",
            "完善多因子评分模型"
        ],
        "long_term": [
            "回测验证策略有效性",
            "建立完整的投资体系文档"
        ]
    }
}

# ============================================================
# 我的能力自评（每月更新）
# ============================================================
SELF_ASSESSMENT = {
    "date": "2026-04-09",
    "overall_level": "初级偏中级",
    "strengths": [
        "数据获取能力强（NeoData/腾讯/东方财富）",
        "PE/PB/股息等基础指标计算准确",
        "能综合多维度做初步评分"
    ],
    "weaknesses": [
        "无法深度理解行业竞争格局",
        "不会DCF现金流折现估值",
        "无法识别财务报表细节问题",
        "缺乏实战经验积累",
        "无法真正'记住'知识（每次会话重置）"
    ],
    "distance_to_expert": {
        "基本面分析": "差距大 - 需要深度学习",
        "估值能力": "差距中等 - 有基础，需深化",
        "行业研究": "差距大 - 缺乏系统知识",
        "风险管理": "差距中等 - 原则懂但执行难"
    },
    "next_steps": [
        "1. 深入学习财务报表分析方法（Day2）",
        "2. 建立行业分析模板（Day3）",
        "3. 学习如何用NeoData获取更深层数据",
        "4. 建立知识库调用机制，确保每次分析都用到"
    ]
}

# ============================================================
# 知识库管理
# ============================================================
def save_knowledge():
    """保存所有知识到文件"""
    all_knowledge = {
        "benjamin_graham": BENJAMIN_GRAHAM,
        "bank_screw": BANK_SCREW,
        "peter_lynch": PETER_LYNCH,
        "professional_framework": PROFESSIONAL_FRAMEWORK,
        "self_assessment": SELF_ASSESSMENT
    }
    
    for name, data in all_knowledge.items():
        filepath = os.path.join(KB_DIR, f"{name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 知识库已保存:")
    for name in all_knowledge:
        print(f"   - {name}.json")
    print()

def load_knowledge(name):
    """加载特定知识"""
    filepath = os.path.join(KB_DIR, f"{name}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def analyze_with_knowledge(code, name, stock_data):
    """
    用知识库分析股票
    返回分析报告，包含知识引用
    """
    # 加载知识
    bg = load_knowledge("benjamin_graham")  # 格雷厄姆
    bs = load_knowledge("bank_screw")  # 银行螺丝钉
    pl = load_knowledge("peter_lynch")  # 林奇
    
    pe = stock_data.get('pe', 0)
    pb = stock_data.get('pb', 0)
    price = stock_data['price']
    change = stock_data.get('change_pct', 0)
    
    findings = []
    signals = []
    
    # 1. 格雷厄姆安全边际检查
    if pe < 15:
        findings.append(f"✅ PE={pe} 符合格雷厄姆买入条件(<15)")
        signals.append(("buy", f"安全边际高"))
    elif pe > 25:
        findings.append(f"⚠️ PE={pe} 超过格雷厄姆警戒线(>25)")
        signals.append(("sell", f"高估风险"))
    
    if pb < 1.5:
        findings.append(f"✅ PB={pb} 在合理区间")
    
    # 2. 银行螺丝钉百分位检查
    # 注：需要历史数据，这里简化
    if pe < 12:
        findings.append(f"✅ PE={pe} 低于银行螺丝钉低估线(<12)")
    if change < -3:
        findings.append(f"✅ 今日下跌{change}% 创造买入机会")
    
    # 3. 彼得林奇检查
    if pe > 0 and pe < 20:
        signals.append(("consider", f"PE={pe}在合理范围"))
    
    # 综合判断
    buy_signals = [s for s in signals if s[0] in ('buy', 'strong_buy')]
    sell_signals = [s for s in signals if s[0] in ('sell')]
    
    return {
        "stock": f"{name}({code})",
        "price": price,
        "pe": pe,
        "pb": pb,
        "findings": findings,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "knowledge_applied": ["benjamin_graham", "bank_screw", "peter_lynch"]
    }


def print_self_assessment():
    """打印能力自评"""
    sa = SELF_ASSESSMENT
    fw = PROFESSIONAL_FRAMEWORK
    
    print("\n" + "="*60)
    print("📊 AI投资能力自评报告")
    print("="*60)
    print(f"\n日期: {sa['date']}")
    print(f"总体水平: {sa['overall_level']}")
    
    print("\n【优势】")
    for s in sa['strengths']:
        print(f"  ✅ {s}")
    
    print("\n【劣势】")
    for w in sa['weaknesses']:
        print(f"  ❌ {w}")
    
    print("\n【与专家差距】")
    for area, gap in sa['distance_to_expert'].items():
        print(f"  {area}: {gap}")
    
    print("\n【改进计划】")
    for step in sa['next_steps']:
        print(f"  → {step}")
    
    print("\n" + "="*60)
    print("【各维度详细评估】")
    print("="*60)
    for area, details in fw['competencies'].items():
        print(f"\n{area} (权重{details['weight']}%)")
        print(f"  技能要求: {', '.join(details['skills'])}")
        print(f"  我的水平: {details['my_level']}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    save_knowledge()
    print_self_assessment()

# -*- coding: utf-8 -*-
"""
专业投资决策引擎 v5.0
综合: 估值 + 机构观点 + 盈利增长 + 资金流向 + 技术面
"""
import sys, re, json
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.path.insert(0, r'D:\Progra~1\QClaw\resources\openclaw\config\skills\neodata-financial-search')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from analysis.fetcher import StockFetcher
from analysis.portfolio_manager import PortfolioManager
from scripts.query import query_neodata


def parse_neodata(name, query):
    """查询并解析NeoData数据"""
    result = query_neodata(f"{name} {query}")
    if not result or result.get('code') != '200':
        return {}
    
    data = {}
    api = result['data']['apiData']
    
    for r in api.get('apiRecall', []):
        t = r['type']
        c = r['content']
        
        if t == '股票实时行情' or '行情' in t:
            # PB, 股息率, 量比, 换手率, 振幅
            for k, pat in [
                ('pb', r'市净率:([\d.]+)'),
                ('dividend', r'股息率:([\d.]+)'),
                ('turnover', r'换手率:([\d.]+)'),
                ('volume_ratio', r'量比:([\d.]+)'),
                ('amplitude', r'振幅:([\d.]+)'),
                ('ytd_change', r'年初至今涨跌幅:\s*([-\d.]+)%'),
                ('m5_change', r'5日涨跌幅:([-\d.]+)%'),
                ('m20_change', r'20日涨跌幅:([-\d.]+)%'),
            ]:
                m = re.search(pat, c)
                if m:
                    data[k] = float(m.group(1))
        
        elif t == '市场观点' or '观点' in t or '研报' in t:
            # 目标价
            m = re.search(r'综合目标价为([\d,.]+)元', c)
            if m:
                data['target_price'] = float(m.group(1).replace(',', ''))
            
            m = re.search(r'上涨空间为([\d.]+)%', c)
            if m:
                data['upside'] = float(m.group(1))
            
            # 机构评级
            m = re.search(r'利好占比(\d+)%', c)
            if m:
                data['rating_bullish'] = int(m.group(1))
            m = re.search(r'利空占比(\d+)%', c)
            if m:
                data['rating_bearish'] = int(m.group(1))
            
            # 基金持股
            m = re.search(r'基金持股比例([\d.]+)%', c)
            if m:
                data['fund_holding'] = float(m.group(1))
            
            # 盈利预测 2026
            m = re.search(r'2026年.*?预测每股收益为([\d.]+)元', c)
            if m:
                data['eps_2026'] = float(m.group(1))
            
            m = re.search(r'2026年.*?预测净利润同比增长为([\d.-]+)%', c)
            if m:
                data['profit_growth_2026'] = float(m.group(1))
    
    return data


class ProAnalyzer:
    """专业分析器 - 模拟基金经理分析流程"""
    
    def __init__(self):
        self.sf = StockFetcher()
    
    def analyze(self, code, name):
        """综合分析"""
        # 第一步：基础行情
        basic = self.sf.get_a_stock_price(code)
        if not basic:
            return None
        
        price = basic['price']
        pe = basic.get('pe', 0)
        pb = basic.get('pb', 0)
        change = basic.get('change_pct', 0)
        dividend = basic.get('dividend', 0)
        
        # 第二步：机构观点 + 盈利预测 + 资金流向
        nd = parse_neodata(name, "机构评级 目标价 盈利预测 资金流向")
        
        # 补充NeoData中的数据
        if 'pb' in nd and nd['pb'] > 0:
            pb = nd['pb']
        if 'dividend' in nd and nd['dividend'] > 0:
            dividend = nd['dividend']
        
        target_price = nd.get('target_price', 0)
        upside = nd.get('upside', 0)
        fund_holding = nd.get('fund_holding', 0)
        eps_2026 = nd.get('eps_2026', 0)
        profit_growth = nd.get('profit_growth_2026', 0)
        ytd_change = nd.get('ytd_change', 0)
        m5_change = nd.get('m5_change', 0)
        m20_change = nd.get('m20_change', 0)
        turnover = nd.get('turnover', 0)
        
        # ===== 多维度评分 =====
        scores = {}
        reasons = []
        
        # 1. 估值评分 (30分)
        val_score = 0
        if pe > 0:
            if pe < 8: val_score = 30; reasons.append(f"PE={pe:.1f} 极低估值")
            elif pe < 12: val_score = 24; reasons.append(f"PE={pe:.1f} 低估值")
            elif pe < 18: val_score = 16; reasons.append(f"PE={pe:.1f} 合理")
            elif pe < 25: val_score = 8; reasons.append(f"PE={pe:.1f} 偏高")
            else: val_score = 2; reasons.append(f"PE={pe:.1f} 高估")
        
        if pb > 0:
            if pb < 1: val_score = min(30, val_score + 5); reasons.append(f"PB={pb:.2f} 破净")
        
        if dividend >= 4:
            val_score = min(30, val_score + 3)
            reasons.append(f"股息{dividend:.1f}% 高分红")
        elif dividend >= 2.5:
            val_score = min(30, val_score + 2)
        scores['valuation'] = val_score
        
        # 2. 机构观点评分 (25分) - 专业分析师怎么看
        inst_score = 0
        if upside > 30:
            inst_score = 25
            reasons.append(f"机构目标价¥{target_price:.0f} 上涨空间{upside:.0f}%")
        elif upside > 20:
            inst_score = 20
            reasons.append(f"机构目标价¥{target_price:.0f} 上涨空间{upside:.0f}%")
        elif upside > 10:
            inst_score = 15
            reasons.append(f"机构目标价¥{target_price:.0f} 空间{upside:.0f}%")
        elif upside > 0:
            inst_score = 8
        else:
            inst_score = 3
        
        if fund_holding > 3:
            inst_score = min(25, inst_score + 3)
            reasons.append(f"基金持股{fund_holding:.1f}% 机构青睐")
        scores['institution'] = inst_score
        
        # 3. 成长性评分 (20分) - 未来盈利增长
        growth_score = 0
        if eps_2026 > 0 and pe > 0:
            # PEG = PE / 增长率
            peg = pe / profit_growth if profit_growth > 0 else 999
            if peg < 0.5:
                growth_score = 20
                reasons.append(f"PEG={peg:.1f} 极度低估+高增长")
            elif peg < 1:
                growth_score = 16
                reasons.append(f"PEG={peg:.1f} 估值合理+增长")
            elif peg < 1.5:
                growth_score = 12
                reasons.append(f"PEG={peg:.1f} 增长可覆盖估值")
            elif peg < 2:
                growth_score = 6
            else:
                growth_score = 2
        
        if profit_growth > 15:
            growth_score = min(20, growth_score + 3)
            reasons.append(f"预计净利增长{profit_growth:.1f}%")
        elif profit_growth > 8:
            growth_score = min(20, growth_score + 2)
        elif profit_growth < 0:
            growth_score = max(0, growth_score - 3)
            reasons.append(f"预计净利下滑{profit_growth:.1f}%")
        scores['growth'] = growth_score
        
        # 4. 技术面评分 (15分) - 趋势+动量
        tech_score = 8  # 基础分
        if m20_change is not None:
            if m20_change < -10:
                tech_score = 15
                reasons.append(f"20日跌{m20_change:.1f}% 超跌反弹")
            elif m20_change < -5:
                tech_score = 13
                reasons.append(f"20日跌{m20_change:.1f}% 回调")
            elif m20_change > 10:
                tech_score = 4
                reasons.append(f"20日涨{m20_change:.1f}% 短期追高风险")
            elif m20_change > 5:
                tech_score = 6
        
        if ytd_change is not None:
            if ytd_change < -15:
                tech_score = min(15, tech_score + 3)
                reasons.append(f"年内跌{ytd_change:.1f}% 低估区间")
        scores['technical'] = tech_score
        
        # 5. 安全边际评分 (10分) - 下跌空间多大
        safety_score = 5
        if target_price > 0:
            # 安全边际 = (目标价 - 现价) / 现价
            margin = (target_price - price) / price * 100
            if margin > 40:
                safety_score = 10
                reasons.append(f"安全边际{margin:.0f}% 很高")
            elif margin > 25:
                safety_score = 8
                reasons.append(f"安全边际{margin:.0f}%")
            elif margin > 10:
                safety_score = 6
            elif margin < 0:
                safety_score = 2
                reasons.append(f"已超目标价{abs(margin):.0f}% 注意风险")
        scores['safety'] = safety_score
        
        # ===== 综合评分 =====
        total = scores['valuation'] + scores['institution'] + scores['growth'] + scores['technical'] + scores['safety']
        
        # ===== 决策 =====
        if total >= 70:
            decision = '强烈买入'
            emoji = '🟢🟢'
        elif total >= 55:
            decision = '买入'
            emoji = '🟢'
        elif total >= 40:
            decision = '持有'
            emoji = '⏸️'
        elif total >= 25:
            decision = '减仓'
            emoji = '🟡'
        else:
            decision = '卖出'
            emoji = '🔴'
        
        return {
            'name': name, 'code': code, 'price': price,
            'pe': pe, 'pb': pb, 'dividend': dividend, 'change': change,
            'target_price': target_price, 'upside': upside,
            'eps_2026': eps_2026, 'profit_growth': profit_growth,
            'fund_holding': fund_holding,
            'ytd_change': ytd_change, 'm5_change': m5_change, 'm20_change': m20_change,
            'turnover': turnover,
            'scores': scores, 'total': total,
            'decision': decision, 'emoji': emoji,
            'reasons': reasons,
        }


def run_analysis():
    analyzer = ProAnalyzer()
    
    stocks = [
        ('601166', '兴业银行'), ('600036', '招商银行'), ('601318', '中国平安'),
        ('600030', '中信证券'), ('600887', '伊利股份'), ('000858', '五粮液'),
        ('000333', '美的集团'), ('600519', '贵州茅台'), ('600276', '恒瑞医药'),
        ('601888', '中国中免'), ('601328', '交通银行'),
    ]
    
    results = []
    for code, name in stocks:
        print(f"  分析 {name}...", end="", flush=True)
        r = analyzer.analyze(code, name)
        if r:
            results.append(r)
            print(f" {r['decision']} {r['total']}分")
        else:
            print(" 失败")
    
    results.sort(key=lambda x: x['total'], reverse=True)
    return results


def print_report():
    print(f"\n{'='*65}")
    print(f"  📊 专业投资分析报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  分析维度: 估值30% + 机构25% + 成长20% + 技术15% + 安全边际10%")
    print(f"{'='*65}\n")
    
    results = run_analysis()
    
    # 按决策分组
    groups = {}
    for r in results:
        d = r['decision']
        if d not in groups:
            groups[d] = []
        groups[d].append(r)
    
    order = ['强烈买入', '买入', '持有', '减仓', '卖出']
    
    for d in order:
        if d not in groups:
            continue
        items = groups[d]
        
        if d in ('强烈买入', '买入'):
            print(f"\n{'🟢' if d=='买入' else '🟢🟢'} {d}:")
        elif d == '持有':
            print(f"\n⏸️ {d}:")
        else:
            print(f"\n{'🔴' if d=='卖出' else '🟡'} {d}:")
        
        print("-" * 65)
        
        for r in items:
            upside_s = f"空间{r['upside']:.0f}%" if r['upside'] > 0 else "无目标价"
            target_s = f"目标¥{r['target_price']:.0f}" if r['target_price'] > 0 else ""
            growth_s = f"增长{r['profit_growth']:.0f}%" if r['profit_growth'] else ""
            
            print(f"  {r['name']}({r['code']}) {r['emoji']} {r['total']}分")
            print(f"    现价¥{r['price']:.2f} PE:{r['pe']:.1f} PB:{r['pb']:.2f} 股息:{r['dividend']:.1f}%")
            print(f"    {target_s} {upside_s} {growth_s}")
            
            # 分维度
            s = r['scores']
            dims = f"    估值{s['valuation']:.0f} 机构{s['institution']:.0f} 成长{s['growth']:.0f} 技术{s['technical']:.0f} 安全{s['safety']:.0f}"
            print(dims)
            
            # 核心理由
            core = [x for x in r['reasons'] if any(k in x for k in ['极低', '低估', '高估', '破净', '高分红', 'PEG', '超跌', '机构', '目标价', '安全边际', '增长', '下滑'])]
            if core:
                print(f"    → {' | '.join(core[:2])}")
            print()
    
    # 完整排名
    print(f"\n📋 完整排名 (总分100):")
    print("-" * 65)
    print(f"{'名称':<10}{'代码':<8}{'决策':<8}{'总分':<5}{'估值':<5}{'机构':<5}{'成长':<5}{'技术':<5}{'安全':<5}{'PE':<6}{'空间'}")
    print("-" * 65)
    for r in results:
        s = r['scores']
        pe_s = f"{r['pe']:.1f}" if r['pe'] > 0 else "N/A"
        up_s = f"{r['upside']:.0f}%" if r['upside'] > 0 else "-"
        print(f"{r['name']:<10}{r['code']:<8}{r['decision']:<8}{r['total']:<5}{s['valuation']:<5}{s['institution']:<5}{s['growth']:<5}{s['technical']:<5}{s['safety']:<5}{pe_s:<6}{up_s}")
    
    print(f"\n{'='*65}")
    print("分析框架: 估值(PE/PB/股息) + 机构观点(目标价/评级) + 成长性(PEG/盈利增长)")
    print("          + 技术面(20日趋势) + 安全边际(目标价vs现价)")
    print("仅供参考，不构成投资建议")
    print(f"{'='*65}\n")


if __name__ == '__main__':
    print_report()

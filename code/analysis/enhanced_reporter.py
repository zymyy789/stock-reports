"""
增强版报告生成模块 - 生成详细的分析报告
"""
import os
from datetime import datetime
from typing import List, Dict
import json
from config import REPORT_DIR, INITIAL_CAPITAL
from analysis.risk_analyzer import format_risk_for_report


def fmt_num(val, decimals=2):
    """安全格式化数字"""
    if val is None:
        return 'N/A'
    try:
        return f"{float(val):.{decimals}f}"
    except:
        return 'N/A'


class EnhancedReportGenerator:
    """增强版报告生成器"""
    
    def __init__(self, report_dir: str = REPORT_DIR):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
    
    def generate_full_report(self, 
                           market_data: Dict,
                           stock_recommendations: List[Dict],
                           fund_recommendations: List[Dict],
                           portfolio_summary: List[Dict],
                           portfolio_value: float,
                           historical_analysis: Dict = None) -> str:
        """生成完整分析报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        profit = portfolio_value - INITIAL_CAPITAL
        profit_pct = (profit / INITIAL_CAPITAL * 100) if INITIAL_CAPITAL > 0 else 0
        
        report = f"""# 📊 智能投资分析报告

**报告日期**: {date}  
**生成时间**: {now}  
**系统状态**: ✅ 运行正常

---

## 📈 市场全景

### A股市场
| 指数名称 | 最新点位 | 涨跌幅 | 市场判断 |
|----------|----------|--------|----------|
| 上证指数 | {fmt_num(market_data.get('shanghai', {}).get('price'))} | {fmt_num(market_data.get('shanghai', {}).get('change_pct'))}% | {self._judge_market(market_data.get('shanghai', {}).get('change_pct', 0))} |
| 深证成指 | {fmt_num(market_data.get('shenzhen', {}).get('price'))} | {fmt_num(market_data.get('shenzhen', {}).get('change_pct'))}% | {self._judge_market(market_data.get('shenzhen', {}).get('change_pct', 0))} |

### 港股市场
| 指数名称 | 最新点位 | 涨跌幅 | 市场判断 |
|----------|----------|--------|----------|
| 恒生指数 | {fmt_num(market_data.get('hsi', {}).get('price'))} | {fmt_num(market_data.get('hsi', {}).get('change_pct'))}% | {self._judge_market(market_data.get('hsi', {}).get('change_pct', 0))} |
| 国企指数 | {fmt_num(market_data.get('hscei', {}).get('price'))} | {fmt_num(market_data.get('hscei', {}).get('change_pct'))}% | {self._judge_market(market_data.get('hscei', {}).get('change_pct', 0))} |

### 美股市场
| 指数名称 | 最新点位 | 涨跌幅 | 市场判断 |
|----------|----------|--------|----------|
| 标普500 | {fmt_num(market_data.get('sp500', {}).get('price'))} | {fmt_num(market_data.get('sp500', {}).get('change_pct'))}% | {self._judge_market(market_data.get('sp500', {}).get('change_pct', 0))} |
| 道琼斯 | {fmt_num(market_data.get('dow', {}).get('price'))} | {fmt_num(market_data.get('dow', {}).get('change_pct'))}% | {self._judge_market(market_data.get('dow', {}).get('change_pct', 0))} |

---

## 🎯 低估值股票推荐

### 评分体系说明
| 评分维度 | 权重 | 计算方法 |
|----------|------|----------|
| PE估值 | 40% | PE越低分数越高，PE>30为高分 |
| PB估值 | 30% | PB越低分数越高，PB>5为高分 |
| 股息率 | 30% | 股息率越高分数越高，>3%为佳 |

> 📊 **高分标准**: 估值得分 > 80分 为**低估值优质标的**  
> 📊 **参考标准**: 70-80分 为估值合理，< 70分 为偏高估

### 推荐股票
| 代码 | 名称 | 现价 | 涨跌幅 | PE | PB | 股息率 | 估值得分 | 估值评价 |
|------|------|------|--------|-----|-----|---------|----------|----------|
"""
        
        for rec in stock_recommendations[:10]:
            score = rec.get('valuation_score', 0)
            evaluation = self._evaluate_valuation(score)
            
            # 添加历史百分位信息
            hist_info = ""
            if 'valuation_assessment' in rec:
                hist = rec['valuation_assessment']
                hist_info = f" ({hist.get('overall', '')})"
            
            report += f"| {rec['code']} | {rec.get('name', '')} | {fmt_num(rec.get('price'))} | {fmt_num(rec.get('change_pct'))}% | {fmt_num(rec.get('pe'))} | {fmt_num(rec.get('pb'))} | {fmt_num(rec.get('dividend'))}% | **{fmt_num(score)}** | {evaluation}{hist_info} |\n"
        
        # 添加历史百分位详细分析
        report += """
### 历史估值百分位分析（近3年）

> 📊 **百分位说明**: 表示当前估值在历史数据中的位置，越低代表越便宜
> - 🟢 0-20%: 极度低估，适合买入
> - 🟡 20-40%: 偏低，可考虑买入
> - ⚪ 40-60%: 合理估值
> - 🟠 60-80%: 偏高，谨慎买入
> - 🔴 80-100%: 极度高估，考虑卖出

"""
        
        for rec in stock_recommendations[:5]:  # 只显示前5只的详细分析
            if 'historical_percentile' in rec and rec['historical_percentile']:
                hist = rec['historical_percentile']
                name = rec.get('name', rec['code'])
                
                report += f"#### {name} ({rec['code']})\n\n"
                
                # PE百分位
                if 'pe' in hist:
                    pe = hist['pe']
                    pe_emoji = self._get_percentile_emoji(pe.percentile)
                    report += f"- **PE估值**: {pe.current_value:.1f} | 历史分位: {pe.percentile:.0f}% {pe_emoji}\n"
                    report += f"  - 历史区间: {pe.min_value:.1f} - {pe.max_value:.1f}, 中位数: {pe.median:.1f}\n"
                
                # PB百分位
                if 'pb' in hist:
                    pb = hist['pb']
                    pb_emoji = self._get_percentile_emoji(pb.percentile)
                    report += f"- **PB估值**: {pb.current_value:.2f} | 历史分位: {pb.percentile:.0f}% {pb_emoji}\n"
                    report += f"  - 历史区间: {pb.min_value:.2f} - {pb.max_value:.2f}, 中位数: {pb.median:.2f}\n"
                
                # 综合评估
                if 'valuation_assessment' in rec:
                    assess = rec['valuation_assessment']
                    report += f"- **综合评估**: {assess.get('overall', 'N/A')} (评分: {assess.get('score', 'N/A')}/100)\n"
                    for detail in assess.get('details', []):
                        report += f"  - {detail}\n"
                
                # 风险指标
                if 'risk_metrics' in rec:
                    risk = rec['risk_metrics']
                    report += f"- **风险指标**: {format_risk_for_report(risk)}\n"
                
                report += "\n"
        
        report += """
---

## 📦 基金分析（重点）

### 基金评分体系说明
| 评分维度 | 权重 | 计算方法 | 优秀标准 |
|----------|------|----------|----------|
| 趋势评分 | 30% | 当前价格与MA20/60/200均线关系 | 价格位于所有均线上方 |
| 稳定性 | 20% | 历史波动率(标准差) | 波动率 < 1.5% |
| 收益评分 | 30% | 年化收益率 | 年化 > 15% |
| 短期表现 | 20% | 近1月收益率 | 收益率 > 5% |

> 📊 **高分标准**: 综合得分 > 75分 为**优质基金**  
> 📊 **参考标准**: 60-75分 为良好，< 60分 为一般

### 推荐基金
| 代码 | 名称 | 最新净值 | 日涨跌 | 综合评分 | 趋势 | 风险等级 |
|------|------|----------|--------|----------|------|----------|
"""
        
        for fund in fund_recommendations[:10]:
            score = fund.get('fund_score', 0)
            trend = fund.get('trend', 'N/A')
            report += f"| {fund['code']} | {fund.get('name', '')} | {fmt_num(fund.get('nav'))} | {fmt_num(fund.get('daily_change'))}% | **{fmt_num(score)}** | {trend} | {fund.get('risk_level', 'N/A')} |\n"
        
        # 基金详细信息
        if fund_recommendations:
            report += """
### 重点基金详情

"""
            for fund in fund_recommendations[:5]:
                methodology = fund.get('methodology', {})
                report += f"""#### {fund.get('name', fund['code'])} ({fund['code']})

| 指标 | 数值 |
|------|------|
| 基金类型 | {fund.get('fund_type', 'N/A')} |
| 跟踪指数 | {fund.get('tracking_index', 'N/A')} |
| 基金规模 | {fund.get('scale', 'N/A')} |
| 管理费率 | {fund.get('fee', 'N/A')} |
| 成立以来收益 | {fmt_num(fund.get('total_return', 0))}% |

**前十大持仓**: {', '.join(fund.get('top_holdings', [])[:5]) if fund.get('top_holdings') else 'N/A'}

**评分详情**:
- 趋势评分: {methodology.get('trend_score', 'N/A')}
- 稳定性: {methodology.get('stability_score', 'N/A')}
- 收益评分: {methodology.get('return_score', 'N/A')}
- 短期表现: {methodology.get('month_score', 'N/A')}

"""
        
        # 持仓分析
        report += f"""
---

## 💰 持仓分析

### 账户概况
| 指标 | 数值 |
|------|------|
| 初始资金 | {INITIAL_CAPITAL:,.2f} 元 |
| 当前市值 | {portfolio_value:,.2f} 元 |
| 盈亏金额 | {profit:+,.2f} 元 |
| 盈亏比例 | {profit_pct:+.2f}% |

"""
        
        if portfolio_summary:
            report += """### 当前持仓明细

| 代码 | 名称 | 持仓量 | 成本价 | 现价 | 市值 | 盈亏 | 盈亏% | 操作建议 |
|------|------|--------|--------|------|------|------|--------|----------|
"""
            for pos in portfolio_summary:
                action = pos.get('action', '持有')
                report += f"| {pos['code']} | {pos.get('name', '')} | {pos.get('amount', 0)} | {fmt_num(pos.get('cost'))} | {fmt_num(pos.get('current_price'))} | {fmt_num(pos.get('value', 0))} | {pos.get('profit', 0):+,.2f} | {fmt_num(pos.get('profit_pct'))}% | {action} |\n"
        
        report += f"""
---

## 📋 操作建议

### 今日重点关注

"""
        
        if stock_recommendations:
            top_stock = stock_recommendations[0]
            report += f"**股票**: 建议关注 **{top_stock.get('name', top_stock['code'])}**，估值得分 **{fmt_num(top_stock.get('valuation_score', 0))}**，{self._evaluate_valuation(top_stock.get('valuation_score', 0))}\n"
        
        if fund_recommendations:
            top_fund = fund_recommendations[0]
            report += f"**基金**: 建议关注 **{top_fund.get('name', top_fund['code'])}**，综合评分 **{fmt_num(top_fund.get('fund_score', 0))}**，{top_fund.get('trend', '趋势待观察')}\n"
        
        report += """
### 风险提示

1. ⚠️ 本报告仅供学习研究，不构成投资建议
2. ⚠️ 历史收益不代表未来表现
3. ⚠️ 请根据自身风险承受能力合理配置
4. ⚠️ 基金投资需关注长期价值，避免短期追涨杀跌

---

## 📊 数据说明

- ⏰ 报告更新时间: 每日收盘后
- 📈 数据来源: 东方财富、新浪财经（模拟数据）
- 🔄 持仓追踪: 止盈线 15%，止损线 -10%
- 💾 历史数据: 存储于本地SQLite数据库

---

*🤖 本报告由 AI 智能分析系统自动生成*
*📅 生成时间: """ + now + """
"""
        
        return report
    
    def _judge_market(self, change_pct: float) -> str:
        """判断市场状态"""
        if change_pct is None:
            return '数据获取中'
        if change_pct > 1.5:
            return '🌟 强势上涨'
        elif change_pct > 0.5:
            return '📈 小幅上涨'
        elif change_pct > -0.5:
            return '➡️ 横盘整理'
        elif change_pct > -1.5:
            return '📉 小幅下跌'
        else:
            return '⚠️ 弱势下跌'
    
    def _evaluate_valuation(self, score: float) -> str:
        """评估估值"""
        if score is None:
            return 'N/A'
        if score >= 85:
            return '🟢 深度低估'
        elif score >= 75:
            return '🟢 低估'
        elif score >= 60:
            return '🟡 合理'
        elif score >= 40:
            return '🟠 偏高'
        else:
            return '🔴 高估'
    
    def _get_percentile_emoji(self, percentile: float) -> str:
        """根据百分位返回表情符号"""
        if percentile <= 20:
            return '🟢'  # 极度低估
        elif percentile <= 40:
            return '🟡'  # 偏低
        elif percentile <= 60:
            return '⚪'  # 合理
        elif percentile <= 80:
            return '🟠'  # 偏高
        else:
            return '🔴'  # 极度高估
    
    def save_report(self, report: str, filename: str = None) -> str:
        """保存报告"""
        if filename is None:
            filename = f"full_report_{datetime.now().strftime('%Y-%m-%d')}.md"
        
        filepath = os.path.join(self.report_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filepath


if __name__ == "__main__":
    generator = EnhancedReportGenerator()
    print("增强版报告生成器测试完成")
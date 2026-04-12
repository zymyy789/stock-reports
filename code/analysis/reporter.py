"""
报告生成模块 - 生成每日分析报告
"""
import os
from datetime import datetime
from typing import List, Dict
import json
from config import REPORT_DIR, INITIAL_CAPITAL


def fmt_num(val, decimals=2):
    """安全格式化数字"""
    if val is None:
        return 'N/A'
    try:
        return f"{float(val):.2f}"
    except:
        return 'N/A'


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, report_dir: str = REPORT_DIR):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
    
    def generate_daily_report(self, 
                            market_data: Dict,
                            recommendations: List[Dict],
                            portfolio_analysis: List[Dict],
                            portfolio_summary: List[Dict],
                            portfolio_value: float) -> str:
        """生成每日报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 计算收益率
        profit = portfolio_value - INITIAL_CAPITAL
        profit_pct = (profit / INITIAL_CAPITAL * 100) if INITIAL_CAPITAL > 0 else 0
        
        report = f"""# 📈 股票基金每日分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 市场概况

### A股指数
| 指数 | 最新价 | 涨跌幅 |
|------|--------|--------|
| 上证指数 | {fmt_num(market_data.get('shanghai', {}).get('price'))} | {fmt_num(market_data.get('shanghai', {}).get('change_pct'))}% |
| 深证成指 | {fmt_num(market_data.get('shenzhen', {}).get('price'))} | {fmt_num(market_data.get('shenzhen', {}).get('change_pct'))}% |

### 港股指数
| 指数 | 最新价 | 涨跌幅 |
|------|--------|--------|
| 恒生指数 | {fmt_num(market_data.get('hsi', {}).get('price'))} | {fmt_num(market_data.get('hsi', {}).get('change_pct'))}% |
| 国企指数 | {fmt_num(market_data.get('hscei', {}).get('price'))} | {fmt_num(market_data.get('hscei', {}).get('change_pct'))}% |

### 美股指数
| 指数 | 最新价 | 涨跌幅 |
|------|--------|--------|
| 标普500 | {fmt_num(market_data.get('sp500', {}).get('price'))} | {fmt_num(market_data.get('sp500', {}).get('change_pct'))}% |
| 道琼斯 | {fmt_num(market_data.get('dow', {}).get('price'))} | {fmt_num(market_data.get('dow', {}).get('change_pct'))}% |

---

## 🎯 低估值股票推荐

基于 PE、PB、股息率综合筛选，以下股票处于低估值区间：

| 代码 | 名称 | 现价 | 涨跌幅 | PE | PB | 股息率% | 估值得分 | 推荐理由 |
|------|------|------|--------|-----|-----|---------|----------|----------|
"""
        
        for rec in recommendations[:10]:
            report += f"| {rec['code']} | {rec.get('name', '')} | {fmt_num(rec.get('price'))} | {fmt_num(rec.get('change_pct'))}% | {fmt_num(rec.get('pe'))} | {fmt_num(rec.get('pb'))} | {fmt_num(rec.get('dividend'))} | {fmt_num(rec.get('valuation_score'))} | {rec.get('recommend_reason', '')} |\n"
        
        report += f"""
---

## 💼 持仓分析

### 当前持仓

**模拟资金**: {INITIAL_CAPITAL:,.2f} 元  
**当前市值**: {portfolio_value:,.2f} 元  
**盈亏**: {profit:+,.2f} 元 ({profit_pct:+.2f}%)

| 代码 | 名称 | 持仓量 | 成本价 | 现价 | 盈亏 | 盈亏% | 操作建议 |
|------|------|--------|--------|------|------|--------|----------|
"""
        
        for pos in portfolio_summary:
            report += f"| {pos['code']} | {pos.get('name', '')} | {pos.get('amount', 0)} | {fmt_num(pos.get('cost'))} | {fmt_num(pos.get('current_price'))} | {pos.get('profit', 0):+,.2f} | {fmt_num(pos.get('profit_pct'))}% | {pos.get('action', '持有')} |\n"
        
        if portfolio_summary:
            report += "\n### 持仓操作建议\n\n"
            for analysis in portfolio_analysis:
                report += f"- **{analysis['name']}** ({analysis['code']}): {analysis['action']} - {analysis['reason']}\n"
        
        report += f"""
---

## 📝 总结

1. **市场情绪**: {self._get_market_sentiment(market_data)}
2. **今日操作**: {"无新推荐" if not recommendations else f"建议关注 {recommendations[0]['name']} 等低估值股票"}
3. **风险提示**: 本报告仅供学习研究，不构成投资建议。

---

*本报告由 AI 自动生成*
"""
        
        return report
    
    def _get_market_sentiment(self, market_data: Dict) -> str:
        """判断市场情绪"""
        changes = []
        for key, data in market_data.items():
            pct = data.get('change_pct', 0)
            if pct:
                changes.append(pct)
        
        if not changes:
            return "数据获取中..."
        
        avg = sum(changes) / len(changes)
        if avg > 1:
            return "偏暖，市场上涨家数较多"
        elif avg < -1:
            return "偏冷，市场下跌家数较多"
        else:
            return "中性，震荡整理为主"
    
    def save_report(self, report: str, filename: str = None) -> str:
        """保存报告到文件"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y-%m-%d')}.md"
        
        filepath = os.path.join(self.report_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filepath
    
    def export_json(self, data: Dict, filename: str = None) -> str:
        """导出数据为JSON"""
        if filename is None:
            filename = f"data_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        filepath = os.path.join(self.report_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath


if __name__ == "__main__":
    generator = ReportGenerator()
    print("报告生成模块测试")
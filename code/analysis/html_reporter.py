"""
生成HTML格式报告 - 修复版
包含HTML报告和微信消息两种格式
"""
import os
from datetime import datetime
from typing import List, Dict


def fmt_num(val, decimals=2):
    if val is None:
        return 'N/A'
    try:
        return f"{float(val):.{decimals}f}"
    except:
        return 'N/A'


def make_wechat_message(
    market_data: Dict,
    stock_recommendations: List[Dict],
    fund_recommendations: List[Dict],
    portfolio_summary: List[Dict],
    portfolio_value: float,
    INITIAL_CAPITAL: float = 100000
) -> str:
    """生成微信可读的消息，链接使用纯文本格式（微信不支持Markdown链接）"""
    date = datetime.now().strftime('%Y-%m-%d')
    
    profit = portfolio_value - INITIAL_CAPITAL
    profit_pct = (profit / INITIAL_CAPITAL * 100) if INITIAL_CAPITAL > 0 else 0
    
    msg = f"""📊 智能投资分析报告 {date}

━━━━━━━━━━━━━━━━━━

📈 市场行情
• 上证: {fmt_num(market_data.get('shanghai', {}).get('price'))} ({fmt_num(market_data.get('shanghai', {}).get('change_pct'))}%)
• 深证: {fmt_num(market_data.get('shenzhen', {}).get('price'))} ({fmt_num(market_data.get('shenzhen', {}).get('change_pct'))}%)
• 恒生: {fmt_num(market_data.get('hsi', {}).get('price'))} ({fmt_num(market_data.get('hsi', {}).get('change_pct'))}%)
• 标普500: {fmt_num(market_data.get('sp500', {}).get('price'))} ({fmt_num(market_data.get('sp500', {}).get('change_pct'))}%)

━━━━━━━━━━━━━━━━━━

🏆 低估值股票 TOP 12"""

    # 展示更多股票（至少12只）
    display_stocks = stock_recommendations[:12] if len(stock_recommendations) >= 12 else stock_recommendations
    for i, rec in enumerate(display_stocks, 1):
        score = rec.get('valuation_score', 0)
        score_emoji = "🟢" if score >= 80 else ("🟡" if score >= 70 else ("🟠" if score >= 60 else "🔴"))
        change = rec.get('change_pct', 0)
        change_str = f"+{change}%" if change >= 0 else f"{change}%"
        market = 'sh' if rec['code'][0] in '569' else 'sz'
        link = f"https://quote.eastmoney.com/{market}{rec['code']}.html"
        name = rec.get('name', '')
        
        msg += f"""

{i}. {name}({rec['code']})
   现价: {rec.get('price', 0):.2f}元 {change_str}
   PE={fmt_num(rec.get('pe'))} 股息={fmt_num(rec.get('dividend'))}%
   {score_emoji} 估值得分: {score:.1f}
   {rec.get('recommend_reason', '')}
   🔗 {link}"""

    msg += """

━━━━━━━━━━━━━━━━━━

📦 基金分析 TOP 15
评分: 趋势30% + 稳定性20% + 收益30% + 短期20%"""

    # 展示更多基金（至少15只）
    display_funds = fund_recommendations[:15] if len(fund_recommendations) >= 15 else fund_recommendations
    for i, fund in enumerate(display_funds, 1):
        score = fund.get('fund_score', 0)
        risk = fund.get('risk_level', '中')
        risk_emoji = "🔴" if risk == "高" else ("🟡" if risk == "中" else "🟢")
        daily = fund.get('daily_change', 0)
        daily_str = f"+{daily}%" if daily >= 0 else f"{daily}%"
        link = f"https://fund.eastmoney.com/{fund['code']}.html"
        name = fund.get('name', '')
        
        msg += f"""

{i}. {name}({fund['code']})
   净值: {fund.get('nav', 0):.4f} 日涨跌: {daily_str}
   {risk_emoji}风险:{risk} | 综合评分:{score:.1f}
   🔗 {link}"""

    # 持仓分析
    profit_emoji = "🟢" if profit >= 0 else "🔴"
    
    msg += f"""

━━━━━━━━━━━━━━━━━━

💼 持仓分析
• 初始资金: {INITIAL_CAPITAL:,.0f}元
• 当前市值: {portfolio_value:,.0f}元
• 盈亏: {profit_emoji} {profit:+,.0f}元 ({profit_pct:+.2f}%)"""

    if portfolio_summary:
        msg += "\n\n持仓明细:"
        for pos in portfolio_summary:
            market = 'sh' if pos['code'][0] in '569' else 'sz'
            link = f"https://quote.eastmoney.com/{market}{pos['code']}.html"
            profit_emoji_pos = "🟢" if pos.get('profit', 0) >= 0 else "🔴"
            name = pos.get('name', pos['code'])
            msg += f"""

• {name}({pos['code']})
  持仓: {pos.get('amount', 0)}股
  成本: {pos.get('cost', 0):.2f}元 → 现价: {pos.get('current_price', 0):.2f}元
  {profit_emoji_pos} 盈亏: {pos.get('profit', 0):+,.0f}元 ({pos.get('profit_pct', 0):+.1f}%)
  建议: {pos.get('action', '持有')}
  🔗 {link}"""
    else:
        msg += "\n\n暂无持仓记录"

    # 操作建议
    msg += """

━━━━━━━━━━━━━━━━━━

📋 操作建议"""
    if stock_recommendations:
        top = stock_recommendations[0]
        market = 'sh' if top['code'][0] in '569' else 'sz'
        link = f"https://quote.eastmoney.com/{market}{top['code']}.html"
        name = top.get('name', '')
        msg += f"""

• 股票: 关注 {name}({top['code']})
  估值得分: {top.get('valuation_score', 0):.1f}
  🔗 {link}"""
    
    if fund_recommendations:
        top_fund = fund_recommendations[0]
        link = f"https://fund.eastmoney.com/{top_fund['code']}.html"
        name = top_fund.get('name', '')
        msg += f"""

• 基金: 关注 {name}({top_fund['code']})
  综合评分: {top_fund.get('fund_score', 0):.1f}
  🔗 {link}"""

    msg += """

━━━━━━━━━━━━━━━━━━

⚠️ 本报告仅供参考，不构成投资建议
🤖 AI智能分析系统 自动生成"""

    return msg


def generate_html_report(
    market_data: Dict,
    stock_recommendations: List[Dict],
    fund_recommendations: List[Dict],
    portfolio_summary: List[Dict],
    portfolio_value: float,
    INITIAL_CAPITAL: float = 100000
) -> str:
    """生成HTML报告"""
    
    date = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    profit = portfolio_value - INITIAL_CAPITAL
    profit_pct = (profit / INITIAL_CAPITAL * 100) if INITIAL_CAPITAL > 0 else 0
    
    # 股票链接
    stock_links = {
        '600519': 'https://quote.eastmoney.com/sh600519.html',
        '601318': 'https://quote.eastmoney.com/sh601318.html',
        '600036': 'https://quote.eastmoney.com/sh600036.html',
        '000858': 'https://quote.eastmoney.com/sz000858.html',
        '601166': 'https://quote.eastmoney.com/sh601166.html',
        '600030': 'https://quote.eastmoney.com/sh600030.html',
        '600887': 'https://quote.eastmoney.com/sh600887.html',
        '000333': 'https://quote.eastmoney.com/sz000333.html',
        '601888': 'https://quote.eastmoney.com/sh601888.html',
        '600276': 'https://quote.eastmoney.com/sh600276.html',
        '000651': 'https://quote.eastmoney.com/sz000651.html',
        '002594': 'https://quote.eastmoney.com/sz002594.html',
    }
    
    # 基金链接
    fund_links = {
        '510050': 'https://fund.eastmoney.com/510050.html',
        '510300': 'https://fund.eastmoney.com/510300.html',
        '510310': 'https://fund.eastmoney.com/510310.html',
        '159915': 'https://fund.eastmoney.com/159915.html',
        '510500': 'https://fund.eastmoney.com/510500.html',
        '588000': 'https://fund.eastmoney.com/588000.html',
        '512880': 'https://fund.eastmoney.com/512880.html',
        '515000': 'https://fund.eastmoney.com/515000.html',
        '159920': 'https://fund.eastmoney.com/159920.html',
        '513500': 'https://fund.eastmoney.com/513500.html',
        '513100': 'https://fund.eastmoney.com/513100.html',
        '002001': 'https://fund.eastmoney.com/002001.html',
        '110022': 'https://fund.eastmoney.com/110022.html',
        '000831': 'https://fund.eastmoney.com/000831.html',
        '163402': 'https://fund.eastmoney.com/163402.html',
        '270008': 'https://fund.eastmoney.com/270008.html',
        '000128': 'https://fund.eastmoney.com/000128.html',
        '110008': 'https://fund.eastmoney.com/110008.html',
        '159788': 'https://fund.eastmoney.com/159788.html',
        '159805': 'https://fund.eastmoney.com/159805.html',
        '159819': 'https://fund.eastmoney.com/159819.html',
        '515050': 'https://fund.eastmoney.com/515050.html',
        '512760': 'https://fund.eastmoney.com/512760.html',
        '513030': 'https://fund.eastmoney.com/513030.html',
    }
    
    def score_color(score):
        if score is None:
            return '#666'
        if score >= 85:
            return '#28a745'
        elif score >= 75:
            return '#5cb85c'
        elif score >= 60:
            return '#ffc107'
        elif score >= 40:
            return '#fd7e14'
        else:
            return '#dc3545'
    
    def change_class(val):
        if val is None:
            return ''
        return 'positive' if val > 0 else 'negative'
    
    # ============ HTML 模板 ============
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能投资分析报告 {date}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 16px; max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        h1 {{ font-size: 22px; color: #1a1a1a; margin-bottom: 8px; text-align: center; }}
        .subtitle {{ text-align: center; color: #666; font-size: 13px; margin-bottom: 20px; }}
        h2 {{ font-size: 16px; color: #333; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #1a73e8; }}
        h3 {{ font-size: 14px; color: #555; margin: 12px 0 8px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }}
        th {{ background: #f8f9fa; padding: 10px 6px; text-align: left; font-weight: 600; color: #333; border-bottom: 2px solid #dee2e6; }}
        td {{ padding: 10px 6px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .positive {{ color: #dc3545; }}
        .negative {{ color: #28a745; }}
        .score {{ font-weight: bold; padding: 4px 8px; border-radius: 4px; display: inline-block; min-width: 40px; text-align: center; }}
        .link {{ color: #1a73e8; text-decoration: none; font-size: 12px; }}
        .summary-box {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin: 12px 0; }}
        .summary-item {{ background: #f8f9fa; padding: 12px; border-radius: 8px; text-align: center; }}
        .summary-label {{ font-size: 12px; color: #666; }}
        .summary-value {{ font-size: 18px; font-weight: bold; color: #1a1a1a; margin-top: 4px; }}
        .tag {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 11px; }}
        .tag-green {{ background: #d4edda; color: #155724; }}
        .tag-red {{ background: #f8d7da; color: #721c24; }}
        .footer {{ text-align: center; color: #999; font-size: 11px; padding: 20px; }}
        .methodology {{ background: #f8f9fa; padding: 12px; border-radius: 8px; font-size: 12px; color: #555; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>智能投资分析报告</h1>
        <div class="subtitle">{date} 自动生成</div>
        
        <div class="summary-box">
            <div class="summary-item">
                <div class="summary-label">上证指数</div>
                <div class="summary-value">{fmt_num(market_data.get('shanghai', {}).get('price'))}</div>
                <div class="{change_class(market_data.get('shanghai', {}).get('change_pct'))}">{fmt_num(market_data.get('shanghai', {}).get('change_pct'))}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">深证成指</div>
                <div class="summary-value">{fmt_num(market_data.get('shenzhen', {}).get('price'))}</div>
                <div class="{change_class(market_data.get('shenzhen', {}).get('change_pct'))}">{fmt_num(market_data.get('shenzhen', {}).get('change_pct'))}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">恒生指数</div>
                <div class="summary-value">{fmt_num(market_data.get('hsi', {}).get('price'))}</div>
                <div class="{change_class(market_data.get('hsi', {}).get('change_pct'))}">{fmt_num(market_data.get('hsi', {}).get('change_pct'))}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">标普500</div>
                <div class="summary-value">{fmt_num(market_data.get('sp500', {}).get('price'))}</div>
                <div class="{change_class(market_data.get('sp500', {}).get('change_pct'))}">{fmt_num(market_data.get('sp500', {}).get('change_pct'))}%</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>低估值股票推荐</h2>
        <div class="methodology">
            评分体系：PE估值40% + PB估值30% + 股息率30%<br>
            高分标准：>80分为低估值优质标的
        </div>
        <table>
            <tr><th>代码</th><th>名称</th><th>现价</th><th>涨跌</th><th>PE</th><th>股息</th><th>评分</th></tr>"""
    
    for rec in stock_recommendations[:12]:
        score = rec.get('valuation_score', 0)
        link = stock_links.get(rec['code'], f"https://quote.eastmoney.com/{'sh' if rec['code'][0] in '569' else 'sz'}{rec['code']}.html")
        html += f"""<tr>
            <td><a href="{link}" class="link" target="_blank">{rec['code']}</a></td>
            <td>{rec.get('name', '')}</td>
            <td>{fmt_num(rec.get('price'))}</td>
            <td class="{change_class(rec.get('change_pct'))}">{fmt_num(rec.get('change_pct'))}%</td>
            <td>{fmt_num(rec.get('pe'))}</td>
            <td>{fmt_num(rec.get('dividend'))}%</td>
            <td><span class="score" style="background:{score_color(score)};color:white">{fmt_num(score)}</span></td>
        </tr>"""
    
    html += """</table></div>
    
    <div class="card">
        <h2>基金分析</h2>
        <div class="methodology">
            评分体系：趋势30% + 稳定性20% + 收益30% + 短期20%<br>
            高分标准：>75分为优质基金
        </div>
        <table>
            <tr><th>代码</th><th>名称</th><th>净值</th><th>日涨跌</th><th>风险</th><th>评分</th></tr>"""
    
    # 显示更多基金，至少显示15只
    display_funds = fund_recommendations[:15] if len(fund_recommendations) >= 15 else fund_recommendations
    for fund in display_funds:
        score = fund.get('fund_score', 0)
        link = fund_links.get(fund['code'], f"https://fund.eastmoney.com/{fund['code']}.html")
        html += f"""<tr>
            <td><a href="{link}" class="link" target="_blank">{fund['code']}</a></td>
            <td>{fund.get('name', '')}</td>
            <td>{fmt_num(fund.get('nav'), 4)}</td>
            <td class="{change_class(fund.get('daily_change'))}">{fmt_num(fund.get('daily_change'))}%</td>
            <td><span class="tag {'tag-red' if fund.get('risk_level') == '高' else ('tag-green' if fund.get('risk_level') == '低' else '')}">{fund.get('risk_level', 'N/A')}</span></td>
            <td><span class="score" style="background:{score_color(score)};color:white">{fmt_num(score)}</span></td>
        </tr>"""
    
    # 重点基金详情（显示前5只）
    if fund_recommendations[:5]:
        html += """</table>
        <h3>重点基金详情</h3>
        <table>"""
        for fund in fund_recommendations[:5]:
            link = fund_links.get(fund['code'], f"https://fund.eastmoney.com/{fund['code']}.html")
            html += f"""<tr>
                <td colspan="6" style="background:#f8f9fa;font-weight:bold;padding:12px;">
                    <a href="{link}" class="link" target="_blank">{fund.get('name', '')} ({fund['code']})</a><br>
                    <small style="color:#666;">类型：{fund.get('fund_type', 'N/A')} | 规模：{fund.get('scale', 'N/A')} | 跟踪：{fund.get('tracking_index', 'N/A')}</small>
                </td>
            </tr>"""
    
    html += """</table></div>
    
    <div class="card">
        <h2>持仓分析</h2>
        <div class="summary-box">
            <div class="summary-item">
                <div class="summary-label">初始资金</div>
                <div class="summary-value">{:.0f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">当前市值</div>
                <div class="summary-value">{:.0f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">盈亏金额</div>
                <div class="summary-value {positive if profit > 0 else negative}">{profit:+,.0f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">盈亏比例</div>
                <div class="summary-value {positive if profit_pct > 0 else negative}">{profit_pct:+.2f}%</div>
            </div>
        </div>"""
    
    if portfolio_summary:
        html += """<table>
            <tr><th>代码</th><th>名称</th><th>持仓</th><th>盈亏</th><th>建议</th></tr>"""
        for pos in portfolio_summary:
            link = stock_links.get(pos['code'], fund_links.get(pos['code'], f"https://quote.eastmoney.com/{'sh' if pos['code'][0] in '569' else 'sz'}{pos['code']}.html"))
            html += f"""<tr>
                <td><a href="{link}" class="link">{pos['code']}</a></td>
                <td>{pos.get('name', '')}</td>
                <td>{pos.get('amount', 0)}</td>
                <td class="{change_class(pos.get('profit'))}">{pos.get('profit', 0):+,.0f}</td>
                <td>{pos.get('action', '持有')}</td>
            </tr>"""
        html += "</table>"
    else:
        html += "<p style='color:#999;text-align:center;padding:20px;'>暂无持仓</p>"
    
    html += f"""</div>
    
    <div class="card">
        <h2>操作建议</h2>
        <div style="padding:12px;background:#e8f4fd;border-radius:8px;">"""
    
    if stock_recommendations:
        top_stock = stock_recommendations[0]
        link = stock_links.get(top_stock['code'], f"https://quote.eastmoney.com/{'sh' if top_stock['code'][0] in '569' else 'sz'}{top_stock['code']}.html")
        html += f"""<p>股票：关注 <a href="{link}" class="link">{top_stock.get('name', '')}</a>，估值得分 {fmt_num(top_stock.get('valuation_score'))}</p>"""
    
    if fund_recommendations:
        top_fund = fund_recommendations[0]
        link = fund_links.get(top_fund['code'], f"https://fund.eastmoney.com/{top_fund['code']}.html")
        html += f"""<p style="margin-top:8px;">基金：关注 <a href="{link}" class="link">{top_fund.get('name', '')}</a>，综合评分 {fmt_num(top_fund.get('fund_score'))}</p>"""
    
    html += """</div>
        <div style="margin-top:12px;color:#666;font-size:12px;">
            免责声明：本报告仅供参考，不构成投资建议
        </div>
    </div>
    
    <div class="footer">
        <p>AI智能分析系统 · {now}</p>
    </div>
</body>
</html>""".format(
        INITIAL_CAPITAL,
        portfolio_value,
        profit=profit,
        profit_pct=profit_pct,
        now=now
    )
    
    return html


if __name__ == "__main__":
    print("HTML报告生成模块")

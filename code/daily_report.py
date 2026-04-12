# -*- coding: utf-8 -*-
"""
每日自动报告生成 - 包含模拟持仓盈亏和策略信号
"""
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')

from analysis.portfolio_manager import PortfolioManager
from analysis.fetcher import StockFetcher
from analysis.fund_fetcher import FundFetcher
from datetime import datetime
import json

def generate_daily_report():
    """生成每日报告"""
    pm = PortfolioManager()
    stock_fetcher = StockFetcher()
    fund_fetcher = FundFetcher()
    
    # 获取持仓情况
    portfolio = pm.get_portfolio_value()
    signals = pm.get_strategy_signals()
    
    # 获取市场指数
    indices = [
        {'name': '上证指数', 'code': 'sh000001'},
        {'name': '沪深300', 'code': 'sh000300'},
        {'name': '创业板指', 'code': 'sz399006'},
    ]
    
    index_data = []
    for idx in indices:
        try:
            import requests
            url = f"https://qt.gtimg.cn/q={idx['code']}"
            resp = requests.get(url, headers={'Referer': 'https://gu.qq.com/'}, timeout=5)
            resp.encoding = 'gbk'
            parts = resp.text.split('~')
            if len(parts) > 32:
                index_data.append({
                    'name': idx['name'],
                    'price': float(parts[3]),
                    'change': float(parts[32])
                })
        except:
            pass
    
    # 生成报告
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'market': index_data,
        'portfolio': portfolio,
        'signals': signals,
    }
    
    # 保存报告
    report_file = r'C:\Users\zymyy\.qclaw\workspace\stock_work\reports\daily_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成微信消息
    msg = generate_wechat_message(report)
    
    # 保存微信消息
    wechat_file = r'C:\Users\zymyy\.qclaw\workspace\stock_work\reports\wechat_daily.txt'
    with open(wechat_file, 'w', encoding='utf-8') as f:
        f.write(msg)
    
    return report, msg

def generate_wechat_message(report):
    """生成微信可读的消息"""
    lines = []
    lines.append(f"📊 每日投资报告 {report['date']}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    # 市场行情
    lines.append("📈 市场行情")
    for idx in report['market']:
        up = idx['change'] >= 0
        lines.append(f"• {idx['name']}: {idx['price']:.2f} {'🔺' if up else '🔻'}{idx['change']:.2f}%")
    lines.append("")
    
    # 模拟持仓
    p = report['portfolio']
    lines.append("💼 模拟持仓")
    lines.append(f"• 现金: ¥{p['cash']:.2f}")
    lines.append(f"• 持仓市值: ¥{p['total_value']:.2f}")
    lines.append(f"• 总盈亏: {'🔴' if p['total_profit'] >= 0 else '🟢'}¥{p['total_profit']:.2f} ({p['total_profit_pct']:.2f}%)")
    lines.append(f"• 总资产: ¥{p['total_assets']:.2f}")
    
    if p['positions']:
        lines.append("")
        lines.append("持仓明细:")
        for pos in p['positions'][:5]:  # 只显示前5个
            up = pos['profit'] >= 0
            lines.append(f"  {pos['name']}: {'🔴' if up else '🟢'}{pos['profit']:.0f} ({pos['profit_pct']:.1f}%)")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    # 策略信号
    signals = report['signals']
    if signals['buy']:
        lines.append("📥 买入信号")
        for s in signals['buy'][:3]:
            lines.append(f"• {s['name']}(PE:{s['pe']:.1f}) - {s['reason']}")
        lines.append("")
    
    if signals['sell']:
        lines.append("📤 卖出信号")
        for s in signals['sell'][:3]:
            lines.append(f"• {s['name']}(PE:{s['pe']:.1f}) - {s['reason']}")
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("⚠️ 本报告仅供参考，不构成投资建议")
    
    return '\n'.join(lines)

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    report, msg = generate_daily_report()
    print(msg)

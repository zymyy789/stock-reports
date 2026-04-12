# -*- coding: utf-8 -*-
"""
自动模拟交易脚本 - 基于PE估值策略
每天收盘后(15:30)自动运行，检查并执行交易
"""
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

import os
from datetime import datetime
from analysis.fetcher import StockFetcher
from analysis.portfolio_manager import PortfolioManager

DATA_DIR = r'C:\Users\zymyy\.qclaw\workspace\stock_work\data'
os.makedirs(DATA_DIR, exist_ok=True)

BUY_PE = 15   # PE<15 买入
SELL_PE = 30  # PE>30 卖出

def main():
    print(f"[自动交易] 开始检查 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pm = PortfolioManager()
    sf = StockFetcher()
    
    watchlist = [
        ('601166', '兴业银行'), ('600036', '招商银行'), ('601318', '中国平安'),
        ('600030', '中信证券'), ('600887', '伊利股份'), ('000858', '五粮液'),
        ('000333', '美的集团'), ('600519', '贵州茅台'), ('600276', '恒瑞医药'),
        ('601888', '中国中免'), ('601328', '交通银行'), ('000001', '平安银行'),
        ('601818', '光大银行'), ('600016', '民生银行'), ('601288', '农业银行'),
    ]
    
    actions = []
    signals = []
    
    # 获取实时价格
    prices = {}
    for code, name in watchlist:
        d = sf.get_a_stock_price(code)
        if d:
            prices[code] = {'price': d['price'], 'pe': d.get('pe', 0)}
    
    for code, name in watchlist:
        if code not in prices:
            continue
        
        price = prices[code]['price']
        pe = prices[code]['pe']
        
        if pe <= 0:
            continue
        
        pos = next((p for p in pm.data['positions'] if p['code'] == code), None)
        
        # 卖出
        if pos and pe > SELL_PE:
            amount = pos['amount']
            reason = f"PE={pe:.1f}>{SELL_PE}高估卖出"
            pm.sell(code, amount, price, reason)
            actions.append(f"卖出 {name} {amount}股 @¥{price:.2f}")
        
        # 买入
        elif not pos and pe < BUY_PE:
            available = pm.data['cash'] * 0.2
            if available >= price * 100:
                amount = int(available / price / 100) * 100
                reason = f"PE={pe:.1f}<{BUY_PE}低估买入"
                pm.buy(code, name, amount, price, reason)
                actions.append(f"买入 {name} {amount}股 @¥{price:.2f}")
        
        # 信号
        if pe < BUY_PE and not pos:
            signals.append(f"{name} PE:{pe:.1f} 买入信号")
        elif pe > SELL_PE and pos:
            signals.append(f"{name} PE:{pe:.1f} 卖出信号")
    
    pm._save_data()
    
    # 计算市值（用实时价格）
    total_value = 0
    total_cost = 0
    for p in pm.data['positions']:
        code = p['code']
        cost = p['cost'] * p['amount']
        total_cost += cost
        if code in prices:
            total_value += prices[code]['price'] * p['amount']
        else:
            total_value += cost  # 无价格时用成本
    
    profit = total_value - total_cost
    profit_pct = profit / total_cost * 100 if total_cost > 0 else 0
    total_assets = pm.data['cash'] + total_value
    
    report = []
    report.append(f"自动交易报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("━━━━━━━━━━━━━━━━━━")
    
    if actions:
        report.append("交易执行:")
        for a in actions:
            report.append(a)
    else:
        report.append("今日无交易")
    
    report.append("━━━━━━━━━━━━━━━━━━")
    report.append(f"持仓状态:")
    report.append(f"  总市值: {total_value:,.0f}元")
    report.append(f"  盈亏: {profit:,.0f}元 ({profit_pct:+.2f}%)")
    report.append(f"  现金: {pm.data['cash']:,.0f}元")
    report.append(f"  总资产: {total_assets:,.0f}元")
    
    if signals:
        report.append("━━━━━━━━━━━━━━━━━━")
        report.append("信号列表:")
        for s in signals:
            report.append(f"  {s}")
    
    report.append("━━━━━━━━━━━━━━━━━━")
    report.append("仅供参考，不构成投资建议")
    
    full_report = '\n'.join(report)
    print('\n' + full_report)
    
    report_file = os.path.join(DATA_DIR, f'auto_trade_{datetime.now().strftime("%Y%m%d")}.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    return full_report

if __name__ == '__main__':
    main()

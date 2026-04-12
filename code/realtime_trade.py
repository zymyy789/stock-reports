# -*- coding: utf-8 -*-
"""实时监控交易 - 交易时段内定时运行"""
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from analysis.fetcher import StockFetcher
from analysis.portfolio_manager import PortfolioManager

def check_and_trade():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # 只在交易时段运行 (9:30-11:30, 13:00-15:00)
    if not ((9 <= hour < 12 and minute >= 30) or (13 <= hour < 15)):
        print(f"[{now.strftime('%H:%M')}] 非交易时段，跳过")
        return
    
    print(f"[{now.strftime('%H:%M')}] 实时监控开始")
    
    pm = PortfolioManager()
    sf = StockFetcher()
    
    watchlist = [
        ('601166', '兴业银行'), ('600036', '招商银行'), ('601318', '中国平安'),
        ('600030', '中信证券'), ('600887', '伊利股份'), ('000858', '五粮液'),
        ('000333', '美的集团'), ('600519', '贵州茅台'), ('601328', '交通银行'),
        ('601818', '光大银行'), ('600016', '民生银行'), ('601288', '农业银行'),
    ]
    
    actions = []
    
    for code, name in watchlist:
        d = sf.get_a_stock_price(code)
        if not d:
            continue
        
        price = d['price']
        pe = d.get('pe', 0)
        
        if pe <= 0:
            continue
        
        pos = next((p for p in pm.data['positions'] if p['code'] == code), None)
        
        # 卖出信号 (PE>30)
        if pos and pe > 30:
            amount = pos['amount']
            pm.sell(code, amount, price, f"PE={pe:.1f}>30高估卖出")
            actions.append(f"卖出 {name} {amount}股@¥{price:.2f} PE:{pe:.1f}")
        
        # 买入信号 (PE<15)
        elif not pos and pe < 15:
            available = pm.data['cash'] * 0.15  # 每次15%资金
            if available >= price * 100:
                amount = int(available / price / 100) * 100
                pm.buy(code, name, amount, price, f"PE={pe:.1f}<15低估买入")
                actions.append(f"买入 {name} {amount}股@¥{price:.2f} PE:{pe:.1f}")
    
    if actions:
        pm._save_data()
        print("交易执行:")
        for a in actions:
            print(f"  {a}")
    else:
        print("无交易信号")

if __name__ == '__main__':
    check_and_trade()

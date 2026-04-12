# -*- coding: utf-8 -*-
"""
Corrected Morning Report
"""
import sys, json
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from analysis.fetcher import StockFetcher

fetcher = StockFetcher()

with open('data/portfolio.json', 'r', encoding='utf-8') as f:
    portfolio = json.load(f)

positions = portfolio.get('positions', [])
cash = portfolio.get('cash', 0)

name_map = {
    '601166': '兴业银行', '600036': '招商银行', '601318': '中国平安',
    '600030': '中信证券', '600887': '伊利股份', '000858': '五粮液',
    '000333': '美的集团', '601328': '交通银行', '601818': '光大银行',
    '600016': '民生银行', '601288': '农业银行', '000001': '平安银行'
}

print("="*70)
print("Morning Report - 2026-04-10 06:25")
print("="*70)

total_market = 0.0
results = []

for p in positions:
    code = p['code']
    name = name_map.get(code, p.get('name', code))
    amount = float(p['amount'])
    cost_per_share = float(p['cost'])
    
    total_cost_pos = amount * cost_per_share
    
    data = fetcher.get_a_stock_price(code)
    if data:
        price = data.get('price', 0)
        pe = data.get('pe', None)
        
        market_value = price * amount
        gain = (market_value - total_cost_pos) / total_cost_pos * 100
        
        total_market += market_value
        
        pe_str = str(round(pe, 1)) if pe and pe > 0 else 'N/A'
        
        results.append({
            'name': name, 'code': code, 'price': price,
            'amount': amount, 'cost_per': cost_per_share,
            'total_cost': total_cost_pos, 'market': market_value,
            'gain': gain, 'pe': pe_str
        })
        
        status = "OK" if gain >= 0 else "LOSS"
        print(f"{name}: price={price}, shares={amount}, cost={cost_per_share}, total_cost={total_cost_pos:.0f}, mkt={market_value:.0f}, gain={gain:+.1f}% [{status}] PE={pe_str}")
    else:
        print(f"{name}: FETCH FAILED")

total_assets = cash + total_market
total_cost_basis = sum(r['total_cost'] for r in results)
overall_gain = (total_assets - 100000) / 100000 * 100

print()
print(f"Cash: {cash:,.0f}")
print(f"Total Cost Basis: {total_cost_basis:,.0f}")
print(f"Total Market Value: {total_market:,.0f}")
print(f"Total Assets: {total_assets:,.0f}")
print(f"Overall Portfolio Gain: {overall_gain:+.1f}%")
print("="*70)

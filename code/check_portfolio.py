import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/portfolio.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== 持仓检查 ===')
print('Cash:', data.get('cash'))
positions = data.get('positions', [])
print('Positions:', len(positions))
total_cost = data.get('cash', 0)
for p in positions:
    c = p['cost'] * p['amount']
    total_cost += c
    print(f"  {p['name']}({p['code']}): {p['amount']}股 x {p['cost']} = {c:.2f}")
print(f'Total invested: {total_cost:.2f}')

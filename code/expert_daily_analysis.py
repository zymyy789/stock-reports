# -*- coding: utf-8 -*-
"""
专家级每日持仓分析 - 2026-04-11
实战数据驱动，不做理论推演
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import time
from datetime import datetime

# ============================================================
# 1. 获取实时行情数据
# ============================================================

class RealTimeData:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_tencent_quote(self, code):
        """腾讯财经实时行情"""
        # 腾讯格式: sh600036 或 sz000001
        prefix = 'sh' if code.startswith('6') else 'sz'
        url = f'http://qt.gtimg.cn/q={prefix}{code}'
        try:
            resp = self.session.get(url, timeout=5)
            data = resp.text
            if 'pv_none_match' in data or '~' not in data:
                return None
            fields = data.split('~')
            if len(fields) < 50:
                return None
            return {
                'name': fields[1],
                'code': code,
                'price': float(fields[3]),
                'yesterday_close': float(fields[4]),
                'open': float(fields[5]),
                'high': float(fields[33]),
                'low': float(fields[34]),
                'volume': int(fields[6]),
                'amount': float(fields[37]) / 10000,  # 万元
                'pe': float(fields[39]) if fields[39] else None,
                'pb': float(fields[46]) if fields[46] else None,
                'change_pct': ((float(fields[3]) - float(fields[4])) / float(fields[4])) * 100,
                'market_cap': float(fields[45]) if fields[45] else None,  # 总市值(亿)
            }
        except Exception as e:
            return None

# ============================================================
# 2. 持仓配置
# ============================================================

PORTFOLIO = {
    "cash": 13660.0,
    "positions": [
        {"code": "601166", "name": "兴业银行", "cost": 18.66, "amount": 600, "industry": "银行"},
        {"code": "600036", "name": "招商银行", "cost": 39.27, "amount": 300, "industry": "银行"},
        {"code": "601318", "name": "中国平安", "cost": 58.36, "amount": 200, "industry": "保险"},
        {"code": "600030", "name": "中信证券", "cost": 24.28, "amount": 300, "industry": "券商"},
        {"code": "600887", "name": "伊利股份", "cost": 26.04, "amount": 100, "industry": "消费"},
        {"code": "000858", "name": "五粮液",   "cost": 100.00, "amount": 102.6, "industry": "白酒"},
        {"code": "000333", "name": "美的集团", "cost": 100.00, "amount": 76.52, "industry": "家电"},
        {"code": "601328", "name": "交通银行", "cost": 6.84, "amount": 1000, "industry": "银行"},
        {"code": "601818", "name": "光大银行", "cost": 3.19, "amount": 1900, "industry": "银行"},
        {"code": "600016", "name": "民生银行", "cost": 3.70, "amount": 1300, "industry": "银行"},
        {"code": "601288", "name": "农业银行", "cost": 6.60, "amount": 600, "industry": "银行"},
        {"code": "000001", "name": "平安银行", "cost": 11.10, "amount": 200, "industry": "银行"},
    ]
}

# ============================================================
# 3. 执行分析
# ============================================================

def main():
    fetcher = RealTimeData()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"{'='*70}")
    print(f"专家级每日持仓分析 - {today}")
    print(f"{'='*70}")
    
    # 获取所有行情
    results = []
    total_market = 0
    total_cost = 0
    industry_market = {}
    industry_cost = {}
    
    for pos in PORTFOLIO['positions']:
        quote = fetcher.get_tencent_quote(pos['code'])
        if quote:
            market_val = quote['price'] * pos['amount']
            cost_val = pos['cost'] * pos['amount']
            gain_pct = (quote['price'] - pos['cost']) / pos['cost'] * 100
            
            results.append({
                **quote,
                'cost': pos['cost'],
                'amount': pos['amount'],
                'industry': pos['industry'],
                'market_val': market_val,
                'cost_val': cost_val,
                'gain_pct': gain_pct,
            })
            
            total_market += market_val
            total_cost += cost_val
            
            ind = pos['industry']
            industry_market[ind] = industry_market.get(ind, 0) + market_val
            industry_cost[ind] = industry_cost.get(ind, 0) + cost_val
        else:
            results.append({
                'name': pos['name'], 'code': pos['code'],
                'price': 0, 'cost': pos['cost'], 'amount': pos['amount'],
                'industry': pos['industry'], 'market_val': 0, 'cost_val': pos['cost'] * pos['amount'],
                'gain_pct': 0, 'pe': None, 'pb': None, 'change_pct': 0,
                'market_cap': None, 'volume': 0, 'amount': pos['amount']
            })
            total_market += 0
            total_cost += pos['cost'] * pos['amount']
            
            ind = pos['industry']
            industry_market[ind] = industry_market.get(ind, 0) + 0
            industry_cost[ind] = industry_cost.get(ind, 0) + pos['cost'] * pos['amount']
        
        time.sleep(0.3)  # 避免频繁请求
    
    total_assets = total_market + PORTFOLIO['cash']
    overall_gain = (total_assets - 100000) / 100000 * 100
    
    # ============================================================
    # 4. 输出报告
    # ============================================================
    
    print(f"\n一、组合概况")
    print(f"{'─'*50}")
    print(f"总资产: {total_assets:,.0f}")
    print(f"持仓市值: {total_market:,.0f}")
    print(f"现金: {PORTFOLIO['cash']:,.0f}")
    print(f"总成本: {total_cost:,.0f}")
    print(f"累计盈亏: {overall_gain:+.1f}%")
    
    print(f"\n二、持仓明细")
    print(f"{'─'*50}")
    print(f"{'名称':<8} {'现价':>7} {'成本':>7} {'盈亏':>7} {'市值':>8} {'权重':>6} {'PE':>6} {'信号'}")
    print(f"{'─'*70}")
    
    signals = []
    for r in results:
        if r['price'] > 0:
            weight = r['market_val'] / total_assets * 100
            pe_str = f"{r['pe']:.1f}" if r['pe'] else "N/A"
            
            # 信号判断
            signal = "持有"
            if r['pe'] and r['pe'] < 6:
                signal = "超低"
            elif r['pe'] and r['pe'] < 8:
                signal = "低估"
            elif r['pe'] and r['pe'] > 20:
                signal = "偏高"
            
            print(f"{r['name']:<7} {r['price']:>7.2f} {r['cost']:>7.2f} {r['gain_pct']:>+6.1f}% {r['market_val']:>8,.0f} {weight:>5.1f}% {pe_str:>6} {signal}")
            
            if signal in ['超低', '低估']:
                signals.append(f"{r['name']}PE={r['pe']:.1f} {signal}")
        else:
            print(f"{r['name']:<7} {'N/A':>7} {r['cost']:>7.2f} {'N/A':>7} {r['cost_val']:>8,.0f} {'N/A':>6}")
    
    # ============================================================
    # 5. 行业分布
    # ============================================================
    
    print(f"\n三、行业分布")
    print(f"{'─'*50}")
    for ind in sorted(industry_market.keys(), key=lambda x: industry_market.get(x, 0), reverse=True):
        mkt = industry_market[ind]
        if mkt > 0:
            pct = mkt / total_assets * 100
            warn = " ⚠️超配" if pct > 40 else ""
            print(f"  {ind}: {mkt:,.0f} ({pct:.1f}%){warn}")
        else:
            pct = industry_cost[ind] / total_assets * 100
            print(f"  {ind}: 获取行情失败")
    
    # ============================================================
    # 6. 专家级分析
    # ============================================================
    
    print(f"\n四、专家级分析")
    print(f"{'─'*50}")
    
    # 按PE排序找最低估
    pe_sorted = [(r['name'], r['pe']) for r in results if r.get('pe') and r['pe'] > 0]
    pe_sorted.sort(key=lambda x: x[1])
    
    if pe_sorted:
        print(f"估值最低(按PE):")
        for name, pe in pe_sorted[:5]:
            print(f"  {name}: PE={pe:.1f}")
    
    # 行业集中度
    bank_pct = industry_market.get('银行', 0) / total_assets * 100 if total_assets > 0 else 0
    if bank_pct > 40:
        print(f"\n⚠️ 风险提示: 银行仓位{bank_pct:.1f}%，超过40%警戒线")
        print(f"  建议: 减持小银行(交行/光大/民生/平安银行)，集中招行+兴业")
    
    # 现金比例
    cash_pct = PORTFOLIO['cash'] / total_assets * 100
    print(f"\n现金比例: {cash_pct:.1f}%")
    if cash_pct < 10:
        print(f"  ⚠️ 现金不足10%，缺乏加仓能力")
    elif cash_pct > 20:
        print(f"  ✅ 现金充裕，有加仓空间")
    
    # 今日涨跌
    up_count = sum(1 for r in results if r.get('change_pct', 0) > 0)
    down_count = sum(1 for r in results if r.get('change_pct', 0) < 0)
    print(f"\n今日表现: {up_count}涨 {down_count}跌 {len(results)-up_count-down_count}平")
    
    # ============================================================
    # 7. 操作建议
    # ============================================================
    
    print(f"\n五、操作建议")
    print(f"{'─'*50}")
    
    # 找出低估且仓位轻的
    for r in results:
        if r.get('pe') and r['pe'] < 7 and r['market_val'] > 0:
            weight = r['market_val'] / total_assets * 100
            if weight < 10:
                print(f"  加仓候选: {r['name']} PE={r['pe']:.1f} 仓位{weight:.1f}%")
    
    # 找出仓位太小没意义的
    for r in results:
        if r['market_val'] > 0:
            weight = r['market_val'] / total_assets * 100
            if weight < 2:
                print(f"  清仓候选: {r['name']} 仓位仅{weight:.1f}%，管理成本>收益")
    
    print(f"\n{'='*70}")
    print(f"分析完成")
    print(f"{'='*70}")
    
    # 保存结果
    with open(r'C:\Users\zymyy\.qclaw\workspace\stock_work\learning\daily_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'total_assets': total_assets,
            'total_market': total_market,
            'cash': PORTFOLIO['cash'],
            'overall_gain_pct': overall_gain,
            'positions': [{
                'name': r['name'],
                'code': r['code'],
                'price': r['price'],
                'cost': r['cost'],
                'gain_pct': r['gain_pct'],
                'pe': r['pe'],
                'pb': r['pb'],
                'market_val': r['market_val'],
                'industry': r['industry'],
            } for r in results]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 daily_analysis_result.json")

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""初始化模拟持仓 - 基于估值体系选择标的"""
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from analysis.portfolio_manager import PortfolioManager
from analysis.fetcher import StockFetcher

def init_portfolio():
    pm = PortfolioManager()
    
    # 检查是否已有持仓
    if pm.data['positions']:
        print(f"已有 {len(pm.data['positions'])} 个持仓，跳过初始化")
        return
    
    stock_fetcher = StockFetcher()
    
    # 低估值股票候选
    candidates = [
        ('601166', '兴业银行', 0.15),  # PE约5
        ('600036', '招商银行', 0.20),  # PE约7
        ('601318', '中国平安', 0.20),  # PE约8
        ('600030', '中信证券', 0.15),  # PE约12
        ('600887', '伊利股份', 0.15),  # PE约21
    ]
    
    # 根据PE分配仓位
    total_alloc = 0.5  # 投入50%资金
    cash = pm.data['cash'] * total_alloc
    
    for code, name, weight in candidates:
        data = stock_fetcher.get_a_stock_price(code)
        if data and data.get('price', 0) > 0:
            price = data['price']
            pe = data.get('pe', 0)
            
            # 根据PE调整权重
            if pe < 10:
                actual_weight = weight * 1.5  # 低PE增加权重
            elif pe > 20:
                actual_weight = weight * 0.5  # 高PE减少权重
            else:
                actual_weight = weight
            
            amount = int((cash * actual_weight) / price / 100) * 100  # 按手买
            
            if amount > 0:
                result = pm.buy(code, name, price, amount, 'stock', 
                              reason=f'PE={pe:.1f}, {name}被低估')
                if result['success']:
                    print(f"买入 {name}({code}): 价格={price}, 数量={amount}, 理由=PE={pe:.1f}")
    
    # 显示最终持仓
    portfolio = pm.get_portfolio_value()
    print(f"\n初始化完成!")
    print(f"现金: ¥{portfolio['cash']:.2f}")
    print(f"持仓市值: ¥{portfolio['total_value']:.2f}")
    print(f"总资产: ¥{portfolio['total_assets']:.2f}")

if __name__ == '__main__':
    init_portfolio()

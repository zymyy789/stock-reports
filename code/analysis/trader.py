"""
模拟交易模块 - 持仓管理和交易决策
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from config import INITIAL_CAPITAL, DATA_DIR

# 确保 DATA_DIR 是绝对路径
if not os.path.isabs(DATA_DIR):
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), DATA_DIR)

class SimTrader:
    """模拟交易器"""
    
    def __init__(self, capital: float = INITIAL_CAPITAL, portfolio_file: str = None):
        self.capital = capital
        self.initial_capital = capital
        self.positions = {}  # {code: {amount, cost, buy_date}}
        
        if portfolio_file is None:
            portfolio_file = os.path.join(DATA_DIR, 'portfolio.json')
        self.portfolio_file = portfolio_file
        
        self.load_portfolio()
    
    def load_portfolio(self):
        """加载持仓"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.capital = data.get('capital', self.capital)
                    self.positions = data.get('positions', {})
                    self.initial_capital = data.get('initial_capital', self.initial_capital)
            except:
                pass
    
    def save_portfolio(self):
        """保存持仓"""
        os.makedirs(DATA_DIR, exist_ok=True)
        data = {
            'capital': self.capital,
            'positions': self.positions,
            'initial_capital': self.initial_capital,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def buy(self, code: str, name: str, price: float, amount: int = None, max_amount: int = None) -> bool:
        """买入股票"""
        # 验证输入
        if not price or price <= 0:
            print(f"  警告: 价格无效 {price}")
            return False
        
        if amount is None and max_amount is None:
            # 默认用30%资金买入
            available = self.capital * 0.3
            # 至少买1手（100股）
            amount = max(100, int(available / price / 100) * 100)
        
        if max_amount:
            # 确保至少买1手
            amount = max(100, min(max_amount, int(self.capital / price / 100) * 100))
        
        if amount <= 0:
            amount = 100  # 强制至少1手
        
        cost = amount * price
        if cost > self.capital:
            amount = int(self.capital / price / 100) * 100
            cost = amount * price
        
        if amount <= 0:
            return False
        
        if code in self.positions:
            # 追加持仓
            old = self.positions[code]
            total_cost = old['cost'] * old['amount'] + cost
            total_amount = old['amount'] + amount
            self.positions[code] = {
                'amount': total_amount,
                'cost': total_cost / total_amount,
                'buy_date': old['buy_date'],
                'name': name
            }
        else:
            self.positions[code] = {
                'amount': amount,
                'cost': price,
                'buy_date': datetime.now().strftime('%Y-%m-%d'),
                'name': name
            }
        
        self.capital -= cost
        self.save_portfolio()
        return True
    
    def sell(self, code: str, price: float, amount: int = None) -> bool:
        """卖出股票"""
        if code not in self.positions:
            return False
        
        position = self.positions[code]
        if amount is None:
            amount = position['amount']
        
        amount = min(amount, position['amount'])
        proceeds = amount * price
        
        position['amount'] -= amount
        if position['amount'] <= 0:
            del self.positions[code]
        
        self.capital += proceeds
        self.save_portfolio()
        return True
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """计算组合市值"""
        total = self.capital
        for code, pos in self.positions.items():
            price = current_prices.get(code, pos['cost'])
            total += pos['amount'] * price
        return total
    
    def get_positions_summary(self, current_prices: Dict[str, float]) -> List[Dict]:
        """获取持仓摘要"""
        summary = []
        for code, pos in self.positions.items():
            current_price = current_prices.get(code, pos['cost'])
            cost = pos['cost']
            amount = pos['amount']
            value = amount * current_price
            cost_value = amount * cost
            profit = value - cost_value
            profit_pct = (profit / cost_value * 100) if cost_value > 0 else 0
            
            summary.append({
                'code': code,
                'name': pos.get('name', code),
                'amount': amount,
                'cost': cost,
                'current_price': current_price,
                'value': value,
                'profit': profit,
                'profit_pct': profit_pct,
                'buy_date': pos.get('buy_date', '')
            })
        
        # 按盈亏排序
        summary.sort(key=lambda x: x['profit_pct'], reverse=True)
        return summary
    
    def analyze_positions(self, current_prices: Dict[str, float]) -> List[Dict]:
        """分析持仓，给出操作建议"""
        analysis = []
        for code, pos in self.positions.items():
            current_price = current_prices.get(code, pos['cost'])
            cost = pos['cost']
            profit_pct = (current_price - cost) / cost * 100 if cost > 0 else 0
            
            # 决策逻辑
            if profit_pct > 15:
                action = "卖出"  # 止盈
                reason = f"涨幅{profit_pct:.1f}%，超过15%止盈线"
            elif profit_pct < -10:
                action = "止损"  # 止损
                reason = f"跌幅{abs(profit_pct):.1f}%，超过10%止损线"
            elif profit_pct > 8:
                action = "持有"  # 继续持有
                reason = f"涨幅{profit_pct:.1f}%，可继续持有"
            else:
                action = "持有"
                reason = "正常持有区间"
            
            analysis.append({
                'code': code,
                'name': pos.get('name', code),
                'current_price': current_price,
                'cost': cost,
                'profit_pct': profit_pct,
                'action': action,
                'reason': reason
            })
        
        return analysis


if __name__ == "__main__":
    trader = SimTrader()
    print(f"初始资金: {trader.initial_capital}")
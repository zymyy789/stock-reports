"""
持仓管理系统
- 记录买入/卖出
- 成本均价计算
- 盈亏追踪
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Position:
    """持仓记录"""
    code: str
    name: str
    amount: int  # 持仓数量
    cost: float  # 总成本
    avg_cost: float  # 成本均价
    first_buy_date: str  # 首次买入日期
    last_update: str  # 最后更新日期
    
    @property
    def current_value(self) -> float:
        return 0  # 需要实时价格计算
    
    @property
    def profit(self) -> float:
        return 0  # 需要实时价格计算


class PositionManager:
    """持仓管理器"""
    
    def __init__(self, portfolio_file: str = None):
        if portfolio_file is None:
            portfolio_file = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'portfolio.json'
            )
        self.portfolio_file = portfolio_file
        self.positions: Dict[str, Dict] = {}
        self.load()
    
    def load(self):
        """从文件加载持仓"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
            except:
                self.positions = {}
    
    def save(self):
        """保存持仓到文件"""
        os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=2)
    
    def buy(self, code: str, name: str, amount: int, price: float, date: str = None) -> Dict:
        """
        买入操作
        返回: 操作结果
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        total_cost = amount * price
        
        if code in self.positions:
            # 已有持仓，加仓
            pos = self.positions[code]
            new_amount = pos['amount'] + amount
            new_cost = pos['cost'] + total_cost
            new_avg_cost = new_cost / new_amount
            
            pos['amount'] = new_amount
            pos['cost'] = new_cost
            pos['avg_cost'] = new_avg_cost
            pos['last_update'] = date
            
            result = {
                'action': 'add',
                'code': code,
                'name': name,
                'amount': amount,
                'price': price,
                'total': total_cost,
                'new_avg_cost': new_avg_cost,
                'message': f"加仓 {name} {amount}股 @ {price:.2f}元，均价调整为 {new_avg_cost:.2f}元"
            }
        else:
            # 新建持仓
            self.positions[code] = {
                'code': code,
                'name': name,
                'amount': amount,
                'cost': total_cost,
                'avg_cost': price,
                'first_buy_date': date,
                'last_update': date
            }
            
            result = {
                'action': 'new',
                'code': code,
                'name': name,
                'amount': amount,
                'price': price,
                'total': total_cost,
                'message': f"新建持仓 {name} {amount}股 @ {price:.2f}元"
            }
        
        self.save()
        return result
    
    def sell(self, code: str, amount: int, price: float, date: str = None) -> Dict:
        """
        卖出操作
        返回: 操作结果
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if code not in self.positions:
            return {'error': f'没有 {code} 的持仓'}
        
        pos = self.positions[code]
        
        if amount > pos['amount']:
            return {'error': f'持仓不足，当前持有 {pos["amount"]} 股'}
        
        sell_value = amount * price
        cost_value = amount * pos['avg_cost']
        profit = sell_value - cost_value
        
        if amount == pos['amount']:
            # 全部卖出
            del self.positions[code]
            message = f"清仓 {pos['name']} {amount}股 @ {price:.2f}元，盈利 {profit:.2f}元"
        else:
            # 部分卖出
            pos['amount'] -= amount
            pos['cost'] -= cost_value
            pos['last_update'] = date
            message = f"减仓 {pos['name']} {amount}股 @ {price:.2f}元，盈利 {profit:.2f}元"
        
        self.save()
        
        return {
            'action': 'sell',
            'code': code,
            'name': pos['name'],
            'amount': amount,
            'price': price,
            'sell_value': sell_value,
            'profit': profit,
            'message': message
        }
    
    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        return list(self.positions.values())
    
    def get_position(self, code: str) -> Optional[Dict]:
        """获取指定持仓"""
        return self.positions.get(code)
    
    def update_prices(self, prices: Dict[str, float]):
        """
        更新持仓的当前价格，计算盈亏
        prices: {code: price}
        """
        for code, pos in self.positions.items():
            if code in prices:
                pos['current_price'] = prices[code]
                pos['current_value'] = pos['amount'] * prices[code]
                pos['profit'] = pos['current_value'] - pos['cost']
                pos['profit_pct'] = (pos['profit'] / pos['cost'] * 100) if pos['cost'] > 0 else 0
    
    def get_portfolio_summary(self) -> Dict:
        """获取组合概览"""
        total_cost = sum(p['cost'] for p in self.positions.values())
        total_value = sum(p.get('current_value', 0) for p in self.positions.values())
        total_profit = total_value - total_cost
        profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        # 持仓数量
        position_count = len(self.positions)
        
        # 持仓明细
        details = []
        for pos in self.positions.values():
            details.append({
                'code': pos['code'],
                'name': pos['name'],
                'amount': pos['amount'],
                'avg_cost': pos['avg_cost'],
                'current_price': pos.get('current_price', 0),
                'current_value': pos.get('current_value', 0),
                'profit': pos.get('profit', 0),
                'profit_pct': pos.get('profit_pct', 0),
                'first_buy_date': pos['first_buy_date']
            })
        
        # 按盈亏排序
        details.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        return {
            'total_cost': total_cost,
            'total_value': total_value,
            'total_profit': total_profit,
            'profit_pct': profit_pct,
            'position_count': position_count,
            'positions': details
        }
    
    def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """获取交易历史"""
        # 简化：从持仓推断的交易记录
        # 实际应该记录完整的交易历史
        history = []
        for pos in self.positions.values():
            history.append({
                'date': pos['first_buy_date'],
                'action': 'buy',
                'code': pos['code'],
                'name': pos['name'],
                'amount': pos['amount'],
                'price': pos['avg_cost']
            })
        
        history.sort(key=lambda x: x['date'], reverse=True)
        return history[:limit]
    
    def clear(self):
        """清空所有持仓"""
        self.positions = {}
        self.save()


# 测试
if __name__ == "__main__":
    pm = PositionManager()
    
    # 测试买入
    print("测试买入:")
    result = pm.buy('600519', '贵州茅台', 100, 1500.0)
    print(result['message'])
    
    result = pm.buy('601166', '兴业银行', 1000, 18.0)
    print(result['message'])
    
    # 测试加仓
    result = pm.buy('601166', '兴业银行', 500, 17.5)
    print(result['message'])
    
    # 获取持仓
    print("\n当前持仓:")
    positions = pm.get_positions()
    for p in positions:
        print(f"  {p['name']}: {p['amount']}股, 均价 {p['avg_cost']:.2f}元")
    
    # 更新价格
    prices = {
        '600519': 1550.0,
        '601166': 18.5
    }
    pm.update_prices(prices)
    
    # 组合概览
    summary = pm.get_portfolio_summary()
    print(f"\n组合概览:")
    print(f"  总成本: {summary['total_cost']:.2f}元")
    print(f"  当前价值: {summary['total_value']:.2f}元")
    print(f"  总盈亏: {summary['total_profit']:.2f}元 ({summary['profit_pct']:.2f}%)")

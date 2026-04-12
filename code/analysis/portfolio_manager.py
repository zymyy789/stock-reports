# -*- coding: utf-8 -*-
"""
模拟持仓管理系统 - 基于真实数据的模拟交易
验证估值体系的有效性
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')

from analysis.fetcher import StockFetcher
from analysis.fund_fetcher import FundFetcher

class PortfolioManager:
    """模拟持仓管理器"""
    
    def __init__(self, data_file: str = None):
        if data_file is None:
            data_file = r'C:\Users\zymyy\.qclaw\workspace\stock_work\data\portfolio.json'
        self.data_file = data_file
        self.stock_fetcher = StockFetcher()
        self.fund_fetcher = FundFetcher()
        self._ensure_data_dir()
        self.data = self._load_data()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _load_data(self) -> Dict:
        """加载持仓数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        # 初始数据
        return {
            'cash': 100000.0,  # 初始资金10万
            'positions': [],   # 持仓列表
            'history': [],     # 交易历史
            'created_at': datetime.now().isoformat(),
        }
    
    def _save_data(self):
        """保存持仓数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_position(self, code: str) -> Optional[Dict]:
        """获取指定持仓"""
        for p in self.data['positions']:
            if p['code'] == code:
                return p
        return None
    
    def buy(self, code: str, name: str, price: float, amount: int, 
            item_type: str = 'stock', reason: str = '') -> Dict:
        """
        买入
        :param code: 代码
        :param name: 名称
        :param price: 买入价格
        :param amount: 数量
        :param item_type: 类型 stock/fund
        :param reason: 买入理由
        :return: 交易结果
        """
        total_cost = price * amount
        
        # 检查资金
        if total_cost > self.data['cash']:
            return {'success': False, 'error': '资金不足'}
        
        # 扣除资金
        self.data['cash'] -= total_cost
        
        # 更新或创建持仓
        position = self.get_position(code)
        if position:
            # 已有持仓，更新成本
            old_amount = position['amount']
            old_cost = position['cost']
            new_amount = old_amount + amount
            new_cost = (old_cost * old_amount + price * amount) / new_amount
            position['amount'] = new_amount
            position['cost'] = new_cost
        else:
            # 新建持仓
            position = {
                'code': code,
                'name': name,
                'type': item_type,
                'cost': price,
                'amount': amount,
                'created_at': datetime.now().isoformat(),
            }
            self.data['positions'].append(position)
        
        # 记录交易历史
        trade = {
            'action': 'buy',
            'code': code,
            'name': name,
            'price': price,
            'amount': amount,
            'total': total_cost,
            'reason': reason,
            'date': datetime.now().isoformat(),
        }
        self.data['history'].append(trade)
        self._save_data()
        
        return {
            'success': True,
            'trade': trade,
            'cash': self.data['cash'],
        }
    
    def sell(self, code: str, price: float, amount: int, 
             reason: str = '') -> Dict:
        """
        卖出
        :param code: 代码
        :param price: 卖出价格
        :param amount: 数量
        :param reason: 卖出理由
        :return: 交易结果
        """
        position = self.get_position(code)
        if not position:
            return {'success': False, 'error': '未持有该股票'}
        
        if amount > position['amount']:
            return {'success': False, 'error': '持仓不足'}
        
        total_value = price * amount
        profit = (price - position['cost']) * amount
        profit_pct = (price - position['cost']) / position['cost'] * 100
        
        # 增加资金
        self.data['cash'] += total_value
        
        # 更新持仓
        position['amount'] -= amount
        if position['amount'] == 0:
            self.data['positions'].remove(position)
        
        # 记录交易历史
        trade = {
            'action': 'sell',
            'code': code,
            'name': position['name'],
            'price': price,
            'amount': amount,
            'total': total_value,
            'profit': profit,
            'profit_pct': profit_pct,
            'reason': reason,
            'date': datetime.now().isoformat(),
        }
        self.data['history'].append(trade)
        self._save_data()
        
        return {
            'success': True,
            'trade': trade,
            'profit': profit,
            'profit_pct': profit_pct,
            'cash': self.data['cash'],
        }
    
    def get_portfolio_value(self) -> Dict:
        """获取当前持仓市值（基于实时价格）"""
        total_cost = 0
        total_value = 0
        positions_detail = []
        
        for p in self.data['positions']:
            code = p['code']
            item_type = p['type']
            
            # 获取实时价格
            if item_type == 'stock':
                data = self.stock_fetcher.get_a_stock_price(code)
                current_price = data.get('price', 0) if data else 0
            else:
                data = self.fund_fetcher.get_fund_basic_info(code)
                current_price = data.get('net_value', 0) if data else 0
            
            cost = p['cost'] * p['amount']
            value = current_price * p['amount']
            profit = value - cost
            profit_pct = (profit / cost * 100) if cost > 0 else 0
            
            total_cost += cost
            total_value += value
            
            positions_detail.append({
                'code': code,
                'name': p['name'],
                'type': item_type,
                'cost_price': p['cost'],
                'current_price': current_price,
                'amount': p['amount'],
                'cost': cost,
                'value': value,
                'profit': profit,
                'profit_pct': profit_pct,
            })
        
        total_profit = total_value - total_cost
        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
        total_assets = self.data['cash'] + total_value
        
        return {
            'cash': self.data['cash'],
            'total_cost': total_cost,
            'total_value': total_value,
            'total_profit': total_profit,
            'total_profit_pct': total_profit_pct,
            'total_assets': total_assets,
            'positions': positions_detail,
            'update_time': datetime.now().isoformat(),
        }
    
    def get_trade_history(self, days: int = 30) -> List[Dict]:
        """获取交易历史"""
        cutoff = datetime.now() - timedelta(days=days)
        history = []
        for h in self.data['history']:
            trade_date = datetime.fromisoformat(h['date'])
            if trade_date >= cutoff:
                history.append(h)
        return history
    
    def get_strategy_signals(self) -> Dict:
        """
        根据估值体系生成买卖信号
        策略：
        - PE < 10：强烈买入
        - PE 10-15：买入
        - PE 15-25：持有
        - PE > 30：卖出
        """
        signals = {
            'buy': [],
            'sell': [],
            'hold': [],
        }
        
        # 检查持仓中的卖出信号
        for p in self.data['positions']:
            if p['type'] != 'stock':
                continue
            data = self.stock_fetcher.get_a_stock_price(p['code'])
            if data and data.get('pe'):
                pe = data['pe']
                if pe > 30:
                    signals['sell'].append({
                        'code': p['code'],
                        'name': p['name'],
                        'pe': pe,
                        'reason': f'PE({pe:.1f})过高，建议卖出',
                        'current_price': data.get('price', 0),
                        'profit_pct': (data.get('price', 0) - p['cost']) / p['cost'] * 100,
                    })
        
        # 检查关注列表的买入信号
        watch_list = ['600519', '601318', '600036', '000858', '000333',
                      '601166', '600030', '600887', '600276', '601888']
        
        for code in watch_list:
            # 跳过已有持仓
            if self.get_position(code):
                continue
            
            data = self.stock_fetcher.get_a_stock_price(code)
            if data and data.get('pe'):
                pe = data['pe']
                if pe < 10:
                    signals['buy'].append({
                        'code': code,
                        'name': data.get('name', ''),
                        'pe': pe,
                        'price': data.get('price', 0),
                        'reason': f'PE({pe:.1f})极低，强烈建议买入',
                    })
                elif pe < 15:
                    signals['buy'].append({
                        'code': code,
                        'name': data.get('name', ''),
                        'pe': pe,
                        'price': data.get('price', 0),
                        'reason': f'PE({pe:.1f})偏低，建议买入',
                    })
        
        return signals
    
    def reset(self):
        """重置模拟账户"""
        self.data = {
            'cash': 100000.0,
            'positions': [],
            'history': [],
            'created_at': datetime.now().isoformat(),
        }
        self._save_data()


if __name__ == '__main__':
    # 测试
    pm = PortfolioManager()
    
    # 查看当前持仓
    portfolio = pm.get_portfolio_value()
    print(f"现金: {portfolio['cash']:.2f}")
    print(f"总市值: {portfolio['total_value']:.2f}")
    print(f"总盈亏: {portfolio['total_profit']:.2f} ({portfolio['total_profit_pct']:.2f}%)")
    print(f"总资产: {portfolio['total_assets']:.2f}")
    
    # 获取策略信号
    signals = pm.get_strategy_signals()
    print("\n买入信号:")
    for s in signals['buy']:
        print(f"  {s['name']}({s['code']}): {s['reason']}")
    
    print("\n卖出信号:")
    for s in signals['sell']:
        print(f"  {s['name']}({s['code']}): {s['reason']}")

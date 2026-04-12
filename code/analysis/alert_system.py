"""
提醒系统
- 价格突破提醒
- 估值极端值提醒
- 再平衡提醒
"""
from typing import Dict, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import os


@dataclass
class AlertRule:
    """提醒规则"""
    rule_id: str
    name: str  # 规则名称
    type: str  # 'price_above', 'price_below', 'pe_below', 'pe_above', 'pct_change', 'rebalance'
    code: str  # 股票代码
    threshold: float  # 阈值
    enabled: bool = True
    triggered: bool = False
    last_triggered: str = None  # 上次触发时间
    
    def check(self, current_value: float) -> bool:
        """检查是否触发"""
        if not self.enabled or self.triggered:
            return False
        
        if self.type == 'price_above':
            return current_value > self.threshold
        elif self.type == 'price_below':
            return current_value < self.threshold
        elif self.type == 'pe_below':
            return current_value < self.threshold
        elif self.type == 'pe_above':
            return current_value > self.threshold
        elif self.type == 'pct_change':
            return abs(current_value) > self.threshold
        
        return False


class AlertSystem:
    """提醒系统"""
    
    def __init__(self, storage_file: str = None):
        if storage_file is None:
            storage_file = os.path.join(
                os.path.dirname(__file__),
                '..', 'data', 'alerts.json'
            )
        self.storage_file = storage_file
        self.rules: List[AlertRule] = []
        self.load()
    
    def load(self):
        """加载提醒规则"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.rules = [AlertRule(**r) for r in data.get('rules', [])]
            except:
                self.rules = []
    
    def save(self):
        """保存提醒规则"""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        data = {'rules': [asdict(r) for r in self.rules]}
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_price_alert(self, code: str, name: str, price: float, direction: str = 'above') -> AlertRule:
        """
        添加价格提醒
        direction: 'above' 或 'below'
        """
        rule_type = 'price_above' if direction == 'above' else 'price_below'
        
        rule = AlertRule(
            rule_id=f"price_{code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=f"{name}价格{direction}提醒",
            type=rule_type,
            code=code,
            threshold=price
        )
        
        self.rules.append(rule)
        self.save()
        
        return rule
    
    def add_pe_alert(self, code: str, name: str, pe: float, direction: str = 'below') -> AlertRule:
        """
        添加 PE 估值提醒
        direction: 'below' 或 'above'
        """
        rule_type = 'pe_below' if direction == 'below' else 'pe_above'
        
        rule = AlertRule(
            rule_id=f"pe_{code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=f"{name} PE{direction}提醒",
            type=rule_type,
            code=code,
            threshold=pe
        )
        
        self.rules.append(rule)
        self.save()
        
        return rule
    
    def add_change_alert(self, code: str, name: str, pct_change: float) -> AlertRule:
        """添加涨跌幅提醒"""
        rule = AlertRule(
            rule_id=f"change_{code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=f"{name}涨跌幅提醒",
            type='pct_change',
            code=code,
            threshold=pct_change
        )
        
        self.rules.append(rule)
        self.save()
        
        return rule
    
    def add_rebalance_alert(self, portfolio_value: float, threshold_pct: float = 10) -> AlertRule:
        """添加再平衡提醒（当持仓偏离目标比例超过阈值时）"""
        rule = AlertRule(
            rule_id=f"rebalance_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name="组合再平衡提醒",
            type='rebalance',
            code='PORTFOLIO',
            threshold=threshold_pct
        )
        
        self.rules.append(rule)
        self.save()
        
        return rule
    
    def check_alerts(self, market_data: Dict, stock_data: Dict, fund_data: Dict) -> List[Dict]:
        """
        检查所有提醒
        返回: 触发的提醒列表
        """
        triggered = []
        
        for rule in self.rules:
            if not rule.enabled or rule.triggered:
                continue
            
            current_value = None
            
            # 获取当前值
            if rule.type in ['price_above', 'price_below']:
                # 股票价格
                if rule.code in stock_data:
                    current_value = stock_data[rule.code].get('price', 0)
            elif rule.type in ['pe_below', 'pe_above']:
                # PE
                if rule.code in stock_data:
                    current_value = stock_data[rule.code].get('pe', 0)
            elif rule.type == 'pct_change':
                # 涨跌幅
                if rule.code in stock_data:
                    current_value = stock_data[rule.code].get('change_pct', 0)
            
            # 检查是否触发
            if current_value is not None and rule.check(current_value):
                rule.triggered = True
                rule.last_triggered = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                triggered.append({
                    'rule': rule,
                    'current_value': current_value,
                    'message': f"⚠️ 触发提醒: {rule.name}, 当前值: {current_value:.2f}, 阈值: {rule.threshold:.2f}"
                })
        
        if triggered:
            self.save()
        
        return triggered
    
    def get_active_rules(self) -> List[AlertRule]:
        """获取所有启用的规则"""
        return [r for r in self.rules if r.enabled and not r.triggered]
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """获取指定规则"""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def disable_rule(self, rule_id: str):
        """禁用规则"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
            self.save()
    
    def enable_rule(self, rule_id: str):
        """启用规则"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
            self.save()
    
    def reset_rule(self, rule_id: str):
        """重置规则（允许再次触发）"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.triggered = False
            self.save()
    
    def clear_triggered(self):
        """清除所有已触发的规则"""
        self.rules = [r for r in self.rules if not r.triggered]
        self.save()
    
    def format_alert_report(self) -> str:
        """格式化提醒报告"""
        active = self.get_active_rules()
        triggered = [r for r in self.rules if r.triggered]
        
        lines = []
        lines.append("\n🔔 提醒系统状态")
        lines.append("=" * 50)
        lines.append(f"  活跃规则: {len(active)}")
        lines.append(f"  已触发: {len(triggered)}")
        
        if active:
            lines.append("\n📋 活跃提醒:")
            for r in active[:10]:
                lines.append(f"  • {r.name} - {r.code} - 阈值: {r.threshold}")
        
        if triggered:
            lines.append("\n⚠️ 已触发提醒:")
            for r in triggered:
                lines.append(f"  • {r.name} - {r.last_triggered}")
        
        return "\n".join(lines)


# 测试
if __name__ == "__main__":
    alerts = AlertSystem()
    
    # 添加测试提醒
    alerts.add_price_alert('600519', '贵州茅台', 1800, 'above')
    alerts.add_price_alert('601166', '兴业银行', 16, 'below')
    alerts.add_pe_alert('600519', '贵州茅台', 25, 'above')
    
    # 检查提醒
    stock_data = {
        '600519': {'price': 1850, 'pe': 28, 'change_pct': 2.5},
        '601166': {'price': 17.5, 'pe': 5, 'change_pct': -1.2}
    }
    
    triggered = alerts.check_alerts({}, stock_data, {})
    
    for t in triggered:
        print(t['message'])
    
    # 打印状态
    print(alerts.format_alert_report())
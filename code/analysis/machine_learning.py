"""
机器学习预测模块（谨慎使用）
- 价格趋势预测
- 异常检测
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json


class PricePredictor:
    """价格预测器（简化版，不使用真实ML模型）"""
    
    def __init__(self):
        self.model_params = {}
    
    def predict_next_day(self, prices: List[float], days_ahead: int = 1) -> Optional[float]:
        """
        预测下一日价格
        使用简单的线性回归 + 移动平均
        """
        if len(prices) < 10:
            return None
        
        # 简化：使用最近价格的加权平均
        # 权重：近期权重更高
        n = min(20, len(prices))
        recent = prices[-n:]
        
        # 线性回归斜率
        x = np.arange(n)
        y = np.array(recent)
        
        # 简化计算斜率
        slope = (recent[-1] - recent[0]) / n
        
        # 预测
        predicted = recent[-1] + slope * days_ahead
        
        return round(predicted, 2)
    
    def predict_trend(self, prices: List[float]) -> Dict:
        """
        预测趋势
        返回: 趋势判断和置信度
        """
        if len(prices) < 20:
            return {'trend': '数据不足', 'confidence': 0}
        
        # 计算近期表现
        recent_5 = prices[-5:]
        recent_20 = prices[-20:]
        
        change_5 = (recent_5[-1] - recent_5[0]) / recent_5[0] * 100
        change_20 = (recent_20[-1] - recent_20[0]) / recent_20[0] * 100
        
        # 趋势判断
        if change_5 > 5 and change_20 > 10:
            trend = '强势上涨'
            confidence = 75
        elif change_5 > 2 and change_20 > 0:
            trend = '温和上涨'
            confidence = 60
        elif change_5 < -5 and change_20 < -10:
            trend = '弱势下跌'
            confidence = 75
        elif change_5 < -2 and change_20 < 0:
            trend = '温和下跌'
            confidence = 60
        elif abs(change_5) < 2 and abs(change_20) < 5:
            trend = '震荡整理'
            confidence = 70
        else:
            trend = '方向不明'
            confidence = 40
        
        return {
            'trend': trend,
            'confidence': confidence,
            'change_5d': round(change_5, 2),
            'change_20d': round(change_20, 2)
        }
    
    def calculate_support_resistance(self, prices: List[float]) -> Dict:
        """
        计算支撑位和压力位
        """
        if len(prices) < 20:
            return {}
        
        # 简化：使用近期高低点
        recent = prices[-20:]
        
        # 支撑位：近期最低点附近
        support = min(recent)
        
        # 压力位：近期最高点附近
        resistance = max(recent)
        
        # 计算区间
        mid = (support + resistance) / 2
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'mid': round(mid, 2),
            'range': round((resistance - support) / support * 100, 2)
        }
    
    def detect_anomalies(self, prices: List[float], threshold: float = 3.0) -> List[Dict]:
        """
        异常检测
        使用 Z-score 方法检测价格异常波动
        """
        if len(prices) < 30:
            return []
        
        # 计算收益率
        returns = []
        for i in range(1, len(prices)):
            r = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(r)
        
        # 计算 Z-score
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return []
        
        anomalies = []
        
        for i, r in enumerate(returns):
            z_score = abs((r - mean_return) / std_return)
            
            if z_score > threshold:
                anomalies.append({
                    'date_index': i + 1,
                    'return': round(r * 100, 2),
                    'z_score': round(z_score, 2),
                    'type': '暴涨' if r > 0 else '暴跌'
                })
        
        return anomalies
    
    def generate_prediction_report(self, stock_code: str, prices: List[float], 
                                   current_price: float) -> str:
        """生成预测报告"""
        if len(prices) < 20:
            return f"数据不足，无法预测"
        
        # 预测
        pred_next = self.predict_next_day(prices)
        pred_5d = self.predict_next_day(prices, 5)
        
        # 趋势
        trend_info = self.predict_trend(prices)
        
        # 支撑压力
        sr = self.calculate_support_resistance(prices)
        
        # 异常检测
        anomalies = self.detect_anomalies(prices)
        
        lines = []
        lines.append(f"\n🔮 价格预测 - {stock_code}")
        lines.append("=" * 50)
        
        lines.append(f"\n当前价格: ¥{current_price:.2f}")
        
        if pred_next:
            change = (pred_next - current_price) / current_price * 100
            change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
            lines.append(f"明日预测: ¥{pred_next:.2f} ({change_str})")
        
        if pred_5d:
            change = (pred_5d - current_price) / current_price * 100
            change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
            lines.append(f"5日后预测: ¥{pred_5d:.2f} ({change_str})")
        
        lines.append(f"\n趋势判断: {trend_info['trend']}")
        lines.append(f"置信度: {trend_info['confidence']}%")
        
        if sr:
            lines.append(f"\n支撑位: ¥{sr['support']:.2f}")
            lines.append(f"压力位: ¥{sr['resistance']:.2f}")
        
        if anomalies:
            lines.append(f"\n⚠️ 异常波动: 检测到{len(anomalies)}次")
            for a in anomalies[:3]:
                lines.append(f"  • {a['type']}: {a['return']:.2f}% (Z={a['z_score']:.1f})")
        
        lines.append("\n⚠️ 声明: 此预测仅供参考，不构成投资建议")
        
        return "\n".join(lines)


class PortfolioOptimizer:
    """组合优化器"""
    
    def __init__(self):
        pass
    
    def calculate_sharpe_optimized_weights(self, returns_dict: Dict[str, List[float]]) -> Dict[str, float]:
        """
        计算最优组合权重（最大化夏普比率）
        简化版：使用等权重 + 风险调整
        """
        if not returns_dict:
            return {}
        
        # 计算每个资产的收益和风险
        asset_stats = {}
        for code, returns in returns_dict.items():
            if len(returns) < 10:
                continue
            
            mean_ret = np.mean(returns) * 252  # 年化
            std_ret = np.std(returns) * np.sqrt(252)  # 年化
            
            if std_ret > 0:
                sharpe = mean_ret / std_ret
            else:
                sharpe = 0
            
            asset_stats[code] = {
                'mean_return': mean_ret,
                'volatility': std_ret,
                'sharpe': sharpe
            }
        
        if not asset_stats:
            # 返回等权重
            return {code: 1.0 / len(returns_dict) for code in returns_dict.keys()}
        
        # 简化：基于夏普比率分配权重
        total_sharpe = sum(s['sharpe'] for s in asset_stats.values())
        
        weights = {}
        if total_sharpe > 0:
            for code, stats in asset_stats.items():
                # 权重 = 基础权重 + 夏普加成
                base_weight = 1.0 / len(asset_stats)
                sharpe_bonus = (stats['sharpe'] / total_sharpe) * 0.3
                weights[code] = base_weight + sharpe_bonus
        else:
            weights = {code: 1.0 / len(asset_stats) for code in asset_stats.keys()}
        
        # 归一化
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def rebalance_recommendation(self, current_weights: Dict[str, float], 
                                 target_weights: Dict[str, float],
                                 threshold: float = 5.0) -> List[Dict]:
        """
        生成再平衡建议
        当实际权重偏离目标超过阈值时触发
        """
        recommendations = []
        
        all_assets = set(current_weights.keys()) | set(target_weights.keys())
        
        for asset in all_assets:
            current = current_weights.get(asset, 0) * 100
            target = target_weights.get(asset, 0) * 100
            
            diff = current - target
            
            if abs(diff) > threshold:
                action = '增持' if diff < 0 else '减持'
                recommendations.append({
                    'asset': asset,
                    'current_pct': round(current, 1),
                    'target_pct': round(target, 1),
                    'change_pct': round(abs(diff), 1),
                    'action': action,
                    'reason': f"当前权重{current:.1f}%，目标{target:.1f}%，偏离{diff:.1f}%"
                })
        
        # 按偏离排序
        recommendations.sort(key=lambda x: x['change_pct'], reverse=True)
        
        return recommendations


if __name__ == "__main__":
    # 测试
    import random
    random.seed(42)
    
    # 模拟价格数据
    prices = [100]
    for i in range(100):
        change = random.normalvariate(0.001, 0.02)
        prices.append(prices[-1] * (1 + change))
    
    predictor = PricePredictor()
    
    print(predictor.generate_prediction_report('600519', prices, prices[-1]))
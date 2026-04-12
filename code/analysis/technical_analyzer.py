"""
技术指标计算模块
- MACD
- RSI
- 布林带
- KDJ
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TechnicalIndicators:
    """技术指标结果"""
    ma5: float  # 5日均线
    ma10: float  # 10日均线
    ma20: float  # 20日均线
    ma60: float  # 60日均线
    macd: float  # MACD 值
    signal: float  # 信号线
    histogram: float  # MACD 柱
    rsi: float  # RSI 值
    k: float  # KDJ K值
    d: float  # KDJ D值
    j: float  # KDJ J值
    upper: float  # 布林带上轨
    middle: float  # 布林带中轨
    lower: float  # 布林带下轨


class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self):
        pass
    
    def calculate_ma(self, prices: List[float], period: int) -> Optional[float]:
        """计算移动平均线"""
        if len(prices) < period:
            return None
        return np.mean(prices[-period:])
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """计算指数移动平均线 (EMA)"""
        if len(prices) < period:
            return None
        
        ema = prices[0]
        multiplier = 2 / (period + 1)
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_macd(self, prices: List[float], 
                       fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """
        计算 MACD
        返回: (DIF, DEA, MACD柱)
        """
        if len(prices) < slow:
            return 0, 0, 0
        
        # 计算 EMA
        ema_fast = self._ema_list(prices, fast)
        ema_slow = self._ema_list(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return 0, 0, 0
        
        dif = ema_fast - ema_slow
        
        # 计算 DEA (信号线)
        # 简化处理：用 DIF 的 EMA 作为信号线
        dea = dif * 0.9  # 简化
        
        macd = (dif - dea) * 2
        
        return round(dif, 2), round(dea, 2), round(macd, 2)
    
    def _ema_list(self, prices: List[float], period: int) -> Optional[float]:
        """计算 EMA 序列的最后一个值"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        
        # 取最近 period 个价格
        recent_prices = prices[-period:]
        
        # 计算第一个 EMA (使用 SMA)
        ema = sum(recent_prices) / period
        
        # 计算后续 EMA
        for price in recent_prices[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        计算 RSI 相对强弱指标
        """
        if len(prices) < period + 1:
            return 50.0
        
        # 计算价格变化
        deltas = []
        for i in range(1, len(prices)):
            deltas.append(prices[i] - prices[i-1])
        
        if len(deltas) < period:
            return 50.0
        
        # 取最近 period 个 delta
        recent_deltas = deltas[-period:]
        
        # 分离上涨和下跌
        gains = [d if d > 0 else 0 for d in recent_deltas]
        losses = [-d if d < 0 else 0 for d in recent_deltas]
        
        # 计算平均涨跌幅
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        # 计算 RS 和 RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
        """
        计算布林带
        返回: (上轨, 中轨, 下轨)
        """
        if len(prices) < period:
            return 0, 0, 0
        
        recent_prices = prices[-period:]
        
        # 中轨 = MA
        middle = np.mean(recent_prices)
        
        # 标准差
        std = np.std(recent_prices)
        
        # 上轨和下轨
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        return round(upper, 2), round(middle, 2), round(lower, 2)
    
    def calculate_kdj(self, prices: List[float], period: int = 9) -> Tuple[float, float, float]:
        """
        计算 KDJ 随机指标
        返回: (K, D, J)
        """
        if len(prices) < period:
            return 50, 50, 50
        
        # 取最近 period 个价格
        recent_prices = prices[-period:]
        
        highest = max(recent_prices)
        lowest = min(recent_prices)
        
        current = prices[-1]
        
        if highest == lowest:
            return 50, 50, 50
        
        # 计算 RSV
        rsv = (current - lowest) / (highest - lowest) * 100
        
        # K = 2/3 * 前K值 + 1/3 * RSV (简化：直接用 RSV)
        k = rsv
        d = k * 0.9  # 简化
        j = 3 * k - 2 * d
        
        return round(k, 2), round(d, 2), round(j, 2)
    
    def analyze(self, prices: List[float]) -> Dict:
        """
        综合技术分析
        """
        if len(prices) < 60:
            return {'error': '数据不足，需要至少60个交易日数据'}
        
        result = {}
        
        # 均线
        result['ma5'] = self.calculate_ma(prices, 5)
        result['ma10'] = self.calculate_ma(prices, 10)
        result['ma20'] = self.calculate_ma(prices, 20)
        result['ma60'] = self.calculate_ma(prices, 60)
        
        # MACD
        dif, signal, histogram = self.calculate_macd(prices)
        result['macd_dif'] = dif
        result['macd_signal'] = signal
        result['macd_histogram'] = histogram
        
        # RSI
        result['rsi'] = self.calculate_rsi(prices)
        
        # 布林带
        upper, middle, lower = self.calculate_bollinger_bands(prices)
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower
        
        # KDJ
        k, d, j = self.calculate_kdj(prices)
        result['kdj_k'] = k
        result['kdj_d'] = d
        result['kdj_j'] = j
        
        # 趋势判断
        current_price = prices[-1]
        
        # 均线趋势
        if result['ma5'] > result['ma10'] > result['ma20']:
            result['trend'] = '强势上涨'
        elif result['ma5'] < result['ma10'] < result['ma20']:
            result['trend'] = '弱势下跌'
        else:
            result['trend'] = '震荡整理'
        
        # RSI 判断
        rsi = result['rsi']
        if rsi > 80:
            result['rsi_signal'] = '超买区，注意风险'
        elif rsi < 20:
            result['rsi_signal'] = '超卖区，可能反弹'
        elif rsi > 50:
            result['rsi_signal'] = '多头区域'
        else:
            result['rsi_signal'] = '空头区域'
        
        # 布林带位置
        if current_price > upper:
            result['bb_signal'] = '突破上轨，可能回调'
        elif current_price < lower:
            result['bb_signal'] = '突破下轨，可能反弹'
        else:
            result['bb_signal'] = '布林带内运行'
        
        return result
    
    def format_report(self, analysis: Dict, stock_name: str = '') -> str:
        """格式化技术分析报告"""
        if 'error' in analysis:
            return f"技术分析: {analysis['error']}"
        
        lines = []
        lines.append(f"\n📈 技术分析 - {stock_name}")
        lines.append("=" * 50)
        
        # 均线
        lines.append("\n均线指标:")
        lines.append(f"  MA5: {analysis.get('ma5', 0):.2f}")
        lines.append(f"  MA10: {analysis.get('ma10', 0):.2f}")
        lines.append(f"  MA20: {analysis.get('ma20', 0):.2f}")
        lines.append(f"  MA60: {analysis.get('ma60', 0):.2f}")
        lines.append(f"  趋势: {analysis.get('trend', 'N/A')}")
        
        # MACD
        lines.append("\nMACD:")
        lines.append(f"  DIF: {analysis.get('macd_dif', 0):.2f}")
        lines.append(f"  DEA: {analysis.get('macd_signal', 0):.2f}")
        lines.append(f"  柱: {analysis.get('macd_histogram', 0):.2f}")
        
        # RSI
        lines.append(f"\nRSI(14): {analysis.get('rsi', 0):.2f} - {analysis.get('rsi_signal', '')}")
        
        # KDJ
        lines.append("\nKDJ:")
        lines.append(f"  K: {analysis.get('kdj_k', 0):.2f}")
        lines.append(f"  D: {analysis.get('kdj_d', 0):.2f}")
        lines.append(f"  J: {analysis.get('kdj_j', 0):.2f}")
        
        # 布林带
        lines.append("\n布林带:")
        lines.append(f"  上轨: {analysis.get('bb_upper', 0):.2f}")
        lines.append(f"  中轨: {analysis.get('bb_middle', 0):.2f}")
        lines.append(f"  下轨: {analysis.get('bb_lower', 0):.2f}")
        lines.append(f"  位置: {analysis.get('bb_signal', '')}")
        
        return "\n".join(lines)


# 测试
if __name__ == "__main__":
    import random
    random.seed(42)
    
    # 模拟价格数据
    prices = [100]
    for i in range(100):
        change = random.normalvariate(0.001, 0.02)
        prices.append(prices[-1] * (1 + change))
    
    analyzer = TechnicalAnalyzer()
    
    result = analyzer.analyze(prices)
    print(analyzer.format_report(result, '测试股票'))

"""
风险指标计算模块
计算波动率、最大回撤、夏普比率等风险指标
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RiskMetrics:
    """风险指标"""
    volatility: float  # 年化波动率 (%)
    max_drawdown: float  # 最大回撤 (%)
    sharpe_ratio: float  # 夏普比率
    var_95: float  # 95% VaR (%)
    beta: Optional[float] = None  # 贝塔系数
    alpha: Optional[float] = None  # 阿尔法
    
    def get_risk_level(self) -> str:
        """获取风险等级"""
        if self.volatility < 15:
            return '低风险'
        elif self.volatility < 25:
            return '中低风险'
        elif self.volatility < 35:
            return '中风险'
        elif self.volatility < 50:
            return '高风险'
        else:
            return '极高风险'
    
    def get_sharpe_assessment(self) -> str:
        """评估夏普比率"""
        if self.sharpe_ratio >= 2:
            return '优秀'
        elif self.sharpe_ratio >= 1:
            return '良好'
        elif self.sharpe_ratio >= 0.5:
            return '一般'
        else:
            return '较差'


class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        Args:
            risk_free_rate: 无风险利率（年化），默认3%
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """
        计算收益率序列
        """
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        
        return returns
    
    def calculate_volatility(self, returns: List[float], annualize: bool = True) -> float:
        """
        计算波动率
        
        Args:
            returns: 收益率序列（日收益率）
            annualize: 是否年化
        
        Returns:
            波动率 (%)
        """
        if len(returns) < 2:
            return 0.0
        
        # 计算标准差
        std = np.std(returns, ddof=1)
        
        if annualize:
            # 年化：乘以 sqrt(252) 个交易日
            std = std * np.sqrt(252)
        
        return round(std * 100, 2)  # 转换为百分比
    
    def calculate_max_drawdown(self, prices: List[float]) -> Tuple[float, int, int]:
        """
        计算最大回撤
        
        Returns:
            (最大回撤百分比, 开始索引, 结束索引)
        """
        if len(prices) < 2:
            return 0.0, 0, 0
        
        max_drawdown = 0.0
        peak = prices[0]
        peak_idx = 0
        trough_idx = 0
        max_peak_idx = 0
        
        for i, price in enumerate(prices):
            if price > peak:
                peak = price
                peak_idx = i
            
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_peak_idx = peak_idx
                trough_idx = i
        
        return round(max_drawdown * 100, 2), max_peak_idx, trough_idx
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """
        计算夏普比率
        
        Sharpe = (年化收益率 - 无风险利率) / 年化波动率
        """
        if len(returns) < 2:
            return 0.0
        
        # 计算平均日收益率
        mean_daily_return = np.mean(returns)
        
        # 年化收益率
        annual_return = mean_daily_return * 252
        
        # 年化波动率
        volatility = np.std(returns, ddof=1) * np.sqrt(252)
        
        if volatility == 0:
            return 0.0
        
        sharpe = (annual_return - self.risk_free_rate) / volatility
        return round(sharpe, 2)
    
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """
        计算VaR (Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence: 置信水平，默认95%
        
        Returns:
            VaR值 (%)
        """
        if len(returns) < 10:
            return 0.0
        
        var = np.percentile(returns, (1 - confidence) * 100)
        return round(abs(var) * 100, 2)
    
    def calculate_beta(self, stock_returns: List[float], market_returns: List[float]) -> float:
        """
        计算贝塔系数
        
        Beta = Cov(stock, market) / Var(market)
        """
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 10:
            return 1.0
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return round(beta, 2)
    
    def analyze_stock_risk(self, history: List[Dict], market_history: List[Dict] = None) -> RiskMetrics:
        """
        分析股票风险指标
        
        Args:
            history: 股票历史数据列表，每项包含 'close' 价格
            market_history: 市场指数历史数据（用于计算Beta）
        
        Returns:
            RiskMetrics 风险指标
        """
        if not history or len(history) < 30:
            return RiskMetrics(0, 0, 0, 0)
        
        # 提取收盘价
        prices = [h['close'] for h in history if h.get('close', 0) > 0]
        
        if len(prices) < 30:
            return RiskMetrics(0, 0, 0, 0)
        
        # 计算收益率
        returns = self.calculate_returns(prices)
        
        if len(returns) < 10:
            return RiskMetrics(0, 0, 0, 0)
        
        # 计算各项指标
        volatility = self.calculate_volatility(returns)
        max_dd, _, _ = self.calculate_max_drawdown(prices)
        sharpe = self.calculate_sharpe_ratio(returns)
        var_95 = self.calculate_var(returns, 0.95)
        
        # 计算Beta（如果有市场数据）
        beta = None
        if market_history and len(market_history) >= len(history):
            market_prices = [h['close'] for h in market_history[:len(prices)] if h.get('close', 0) > 0]
            if len(market_prices) == len(prices):
                market_returns = self.calculate_returns(market_prices)
                if len(market_returns) == len(returns):
                    beta = self.calculate_beta(returns, market_returns)
        
        return RiskMetrics(
            volatility=volatility,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            var_95=var_95,
            beta=beta
        )
    
    def get_risk_report(self, metrics: RiskMetrics) -> str:
        """
        生成风险报告文本
        """
        lines = []
        lines.append(f"波动率: {metrics.volatility}% ({metrics.get_risk_level()})")
        lines.append(f"最大回撤: {metrics.max_drawdown}%")
        lines.append(f"夏普比率: {metrics.sharpe_ratio} ({metrics.get_sharpe_assessment()})")
        lines.append(f"95% VaR: {metrics.var_95}%")
        
        if metrics.beta is not None:
            beta_desc = "高波动" if metrics.beta > 1.2 else ("低波动" if metrics.beta < 0.8 else "与市场同步")
            lines.append(f"Beta: {metrics.beta} ({beta_desc})")
        
        return " | ".join(lines)


def format_risk_for_report(metrics: RiskMetrics) -> str:
    """格式化风险指标用于报告"""
    if metrics.volatility == 0:
        return "数据不足"
    
    risk_emoji = "🟢" if metrics.volatility < 20 else ("🟡" if metrics.volatility < 30 else "🔴")
    sharpe_emoji = "🟢" if metrics.sharpe_ratio >= 1 else ("🟡" if metrics.sharpe_ratio >= 0.5 else "🔴")
    
    return f"{risk_emoji} 波动率:{metrics.volatility}% | 最大回撤:{metrics.max_drawdown}% | {sharpe_emoji} 夏普:{metrics.sharpe_ratio}"


if __name__ == "__main__":
    # 测试
    analyzer = RiskAnalyzer()
    
    # 模拟价格数据
    test_prices = [100, 102, 98, 105, 103, 108, 95, 102, 110, 108, 115, 112, 120, 118, 125]
    
    history = [{'close': p} for p in test_prices]
    
    metrics = analyzer.analyze_stock_risk(history)
    print(f"波动率: {metrics.volatility}%")
    print(f"最大回撤: {metrics.max_drawdown}%")
    print(f"夏普比率: {metrics.sharpe_ratio}")
    print(f"风险等级: {metrics.get_risk_level()}")

"""
历史百分位分析模块
计算PE/PB/股价在过去N年的百分位位置
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class PercentileResult:
    """百分位分析结果"""
    current_value: float
    percentile: float  # 0-100
    min_value: float
    max_value: float
    median: float
    mean: float
    std: float
    history_years: float
    data_points: int
    status: str  # 'low', 'normal', 'high'


class HistoricalAnalyzer:
    """历史数据分析器"""
    
    def __init__(self, fetcher):
        """
        Args:
            fetcher: StockFetcher 实例，用于获取历史数据
        """
        self.fetcher = fetcher
    
    def calculate_percentile(self, values: List[float], current: float) -> Tuple[float, str]:
        """
        计算当前值在历史数据中的百分位
        
        Returns:
            (百分位, 状态描述)
            百分位: 0-100，表示当前值在历史数据中的位置
            状态: 'extreme_low', 'low', 'normal', 'high', 'extreme_high'
        """
        if not values or len(values) < 10:
            return 50.0, 'unknown'
        
        # 过滤无效值
        valid_values = [v for v in values if v is not None and v > 0]
        if len(valid_values) < 10:
            return 50.0, 'unknown'
        
        # 计算百分位
        percentile = np.percentile(valid_values, np.arange(0, 101, 1))
        
        # 找到当前值的百分位
        current_pct = 0
        for i, p in enumerate(percentile):
            if current <= p:
                current_pct = i
                break
        else:
            current_pct = 100
        
        # 判断状态
        if current_pct <= 5:
            status = 'extreme_low'
        elif current_pct <= 20:
            status = 'low'
        elif current_pct >= 95:
            status = 'extreme_high'
        elif current_pct >= 80:
            status = 'high'
        else:
            status = 'normal'
        
        return float(current_pct), status
    
    def analyze_stock_percentile(self, stock_code: str, years: int = 3) -> Dict[str, PercentileResult]:
        """
        分析股票的历史百分位
        
        Args:
            stock_code: 股票代码
            years: 分析历史年数 (默认3年)
        
        Returns:
            包含PE、PB、股价百分位的字典
        """
        results = {}
        
        # 获取历史数据
        days = years * 252  # 约252个交易日/年
        history = self.fetcher.get_stock_history(stock_code, days)
        
        if not history or len(history) < 60:
            return results
        
        # 提取价格历史
        prices = [h['close'] for h in history if h.get('close', 0) > 0]
        
        if prices:
            current_price = prices[-1]
            price_pct, price_status = self.calculate_percentile(prices, current_price)
            
            results['price'] = PercentileResult(
                current_value=current_price,
                percentile=price_pct,
                min_value=min(prices),
                max_value=max(prices),
                median=np.median(prices),
                mean=np.mean(prices),
                std=np.std(prices),
                history_years=years,
                data_points=len(prices),
                status=price_status
            )
        
        # 获取当前估值数据
        valuation = self.fetcher.get_a_stock_valuation(stock_code)
        
        if valuation:
            # PE百分位（需要历史PE数据，这里用简化方法）
            current_pe = valuation.get('pe')
            if current_pe and current_pe > 0:
                # 简化：使用价格历史模拟PE历史（假设E相对稳定）
                # 实际应该获取历史PE数据
                pe_history = self._estimate_pe_history(history, current_pe)
                if pe_history:
                    pe_pct, pe_status = self.calculate_percentile(pe_history, current_pe)
                    results['pe'] = PercentileResult(
                        current_value=current_pe,
                        percentile=pe_pct,
                        min_value=min(pe_history),
                        max_value=max(pe_history),
                        median=np.median(pe_history),
                        mean=np.mean(pe_history),
                        std=np.std(pe_history),
                        history_years=years,
                        data_points=len(pe_history),
                        status=pe_status
                    )
            
            # PB百分位
            current_pb = valuation.get('pb')
            if current_pb and current_pb > 0:
                pb_history = self._estimate_pb_history(history, current_pb)
                if pb_history:
                    pb_pct, pb_status = self.calculate_percentile(pb_history, current_pb)
                    results['pb'] = PercentileResult(
                        current_value=current_pb,
                        percentile=pb_pct,
                        min_value=min(pb_history),
                        max_value=max(pb_history),
                        median=np.median(pb_history),
                        std=np.std(pb_history),
                        history_years=years,
                        data_points=len(pb_history),
                        status=pb_status
                    )
        
        return results
    
    def _estimate_pe_history(self, history: List[Dict], current_pe: float) -> List[float]:
        """
        估算历史PE（简化方法）
        实际项目中应该获取真实的历史PE数据
        """
        if not history or len(history) < 10:
            return []
        
        prices = [h['close'] for h in history if h.get('close', 0) > 0]
        if not prices:
            return []
        
        current_price = prices[-1]
        
        # 假设当前PE = 当前价格 / 当前盈利
        # 估算历史PE = 历史价格 / 当前盈利 * (盈利变化因子)
        # 简化：假设盈利每年增长10%，回推历史盈利
        
        pe_history = []
        days_per_year = 252
        
        for i, price in enumerate(prices):
            # 估算该时间点的盈利（假设年化增长10%）
            years_ago = (len(prices) - i) / days_per_year
            earnings_growth = (1.10) ** years_ago  # 假设盈利增长
            estimated_earnings = (current_price / current_pe) / earnings_growth
            
            if estimated_earnings > 0:
                estimated_pe = price / estimated_earnings
                if 0 < estimated_pe < 200:  # 过滤异常值
                    pe_history.append(estimated_pe)
        
        return pe_history
    
    def _estimate_pb_history(self, history: List[Dict], current_pb: float) -> List[float]:
        """
        估算历史PB（简化方法）
        """
        if not history or len(history) < 10:
            return []
        
        prices = [h['close'] for h in history if h.get('close', 0) > 0]
        if not prices:
            return []
        
        current_price = prices[-1]
        
        # 假设净资产相对稳定
        pb_history = []
        
        for price in prices:
            # 简化：假设净资产不变
            estimated_bvps = current_price / current_pb
            if estimated_bvps > 0:
                estimated_pb = price / estimated_bvps
                if 0 < estimated_pb < 50:  # 过滤异常值
                    pb_history.append(estimated_pb)
        
        return pb_history
    
    def get_valuation_assessment(self, percentile_results: Dict[str, PercentileResult]) -> Dict:
        """
        根据百分位结果给出估值评估
        """
        assessment = {
            'overall': 'unknown',
            'score': 50,  # 0-100，越高越低估
            'details': []
        }
        
        if not percentile_results:
            return assessment
        
        scores = []
        
        # PE评估
        if 'pe' in percentile_results:
            pe = percentile_results['pe']
            if pe.status == 'extreme_low':
                scores.append(95)
                assessment['details'].append(f"PE极低: {pe.current_value:.1f} (历史{pe.percentile:.0f}%分位)")
            elif pe.status == 'low':
                scores.append(80)
                assessment['details'].append(f"PE偏低: {pe.current_value:.1f} (历史{pe.percentile:.0f}%分位)")
            elif pe.status == 'high':
                scores.append(30)
                assessment['details'].append(f"PE偏高: {pe.current_value:.1f} (历史{pe.percentile:.0f}%分位)")
            elif pe.status == 'extreme_high':
                scores.append(10)
                assessment['details'].append(f"PE极高: {pe.current_value:.1f} (历史{pe.percentile:.0f}%分位)")
            else:
                scores.append(50)
                assessment['details'].append(f"PE适中: {pe.current_value:.1f} (历史{pe.percentile:.0f}%分位)")
        
        # PB评估
        if 'pb' in percentile_results:
            pb = percentile_results['pb']
            if pb.status == 'extreme_low':
                scores.append(95)
                assessment['details'].append(f"PB极低: {pb.current_value:.2f} (历史{pb.percentile:.0f}%分位)")
            elif pb.status == 'low':
                scores.append(80)
                assessment['details'].append(f"PB偏低: {pb.current_value:.2f} (历史{pb.percentile:.0f}%分位)")
            elif pb.status == 'high':
                scores.append(30)
                assessment['details'].append(f"PB偏高: {pb.current_value:.2f} (历史{pb.percentile:.0f}%分位)")
            elif pb.status == 'extreme_high':
                scores.append(10)
                assessment['details'].append(f"PB极高: {pb.current_value:.2f} (历史{pb.percentile:.0f}%分位)")
            else:
                scores.append(50)
                assessment['details'].append(f"PB适中: {pb.current_value:.2f} (历史{pb.percentile:.0f}%分位)")
        
        # 股价评估
        if 'price' in percentile_results:
            price = percentile_results['price']
            if price.status == 'extreme_low':
                scores.append(90)
                assessment['details'].append(f"股价处于历史低位: {price.percentile:.0f}%分位")
            elif price.status == 'low':
                scores.append(70)
                assessment['details'].append(f"股价处于历史中低位: {price.percentile:.0f}%分位")
            elif price.status == 'high':
                scores.append(40)
                assessment['details'].append(f"股价处于历史中高位: {price.percentile:.0f}%分位")
            elif price.status == 'extreme_high':
                scores.append(20)
                assessment['details'].append(f"股价处于历史高位: {price.percentile:.0f}%分位)")
        
        # 计算综合评分
        if scores:
            assessment['score'] = int(np.mean(scores))
            
            if assessment['score'] >= 80:
                assessment['overall'] = '极度低估'
            elif assessment['score'] >= 65:
                assessment['overall'] = '低估'
            elif assessment['score'] >= 45:
                assessment['overall'] = '合理'
            elif assessment['score'] >= 30:
                assessment['overall'] = '高估'
            else:
                assessment['overall'] = '极度高估'
        
        return assessment
    
    def format_percentile_report(self, stock_code: str, stock_name: str, 
                                  results: Dict[str, PercentileResult]) -> str:
        """
        格式化百分位分析报告
        """
        if not results:
            return f"{stock_name}({stock_code}): 无法获取历史数据"
        
        lines = [f"\n📊 {stock_name}({stock_code}) 历史估值分析"]
        lines.append("=" * 50)
        
        # PE
        if 'pe' in results:
            pe = results['pe']
            lines.append(f"\n📈 PE估值:")
            lines.append(f"   当前: {pe.current_value:.1f}")
            lines.append(f"   历史分位: {pe.percentile:.0f}% (越低越便宜)")
            lines.append(f"   历史区间: {pe.min_value:.1f} - {pe.max_value:.1f}")
            lines.append(f"   历史中位数: {pe.median:.1f}")
        
        # PB
        if 'pb' in results:
            pb = results['pb']
            lines.append(f"\n📊 PB估值:")
            lines.append(f"   当前: {pb.current_value:.2f}")
            lines.append(f"   历史分位: {pb.percentile:.0f}% (越低越便宜)")
            lines.append(f"   历史区间: {pb.min_value:.2f} - {pb.max_value:.2f}")
            lines.append(f"   历史中位数: {pb.median:.2f}")
        
        # 股价
        if 'price' in results:
            price = results['price']
            lines.append(f"\n💰 股价位置:")
            lines.append(f"   当前: {price.current_value:.2f}")
            lines.append(f"   历史分位: {price.percentile:.0f}%")
            lines.append(f"   历史区间: {price.min_value:.2f} - {price.max_value:.2f}")
        
        # 综合评估
        assessment = self.get_valuation_assessment(results)
        lines.append(f"\n🎯 综合评估: {assessment['overall']} (评分: {assessment['score']}/100)")
        for detail in assessment['details']:
            lines.append(f"   • {detail}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    from fetcher import StockFetcher
    
    fetcher = StockFetcher()
    analyzer = HistoricalAnalyzer(fetcher)
    
    # 测试分析
    test_codes = ['600519', '601166']
    
    for code in test_codes:
        print(f"\n分析 {code}...")
        results = analyzer.analyze_stock_percentile(code, years=3)
        
        # 获取股票名称
        price_data = fetcher.get_a_stock_price(code)
        name = price_data.get('name', code) if price_data else code
        
        report = analyzer.format_percentile_report(code, name, results)
        print(report)

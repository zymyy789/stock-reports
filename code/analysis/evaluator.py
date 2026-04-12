"""
估值分析模块 - 筛选低估值股票
"""
import pandas as pd
from typing import List, Dict
from config import PE_LOW, PE_HIGH, PB_LOW, PB_HIGH, DIVIDEND_YIELD_MIN

class StockEvaluator:
    """股票估值分析器"""
    
    def __init__(self):
        self.pe_low = PE_LOW
        self.pe_high = PE_HIGH
        self.pb_low = PB_LOW
        self.pb_high = PB_HIGH
        self.dividend_min = DIVIDEND_YIELD_MIN
    
    def evaluate(self, price_data: List[Dict], valuation_data: List[Dict]) -> pd.DataFrame:
        """综合评估股票"""
        # 合并价格和估值数据
        df = pd.DataFrame(price_data)
        val_df = pd.DataFrame(valuation_data)
        
        if df.empty:
            return pd.DataFrame()
        
        # 如果没有估值数据，返回空
        if val_df.empty:
            return pd.DataFrame()
        
        # 合并
        df = df.merge(val_df, on='code', how='left', suffixes=('_price', '_val'))
        
        # 确保必要字段存在
        if 'pe' not in df.columns or 'pb' not in df.columns or 'dividend' not in df.columns:
            return pd.DataFrame()
        
        # 填充空值
        df['pe'] = pd.to_numeric(df['pe'], errors='coerce').fillna(0)
        df['pb'] = pd.to_numeric(df['pb'], errors='coerce').fillna(0)
        df['dividend'] = pd.to_numeric(df['dividend'], errors='coerce').fillna(0)
        
        # 计算估值得分 (0-100, 越低越被低估)
        df['valuation_score'] = 0
        
        # PE 得分
        pe_score = 100 - (df['pe'] / self.pe_high * 100)
        pe_score = pe_score.clip(0, 100)
        df['valuation_score'] += pe_score * 0.4
        
        # PB 得分
        pb_score = 100 - (df['pb'] / self.pb_high * 100)
        pb_score = pb_score.clip(0, 100)
        df['valuation_score'] += pb_score * 0.3
        
        # 股息率得分
        div_score = (df['dividend'] / self.dividend_min * 100).clip(0, 100)
        df['valuation_score'] += div_score * 0.3
        
        # 过滤不符合条件的
        df = df[
            (df['pe'] >= self.pe_low) & (df['pe'] <= self.pe_high) &
            (df['pb'] >= self.pb_low) & (df['pb'] <= self.pb_high) &
            (df['dividend'] >= self.dividend_min)
        ]
        
        # 按估值得分排序
        df = df.sort_values('valuation_score', ascending=False)
        
        return df
    
    def is_undervalued(self, stock: Dict) -> bool:
        """判断是否低估值"""
        return (
            stock.get('pe', 999) >= self.pe_low and 
            stock.get('pe', 0) <= self.pe_high and
            stock.get('pb', 999) >= self.pb_low and
            stock.get('pb', 0) <= self.pb_high and
            stock.get('dividend', 0) >= self.dividend_min
        )
    
    def get_recommendations(self, evaluated_df: pd.DataFrame, top_n: int = 10) -> List[Dict]:
        """获取推荐股票"""
        if evaluated_df.empty:
            return []
        
        top_stocks = evaluated_df.head(top_n)
        recommendations = []
        
        for _, row in top_stocks.iterrows():
            recommendations.append({
                'code': row['code'],
                'name': row.get('name', ''),
                'price': row.get('price', 0),
                'change_pct': row.get('change_pct', 0),
                'pe': row.get('pe', 0),
                'pb': row.get('pb', 0),
                'dividend': row.get('dividend', 0),
                'valuation_score': row.get('valuation_score', 0),
                'recommend_reason': self._generate_reason(row)
            })
        
        return recommendations
    
    def _generate_reason(self, stock: Dict) -> str:
        """生成推荐理由"""
        reasons = []
        if stock.get('pe', 0) < 15:
            reasons.append(f"PE={stock['pe']:.1f}偏低")
        if stock.get('pb', 0) < 2:
            reasons.append(f"PB={stock['pb']:.2f}偏低")
        if stock.get('dividend', 0) > 3:
            reasons.append(f"股息率{stock['dividend']:.1f}%")
        
        return "，".join(reasons) if reasons else "综合估值偏低"


if __name__ == "__main__":
    evaluator = StockEvaluator()
    print("估值分析模块测试")
"""
数据存储模块 - SQLite数据库存储历史数据
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

class DataBase:
    """历史数据存储"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_history.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 股票每日数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                date TEXT NOT NULL,
                price REAL,
                change_pct REAL,
                pe REAL,
                pb REAL,
                dividend REAL,
                valuation_score REAL,
                UNIQUE(code, date)
            )
        ''')
        
        # 基金每日数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                date TEXT NOT NULL,
                nav REAL,
                acc_nav REAL,
                daily_change REAL,
                fund_score REAL,
                UNIQUE(code, date)
            )
        ''')
        
        # 持仓记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                type TEXT,  -- 'stock' or 'fund'
                amount INTEGER,
                cost REAL,
                buy_date TEXT,
                update_date TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_date ON stock_daily(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_date ON fund_daily(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_code ON stock_daily(code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_code ON fund_daily(code)')
        
        conn.commit()
        conn.close()
    
    def save_stock_data(self, data: Dict):
        """保存股票数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT OR REPLACE INTO stock_daily 
            (code, name, date, price, change_pct, pe, pb, dividend, valuation_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('code'),
            data.get('name'),
            today,
            data.get('price'),
            data.get('change_pct'),
            data.get('pe', 0),
            data.get('pb', 0),
            data.get('dividend', 0),
            data.get('valuation_score', 0),
        ))
        
        conn.commit()
        conn.close()
    
    def save_fund_data(self, data: Dict):
        """保存基金数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT OR REPLACE INTO fund_daily 
            (code, name, date, nav, acc_nav, daily_change, fund_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('code'),
            data.get('name'),
            today,
            data.get('nav'),
            data.get('acc_nav'),
            data.get('daily_change'),
            data.get('fund_score', 0),
        ))
        
        conn.commit()
        conn.close()
    
    def get_stock_history(self, code: str, days: int = 90) -> List[Dict]:
        """获取股票历史数据"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT code, name, date, price, change_pct, pe, pb, dividend, valuation_score
            FROM stock_daily
            WHERE code = ?
            ORDER BY date DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(code, days))
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
    
    def get_fund_history(self, code: str, days: int = 90) -> List[Dict]:
        """获取基金历史数据"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT code, name, date, nav, acc_nav, daily_change, fund_score
            FROM fund_daily
            WHERE code = ?
            ORDER BY date DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(code, days))
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
    
    def get_all_stock_data(self, date: str = None) -> List[Dict]:
        """获取某日所有股票数据"""
        conn = sqlite3.connect(self.db_path)
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = '''
            SELECT * FROM stock_daily WHERE date = ?
            ORDER BY valuation_score DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
    
    def get_all_fund_data(self, date: str = None) -> List[Dict]:
        """获取某日所有基金数据"""
        conn = sqlite3.connect(self.db_path)
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = '''
            SELECT * FROM fund_daily WHERE date = ?
            ORDER BY fund_score DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
    
    def calculate_pe_percentile(self, code: str, days: int = 365) -> Optional[float]:
        """计算PE历史百分位"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT pe FROM stock_daily
            WHERE code = ? AND pe > 0
            ORDER BY date DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(code, days))
        conn.close()
        
        if df.empty:
            return None
        
        current_pe = df['pe'].iloc[0]
        historical = df['pe'].values
        
        percentile = (historical < current_pe).sum() / len(historical) * 100
        return round(percentile, 2)
    
    def calculate_nav_trend(self, code: str, days: int = 30) -> Dict:
        """计算净值趋势"""
        history = self.get_fund_history(code, days)
        
        if len(history) < 5:
            return {'trend': 'N/A', 'details': {}}
        
        navs = [h['nav'] for h in history]
        
        ma5 = sum(navs[:5]) / 5 if len(navs) >= 5 else sum(navs) / len(navs)
        ma10 = sum(navs[:10]) / 10 if len(navs) >= 10 else sum(navs) / len(navs)
        ma20 = sum(navs[:20]) / 20 if len(navs) >= 20 else sum(navs) / len(navs)
        
        current = navs[0]
        
        if current > ma5 > ma10 > ma20:
            trend = '强势上涨'
        elif current > ma5:
            trend = '温和上涨'
        elif current < ma5 < ma10 < ma20:
            trend = '弱势下跌'
        elif current < ma5:
            trend = '温和下跌'
        else:
            trend = '震荡整理'
        
        return {
            'trend': trend,
            'current': current,
            'ma5': round(ma5, 4),
            'ma10': round(ma10, 4),
            'ma20': round(ma20, 4),
            'distance_from_ma20': round((current - ma20) / ma20 * 100, 2),
        }


if __name__ == "__main__":
    db = DataBase()
    print("数据库初始化完成")
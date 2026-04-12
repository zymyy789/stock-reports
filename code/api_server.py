# -*- coding: utf-8 -*-
"""
实时数据API服务 - 为Web App提供数据接口
"""
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')

from flask import Flask, jsonify
from flask_cors import CORS
from analysis.fund_fetcher import FundFetcher, FUND_CODE_LIST
from analysis.fetcher import StockFetcher
import json

app = Flask(__name__)
CORS(app)  # 允许跨域

stock_fetcher = StockFetcher()
fund_fetcher = FundFetcher()

# 关注的股票列表
STOCK_CODES = ['600519', '601318', '600036', '000858', '000333', 
               '601166', '600030', '600887', '600276', '601888']

@app.route('/api/market')
def get_market():
    """获取市场指数"""
    indices = [
        {'name': '上证指数', 'code': 'sh000001'},
        {'name': '沪深300', 'code': 'sh000300'},
        {'name': '创业板指', 'code': 'sz399006'},
        {'name': '恒生指数', 'code': 'hkHSI'}
    ]
    
    result = []
    for idx in indices:
        try:
            # 使用腾讯接口
            import requests
            url = f"https://qt.gtimg.cn/q={idx['code']}"
            resp = requests.get(url, headers={'Referer': 'https://gu.qq.com/'}, timeout=5)
            resp.encoding = 'gbk'
            parts = resp.text.split('~')
            if len(parts) > 32:
                result.append({
                    'name': idx['name'],
                    'price': float(parts[3]),
                    'change': float(parts[32])
                })
        except:
            pass
    
    return jsonify(result)

@app.route('/api/stocks')
def get_stocks():
    """获取股票列表"""
    result = []
    for code in STOCK_CODES:
        try:
            data = stock_fetcher.get_a_stock_price(code)
            if data:
                result.append({
                    'code': code,
                    'name': data.get('name', ''),
                    'price': data.get('price', 0),
                    'change': data.get('change_pct', 0),
                    'pe': data.get('pe', 0)
                })
        except:
            pass
    return jsonify(result)

@app.route('/api/funds')
def get_funds():
    """获取基金列表"""
    result = []
    for code in FUND_CODE_LIST[:15]:  # 取前15只
        try:
            data = fund_fetcher.get_fund_basic_info(code)
            if data:
                result.append({
                    'code': code,
                    'name': data.get('name', ''),
                    'nav': data.get('net_value', 0),
                    'change': data.get('daily_change', 0)
                })
        except:
            pass
    return jsonify(result)

@app.route('/api/stock/<code>')
def get_stock_detail(code):
    """获取股票详情"""
    try:
        data = stock_fetcher.get_a_stock_price(code)
        if data:
            return jsonify({
                'code': code,
                'name': data.get('name', ''),
                'price': data.get('price', 0),
                'change': data.get('change_pct', 0),
                'pe': data.get('pe', 0),
                'pb': data.get('pb', 0),
                'volume': data.get('volume', 0),
                'amount': data.get('amount', 0),
                'high': data.get('high', 0),
                'low': data.get('low', 0),
                'open': data.get('open', 0)
            })
    except:
        pass
    return jsonify({'error': 'not found'}), 404

@app.route('/api/fund/<code>')
def get_fund_detail(code):
    """获取基金详情"""
    try:
        data = fund_fetcher.get_fund_basic_info(code)
        if data:
            return jsonify({
                'code': code,
                'name': data.get('name', ''),
                'nav': data.get('net_value', 0),
                'estimate': data.get('estimate_value', 0),
                'change': data.get('daily_change', 0),
                'date': data.get('update_date', '')
            })
    except:
        pass
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    print("Starting API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

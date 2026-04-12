# -*- coding: utf-8 -*-
"""
Web App 数据接口 - 提供实时数据和模拟持仓
"""
import sys
sys.path.insert(0, r'C:\Users\zymyy\.qclaw\workspace\stock_work')
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, jsonify, request
from flask_cors import CORS
from analysis.fetcher import StockFetcher
from analysis.fund_fetcher import FundFetcher, FUND_CODE_LIST
from analysis.portfolio_manager import PortfolioManager
import json

app = Flask(__name__)
CORS(app)

stock_fetcher = StockFetcher()
fund_fetcher = FundFetcher()
portfolio_manager = PortfolioManager()

# 关注的股票
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
    for code in FUND_CODE_LIST[:15]:
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

@app.route('/api/portfolio')
def get_portfolio():
    """获取模拟持仓"""
    try:
        portfolio = portfolio_manager.get_portfolio_value()
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals')
def get_signals():
    """获取策略信号"""
    try:
        signals = portfolio_manager.get_strategy_signals()
        return jsonify(signals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade', methods=['POST'])
def trade():
    """执行交易"""
    try:
        data = request.json
        action = data.get('action')
        code = data.get('code')
        amount = int(data.get('amount', 0))
        
        if action == 'buy':
            # 获取当前价格
            stock_data = stock_fetcher.get_a_stock_price(code)
            if not stock_data:
                return jsonify({'success': False, 'error': '获取价格失败'})
            
            result = portfolio_manager.buy(
                code=code,
                name=stock_data.get('name', ''),
                price=stock_data.get('price', 0),
                amount=amount,
                item_type='stock',
                reason=data.get('reason', '')
            )
            return jsonify(result)
        
        elif action == 'sell':
            stock_data = stock_fetcher.get_a_stock_price(code)
            if not stock_data:
                return jsonify({'success': False, 'error': '获取价格失败'})
            
            result = portfolio_manager.sell(
                code=code,
                price=stock_data.get('price', 0),
                amount=amount,
                reason=data.get('reason', '')
            )
            return jsonify(result)
        
        else:
            return jsonify({'success': False, 'error': '无效操作'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """获取交易历史"""
    try:
        days = int(request.args.get('days', 30))
        history = portfolio_manager.get_trade_history(days)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<code>')
def get_stock_detail(code):
    """获取股票详情"""
    try:
        data = stock_fetcher.get_a_stock_price(code)
        if data:
            return jsonify(data)
    except:
        pass
    return jsonify({'error': 'not found'}), 404

@app.route('/api/fund/<code>')
def get_fund_detail(code):
    """获取基金详情"""
    try:
        data = fund_fetcher.get_fund_basic_info(code)
        if data:
            return jsonify(data)
    except:
        pass
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    print("API Server starting on http://localhost:5000")
    print("Endpoints:")
    print("  /api/market - Market indices")
    print("  /api/stocks - Stock list")
    print("  /api/funds - Fund list")
    print("  /api/portfolio - Portfolio")
    print("  /api/signals - Trading signals")
    print("  /api/trade - Execute trade (POST)")
    app.run(host='0.0.0.0', port=5000, debug=False)

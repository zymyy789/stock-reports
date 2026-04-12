"""
数据获取模块 - 多源备份版本
支持东方财富、腾讯财经、新浪财经等多个数据源
"""
import requests
import pandas as pd
import time
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class StockFetcher:
    """股票数据获取器 - 多源备份"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        # 统计各数据源成功率
        self.stats = {'eastmoney': {'success': 0, 'fail': 0}, 'tencent': {'success': 0, 'fail': 0}, 'sina': {'success': 0, 'fail': 0}}
    
    def _get_secid(self, stock_code: str) -> str:
        """
        获取东方财富的 secid
        0. 开头 - 深圳交易所 (000/002/003/300开头)
        1. 开头 - 上海交易所 (600/601/603/688开头)
        """
        if stock_code.startswith(('6', '5', '68')):
            return f"1.{stock_code}"
        else:
            return f"0.{stock_code}"
    
    def get_a_stock_price(self, stock_code: str, use_backup: bool = True) -> Optional[Dict]:
        """
        获取A股实时价格
        优先使用腾讯财经（更稳定），失败时尝试新浪财经
        """
        # 尝试腾讯财经（最稳定）
        result = self._get_tencent_price(stock_code)
        if result and result.get('price', 0) > 1:  # 价格大于1元才认为有效
            self.stats['tencent']['success'] += 1
            return result
        self.stats['tencent']['fail'] += 1
        
        if use_backup:
            # 尝试新浪财经
            result = self._get_sina_price(stock_code)
            if result and result.get('price', 0) > 1:
                self.stats['sina']['success'] += 1
                return result
            self.stats['sina']['fail'] += 1
            
            # 最后尝试东方财富
            result = self._get_eastmoney_price(stock_code)
            if result and result.get('price', 0) > 1:
                self.stats['eastmoney']['success'] += 1
                return result
            self.stats['eastmoney']['fail'] += 1
        
        return None
    
    def _get_eastmoney_price(self, stock_code: str) -> Optional[Dict]:
        """从东方财富获取股票价格"""
        try:
            secid = self._get_secid(stock_code)
            url = f"https://push2.eastmoney.com/api/qt/stock/get?fltt=2&invt=2&fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f57,f58,f59,f60,f116,f117,f162,f167,f168,f169,f170,f171,f173,f177&secid={secid}"
            
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            data = resp.json()
            
            if data.get('data'):
                d = data['data']
                
                # 解析价格字段
                price = self._parse_price(d.get('f43'))
                
                # 价格有效性检查
                if price <= 0 or price > 10000:
                    return None
                
                return {
                    'code': stock_code,
                    'name': d.get('f58', ''),
                    'price': price,
                    'change': self._parse_price(d.get('f170')),
                    'change_pct': self._parse_pct(d.get('f171')),
                    'volume': d.get('f47', 0),
                    'amount': d.get('f48', 0),
                    'high': self._parse_price(d.get('f44')),
                    'low': self._parse_price(d.get('f45')),
                    'open': self._parse_price(d.get('f46')),
                    'pre_close': self._parse_price(d.get('f60')),
                    'source': 'eastmoney',
                }
        except Exception as e:
            print(f"[EastMoney] 获取 {stock_code} 失败: {e}")
        return None
    
    def _get_tencent_price(self, stock_code: str) -> Optional[Dict]:
        """从腾讯财经获取股票价格"""
        try:
            # 腾讯格式: sh600519 或 sz000858
            prefix = 'sh' if stock_code.startswith(('6', '5')) else 'sz'
            tencent_code = f"{prefix}{stock_code}"
            
            url = f"https://qt.gtimg.cn/q={tencent_code}"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'gbk'
            
            text = resp.text
            if not text or '~' not in text:
                return None
            
            # 解析腾讯返回的数据格式
            parts = text.split('~')
            if len(parts) < 45:
                return None
            
            # 腾讯数据格式: ...~名称~代码~价格~...~
            name = parts[1]
            price = float(parts[3]) if parts[3] else 0
            
            if price <= 0:
                return None
            
            pre_close = float(parts[4]) if parts[4] else price
            change = price - pre_close
            change_pct = (change / pre_close * 100) if pre_close > 0 else 0
            pe = float(parts[39]) if len(parts) > 39 and parts[39] else 0
            
            return {
                'code': stock_code,
                'name': name,
                'price': price,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'pe': pe,
                'volume': int(parts[36]) if len(parts) > 36 else 0,
                'high': float(parts[33]) if len(parts) > 33 and parts[33] else price,
                'low': float(parts[34]) if len(parts) > 34 and parts[34] else price,
                'open': float(parts[5]) if len(parts) > 5 and parts[5] else price,
                'pre_close': pre_close,
                'source': 'tencent',
            }
        except Exception as e:
            print(f"[Tencent] 获取 {stock_code} 失败: {e}")
        return None
    
    def _get_sina_price(self, stock_code: str) -> Optional[Dict]:
        """从新浪财经获取股票价格"""
        try:
            prefix = 'sh' if stock_code.startswith(('6', '5')) else 'sz'
            sina_code = f"{prefix}{stock_code}"
            
            url = f"https://hq.sinajs.cn/list={sina_code}"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'gbk'
            
            text = resp.text
            if not text or '"' not in text:
                return None
            
            # 解析新浪返回: var hq_str_sh600519="...";
            start = text.find('"') + 1
            end = text.find('"', start)
            data_str = text[start:end]
            
            parts = data_str.split(',')
            if len(parts) < 10:
                return None
            
            name = parts[0]
            price = float(parts[3]) if parts[3] else 0
            
            if price <= 0:
                return None
            
            pre_close = float(parts[2]) if parts[2] else price
            change = price - pre_close
            change_pct = (change / pre_close * 100) if pre_close > 0 else 0
            
            return {
                'code': stock_code,
                'name': name,
                'price': price,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': int(parts[8]) if parts[8] else 0,
                'high': float(parts[4]) if parts[4] else price,
                'low': float(parts[5]) if parts[5] else price,
                'open': float(parts[1]) if parts[1] else price,
                'pre_close': pre_close,
                'source': 'sina',
            }
        except Exception as e:
            print(f"[Sina] 获取 {stock_code} 失败: {e}")
        return None
    
    def _parse_price(self, val) -> float:
        """解析价格字段"""
        if val is None:
            return 0.0
        try:
            # 东方财富价格通常是实际价格的1000倍
            price = float(val) / 1000
            return round(price, 2)
        except:
            return 0.0
    
    def _parse_pct(self, val) -> float:
        """解析百分比字段"""
        if val is None:
            return 0.0
        try:
            # 东方财富涨跌幅是实际值的100倍
            pct = float(val) / 100
            return round(pct, 2)
        except:
            return 0.0
    
    def get_a_stock_valuation(self, stock_code: str) -> Optional[Dict]:
        """
        获取A股估值数据 (PE, PB, 股息率)
        """
        try:
            secid = self._get_secid(stock_code)
            url = f"https://push2.eastmoney.com/api/qt/stock/get?fltt=2&invt=2&fields=f162,f163,f164,f165,f166,f167,f168,f169,f173,f177,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201&secid={secid}"
            
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            data = resp.json()
            
            if data.get('data'):
                d = data['data']
                
                pe = self._parse_price(d.get('f162'))  # 市盈率
                pb = self._parse_price(d.get('f167'))  # 市净率
                dividend = self._parse_pct(d.get('f173'))  # 股息率
                
                # 股息率可能需要额外处理
                if dividend == 0 and d.get('f173'):
                    try:
                        dividend = float(d.get('f173')) / 100
                    except:
                        pass
                
                return {
                    'code': stock_code,
                    'pe': pe if pe > 0 else None,
                    'pb': pb if pb > 0 else None,
                    'dividend': round(dividend, 2) if dividend > 0 else None,
                    'market_cap': self._parse_price(d.get('f116')) / 1000000 if d.get('f116') else None,  # 总市值(亿)
                    'source': 'eastmoney',
                }
        except Exception as e:
            print(f"[EastMoney] 获取估值 {stock_code} 失败: {e}")
        return None
    
    def get_index_price(self, index_code: str) -> Optional[Dict]:
        """
        获取指数行情
        支持: 000001(上证), 399001(深证), HSI(恒生), ^GSPC(标普500)等
        """
        # 映射常见指数代码
        index_mapping = {
            '000001': ('1.000001', '上证指数'),
            '399001': ('0.399001', '深证成指'),
            '399006': ('0.399006', '创业板指'),
            '000300': ('1.000300', '沪深300'),
            '000016': ('1.000016', '上证50'),
            '000905': ('1.000905', '中证500'),
            'HSI': 'HSI',
            'HSCCI': 'HSCCI',
            '^GSPC': 'US.SPX',
            '^DJI': 'US.DJI',
            '^IXIC': 'US.IXIC',
        }
        
        try:
            if index_code in index_mapping:
                mapped = index_mapping[index_code]
                
                if isinstance(mapped, tuple):
                    # A股指数
                    secid, name = mapped
                    url = f"https://push2.eastmoney.com/api/qt/stock/get?fltt=2&invt=2&fields=f43,f44,f45,f46,f57,f58,f169,f170,f171&secid={secid}"
                    
                    resp = self.session.get(url, timeout=10)
                    resp.encoding = 'utf-8'
                    data = resp.json()
                    
                    if data.get('data'):
                        d = data['data']
                        price = self._parse_price(d.get('f43'))
                        
                        if price > 0:
                            return {
                                'code': index_code,
                                'name': name,
                                'price': price,
                                'change': self._parse_price(d.get('f170')),
                                'change_pct': self._parse_pct(d.get('f171')),
                                'source': 'eastmoney',
                            }
                
                elif index_code == 'HSI':
                    # 恒生指数 - 使用腾讯接口
                    return self._get_hk_index_tencent('HSI', '恒生指数')
                
                elif index_code == 'HSCCI':
                    # 国企指数
                    return self._get_hk_index_tencent('HSCCI', '国企指数')
                    
        except Exception as e:
            print(f"获取指数 {index_code} 失败: {e}")
        
        return None
    
    def _get_hk_index_tencent(self, code: str, name: str) -> Optional[Dict]:
        """从腾讯获取港股指数"""
        try:
            # 腾讯港股指数格式
            hk_codes = {'HSI': 'hkHSI', 'HSCCI': 'hkHSCEI'}
            tencent_code = hk_codes.get(code, f'hk{code}')
            
            url = f"https://qt.gtimg.cn/q={tencent_code}"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'gbk'
            
            text = resp.text
            if text and '~' in text:
                parts = text.split('~')
                if len(parts) > 3:
                    price = float(parts[3]) if parts[3] else 0
                    if price > 0:
                        change = float(parts[4]) if len(parts) > 4 and parts[4] else 0
                        change_pct = float(parts[5]) if len(parts) > 5 and parts[5] else 0
                        
                        return {
                            'code': code,
                            'name': name,
                            'price': price,
                            'change': change,
                            'change_pct': change_pct,
                            'source': 'tencent',
                        }
        except Exception as e:
            print(f"[Tencent] 获取港股指数 {code} 失败: {e}")
        return None
    
    def get_hk_stock_price(self, stock_code: str) -> Optional[Dict]:
        """获取港股价格"""
        try:
            # 使用腾讯接口获取港股
            url = f"https://qt.gtimg.cn/q=hk{stock_code}"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'gbk'
            
            text = resp.text
            if text and '~' in text:
                parts = text.split('~')
                if len(parts) > 3:
                    name = parts[1]
                    price = float(parts[3]) if parts[3] else 0
                    
                    if price > 0:
                        change = float(parts[4]) if len(parts) > 4 and parts[4] else 0
                        change_pct = float(parts[5]) if len(parts) > 5 and parts[5] else 0
                        
                        return {
                            'code': stock_code,
                            'name': name,
                            'price': price,
                            'change': change,
                            'change_pct': change_pct,
                            'source': 'tencent',
                        }
        except Exception as e:
            print(f"获取港股 {stock_code} 失败: {e}")
        return None
    
    def get_batch_stocks(self, stock_codes: List[str], delay: float = 0.05) -> List[Dict]:
        """
        批量获取股票数据
        """
        results = []
        success_count = 0
        fail_count = 0
        
        print(f"开始批量获取 {len(stock_codes)} 只股票数据...")
        
        for i, code in enumerate(stock_codes):
            result = self.get_a_stock_price(code)
            if result:
                results.append(result)
                success_count += 1
                print(f"  [{i+1}/{len(stock_codes)}] ✓ {code} {result.get('name', '')}: {result.get('price', 0):.2f} ({result.get('source', 'unknown')})")
            else:
                fail_count += 1
                print(f"  [{i+1}/{len(stock_codes)}] ✗ {code} 获取失败")
            
            time.sleep(delay)
        
        print(f"\n批量获取完成: 成功 {success_count}, 失败 {fail_count}")
        self._print_stats()
        
        return results
    
    def _print_stats(self):
        """打印数据源统计"""
        print("\n数据源统计:")
        for source, stats in self.stats.items():
            total = stats['success'] + stats['fail']
            if total > 0:
                rate = stats['success'] / total * 100
                print(f"  {source}: 成功 {stats['success']}/{total} ({rate:.1f}%)")
    
    def get_stock_history(self, stock_code: str, days: int = 60) -> Optional[List[Dict]]:
        """
        获取股票历史数据（用于计算历史百分位）
        """
        try:
            secid = self._get_secid(stock_code)
            
            # 东方财富历史数据接口
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&end=20500101&lmt={days}"
            
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            data = resp.json()
            
            if data.get('data') and data['data'].get('klines'):
                klines = data['data']['klines']
                history = []
                
                for line in klines:
                    # 格式: 日期,开盘价,收盘价,最高价,最低价,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
                    parts = line.split(',')
                    if len(parts) >= 6:
                        history.append({
                            'date': parts[0],
                            'open': float(parts[1]),
                            'close': float(parts[2]),
                            'high': float(parts[3]),
                            'low': float(parts[4]),
                            'volume': int(float(parts[5])),
                        })
                
                return history
        except Exception as e:
            print(f"获取历史数据 {stock_code} 失败: {e}")
        return None


if __name__ == "__main__":
    fetcher = StockFetcher()
    
    # 测试获取多只股票
    test_codes = ['600519', '000858', '601166', '002594', '300750']
    
    print("=" * 60)
    print("股票数据获取测试")
    print("=" * 60)
    
    for code in test_codes:
        print(f"\n测试 {code}:")
        data = fetcher.get_a_stock_price(code)
        if data:
            print(f"  名称: {data.get('name')}")
            print(f"  价格: {data.get('price')}")
            print(f"  涨跌: {data.get('change_pct')}%")
            print(f"  来源: {data.get('source')}")
            
            # 获取估值数据
            val = fetcher.get_a_stock_valuation(code)
            if val:
                print(f"  PE: {val.get('pe')}")
                print(f"  PB: {val.get('pb')}")
                print(f"  股息: {val.get('dividend')}%")
        else:
            print("  获取失败")
    
    # 测试指数
    print("\n" + "=" * 60)
    print("指数数据测试")
    print("=" * 60)
    
    for idx in ['000001', '399001', 'HSI']:
        data = fetcher.get_index_price(idx)
        if data:
            print(f"{data.get('name')}: {data.get('price')} ({data.get('change_pct')}%)")

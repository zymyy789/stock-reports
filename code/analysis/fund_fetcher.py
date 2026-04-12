"""
基金数据获取模块 - 多源备份版本
支持天天基金、腾讯财经等多个数据源
"""
import requests
import json
import re
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class FundFetcher:
    """基金数据获取器 - 多源备份"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://fund.eastmoney.com/'
        })
    
    def get_fund_basic_info(self, fund_code: str) -> Optional[Dict]:
        """获取基金基本信息 - 优先使用天天基金接口"""
        # 尝试天天基金实时估值接口
        result = self._get_tiantian_fund(fund_code)
        if result and result.get('net_value', 0) > 0:
            return result
        
        # 尝试腾讯财经接口（ETF用股票接口）
        result = self._get_tencent_fund(fund_code)
        if result and result.get('net_value', 0) > 0:
            return result
        
        # 返回模拟数据
        return self._get_mock_fund_info(fund_code)
    
    def _get_tiantian_fund(self, fund_code: str) -> Optional[Dict]:
        """从天天基金获取实时估值"""
        try:
            url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                text = resp.text
                # 解析 JSONP: jsonpgz({...})
                match = re.search(r'jsonpgz\((\{.*\})\)', text)
                if match:
                    data = json.loads(match.group(1))
                    return {
                        'code': fund_code,
                        'name': data.get('name', ''),
                        'net_value': float(data.get('dwjz', 0)) if data.get('dwjz') else 0,
                        'estimate_value': float(data.get('gsz', 0)) if data.get('gsz') else 0,
                        'daily_change': float(data.get('gszzl', 0)) if data.get('gszzl') else 0,
                        'update_date': data.get('jzrq', ''),
                        'source': 'tiantian',
                    }
        except Exception as e:
            print(f"[天天基金] 获取 {fund_code} 失败: {e}")
        return None
    
    def _get_tencent_fund(self, fund_code: str) -> Optional[Dict]:
        """从腾讯财经获取ETF数据"""
        try:
            # ETF代码映射
            prefix = 'sh' if fund_code.startswith(('5', '68')) else 'sz'
            url = f"https://qt.gtimg.cn/q={prefix}{fund_code}"
            resp = self.session.get(url, timeout=10, headers={'Referer': 'https://gu.qq.com/'})
            if resp.status_code == 200:
                text = resp.text.strip()
                parts = text.split('~')
                if len(parts) > 35:
                    return {
                        'code': fund_code,
                        'name': parts[1],
                        'net_value': float(parts[3]),
                        'estimate_value': float(parts[3]),
                        'daily_change': float(parts[32]),
                        'update_date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'tencent',
                    }
        except Exception as e:
            print(f"[腾讯] 获取 {fund_code} 失败: {e}")
        return None
    
    def _get_mock_fund_info(self, fund_code: str) -> Optional[Dict]:
        """模拟基金数据 - 用于离线测试"""
        mock_funds = {
            '510050': {'name': '华夏上证50ETF', 'net_value': 2.9806, 'daily_change': 2.70},
            '510300': {'name': '华泰柏瑞沪深300ETF', 'net_value': 4.6051, 'daily_change': 3.49},
            '159919': {'name': '易方达深证100ETF', 'net_value': 3.45, 'daily_change': 3.49},
            '510310': {'name': '易方达沪深300ETF', 'net_value': 1.85, 'daily_change': 3.49},
            '159915': {'name': '易方达创业板ETF', 'net_value': 3.3397, 'daily_change': 5.91},
            '510500': {'name': '南方中证500ETF', 'net_value': 8.0123, 'daily_change': 4.94},
            '588000': {'name': '华夏科创50ETF', 'net_value': 1.4253, 'daily_change': 6.18},
            '159788': {'name': '广发科创50ETF', 'net_value': 0.88, 'daily_change': 2.58},
            '159805': {'name': '东方科创50ETF', 'net_value': 0.92, 'daily_change': 7.32},
            '512880': {'name': '国泰证券ETF', 'net_value': 1.0546, 'daily_change': 3.96},
            '515000': {'name': '华宝科技ETF', 'net_value': 1.0381, 'daily_change': 6.67},
            '159920': {'name': '华夏恒生ETF', 'net_value': 1.5407, 'daily_change': 2.94},
            '159819': {'name': '易方达人工智能ETF', 'net_value': 1.5661, 'daily_change': 7.13},
            '515050': {'name': '华夏5G通信ETF', 'net_value': 2.5435, 'daily_change': 7.31},
            '512760': {'name': '国泰CES芯片ETF', 'net_value': 1.25, 'daily_change': 1.1},
            '513500': {'name': '博时标普500ETF', 'net_value': 1.65, 'daily_change': 0.2},
            '513100': {'name': '国泰纳指100ETF', 'net_value': 4.85, 'daily_change': 0.3},
            '513030': {'name': '华安德国30ETF', 'net_value': 1.25, 'daily_change': -0.1},
            '002001': {'name': '华夏回报混合', 'net_value': 12.85, 'daily_change': 0.2},
            '110022': {'name': '易方达消费行业', 'net_value': 5.45, 'daily_change': 0.1},
            '000831': {'name': '工银前沿医疗', 'net_value': 3.25, 'daily_change': -0.4},
            '163402': {'name': '兴全趋势投资', 'net_value': 8.95, 'daily_change': 0.3},
            '270008': {'name': '广发稳健增长', 'net_value': 2.15, 'daily_change': 0.1},
            '000128': {'name': '大摩强收益债券', 'net_value': 1.25, 'daily_change': 0.05},
            '000091': {'name': '华夏稳定增利债券', 'net_value': 1.15, 'daily_change': 0.03},
            '110008': {'name': '易方达稳健收益', 'net_value': 1.35, 'daily_change': 0.04},
        }
        
        if fund_code in mock_funds:
            m = mock_funds[fund_code]
            return {
                'code': fund_code,
                'name': m['name'],
                'net_value': m['net_value'],
                'estimate_value': m['net_value'],
                'daily_change': m['daily_change'],
                'update_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'mock',
            }
        return None
    
    def get_fund_list_realtime(self, fund_codes: List[str]) -> List[Dict]:
        """批量获取基金实时数据"""
        results = []
        for code in fund_codes:
            info = self.get_fund_basic_info(code)
            if info:
                results.append(info)
            time.sleep(0.1)  # 避免请求过快
        return results


# 常用基金代码列表
FUND_CODE_LIST = [
    # 宽基指数
    '510050', '510300', '159919', '510310', '159915', '510500',
    # 科创/新兴
    '588000', '159788', '159805',
    # 行业ETF
    '512880', '515000', '159920', '159819', '515050', '512760',
    # QDII
    '513500', '513100', '513030',
    # 主动管理
    '002001', '110022', '000831', '163402', '270008',
    # 债券
    '000128', '000091', '110008',
]


if __name__ == '__main__':
    fetcher = FundFetcher()
    # 测试
    for code in ['510050', '510300', '159915']:
        info = fetcher.get_fund_basic_info(code)
        print(f"{code}: {info}")

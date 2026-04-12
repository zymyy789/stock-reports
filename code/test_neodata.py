# -*- coding: utf-8 -*-
"""测试NeoData获取专业数据"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Progra~1\QClaw\resources\openclaw\config\skills\neodata-financial-search')

from scripts.query import query_neodata

stocks = [
    "兴业银行 机构评级 目标价 盈利预测",
    "招商银行 主力资金流向 研报评级",
    "中国平安 机构评级 目标价",
    "贵州茅台 机构评级 目标价 资金流向",
]

for q in stocks:
    print(f"\n{'='*60}")
    print(f"查询: {q}")
    print('='*60)
    result = query_neodata(q)
    if result and result.get('code') == '200':
        api = result['data']['apiData']
        for r in api.get('apiRecall', []):
            print(f"\n[{r['type']}]")
            content = r['content']
            # 只取前500字符
            print(content[:500])
    else:
        print("查询失败")

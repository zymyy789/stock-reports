# -*- coding: utf-8 -*-
import sys, requests
sys.stdout.reconfigure(encoding='utf-8')

# 测试腾讯接口返回的所有字段
url = "https://qt.gtimg.cn/q=sh601166"
resp = requests.get(url, headers={'Referer': 'https://gu.qq.com/'})
resp.encoding = 'gbk'
parts = resp.text.strip().split('~')

print("Total parts:", len(parts))
for i in range(min(50, len(parts))):
    print(f"[{i}] {parts[i]}")

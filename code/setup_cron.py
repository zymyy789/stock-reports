# 实时交易监控定时任务
# 交易时段: 9:30-11:30, 13:00-15:00
# 每30分钟运行一次

import json

# 5个时段的任务
tasks = [
    {"hour": 9, "minute": 35},   # 开盘后5分钟
    {"hour": 10, "minute": 0},   # 10点
    {"hour": 10, "minute": 30},  # 10:30
    {"hour": 11, "minute": 0},   # 11点
    {"hour": 13, "minute": 5},   # 下午开盘后5分钟
    {"hour": 13, "minute": 30},  # 13:30
    {"hour": 14, "minute": 0},   # 14点
    {"hour": 14, "minute": 30},  # 14:30
]

for i, t in enumerate(tasks):
    cron_expr = f"{t['minute']} {t['hour']} * * 1-5"  # 周一到周五
    print(f"任务{i+1}: {t['hour']:02d}:{t['minute']:02d} -> cron: {cron_expr}")

# 📈 股票基金智能分析系统

自动化价值投资分析系统，每日分析 A股/港股/美股，生成投资建议报告。

## 功能特性

- ✅ **多市场覆盖**：A股、港股（重要中企）、美股/港股指数
- ✅ **智能估值**：低估值股票筛选（PE、PB、股息率）
- ✅ **趋势辅助**：均线、MACD 等技术指标辅助判断
- ✅ **模拟交易**：10万模拟资金，持续跟踪持仓
- ✅ **每日报告**：Markdown 格式报告，推送 GitHub
- ✅ **定时推送**：每日下午6点自动发送报告

## 项目结构

```
stock_work/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt       # 依赖
├── data/                   # 数据存储
│   ├── stocks.csv         # 股票池
│   └── portfolio.json     # 持仓数据
├── analysis/              # 分析模块
│   ├── fetcher.py        # 数据获取
│   ├── evaluator.py      # 估值分析
│   ├── trader.py         # 模拟交易
│   └── reporter.py       # 报告生成
├── reports/               # 报告输出
└── .github/workflows/     # GitHub Actions
    └── daily_report.yml  # 每日任务
```

## 使用方法

### 本地运行

```bash
pip install -r requirements.txt
python main.py
```

### GitHub Actions 自动运行

推送到 GitHub 后自动每日执行（需要配置 Secrets）。

## 依赖

- akshare (A股数据)
- requests
- pandas
- matplotlib

## 免责声明

本系统仅供学习研究，不构成投资建议。模拟交易不代表真实收益。
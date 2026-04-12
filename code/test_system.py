"""
股票分析系统验证脚本
测试各个模块是否正常工作
"""
import sys
import os

# 设置 UTF-8 编码
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("股票分析系统验证测试")
print("=" * 60)

# 测试1: 导入模块
print("\n[测试1] 导入模块...")
try:
    from config import A股_POOL, 港股_POOL, INITIAL_CAPITAL
    from analysis.fetcher import StockFetcher
    from analysis.evaluator import StockEvaluator
    from analysis.trader import SimTrader
    from analysis.reporter import ReportGenerator
    print("  ✅ 所有模块导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 测试2: 配置检查
print("\n[测试2] 配置检查...")
print(f"  A股股票数量: {len(A股_POOL)}")
print(f"  港股股票数量: {len(港股_POOL)}")
print(f"  初始资金: {INITIAL_CAPITAL}")
if len(A股_POOL) >= 10 and INITIAL_CAPITAL == 100000:
    print("  ✅ 配置正确")
else:
    print("  ❌ 配置异常")

# 测试3: 数据获取
print("\n[测试3] 数据获取...")
fetcher = StockFetcher()

# 测试获取一只股票
test_stock = fetcher.get_a_stock_price("600519")
if test_stock and test_stock.get('price', 0) > 0:
    print(f"  ✅ 贵州茅台价格: {test_stock['price']:.2f} 元")
else:
    print("  ❌ 股票数据获取失败")

# 测试4: 估值数据获取
print("\n[测试4] 估值数据获取...")
valuation = fetcher.get_a_stock_valuation("600519")
if valuation and valuation.get('pe', 0) > 0:
    print(f"  ✅ PE: {valuation['pe']:.1f}, PB: {valuation['pb']:.2f}, 股息率: {valuation['dividend']:.1f}%")
else:
    print("  ⚠️ 估值数据可能为空（正常，API可能返回空值）")

# 测试5: 指数数据获取
print("\n[测试5] 指数数据获取...")
idx = fetcher.get_index_price("000001")
if idx:
    print(f"  ✅ 上证指数: {idx.get('price', 'N/A')}")
else:
    print("  ⚠️ 指数数据获取失败（API不稳定）")

# 测试6: 模拟交易器
print("\n[测试6] 模拟交易器...")
trader = SimTrader()
if trader.capital == 100000:
    print(f"  ✅ 初始资金: {trader.capital} 元")
else:
    print(f"  ❌ 资金异常: {trader.capital}")

# 测试买入
result = trader.buy("600519", "贵州茅台", 1500.0, 100)
if result:
    print(f"  ✅ 买入成功，剩余资金: {trader.capital:.2f} 元")
else:
    print("  ❌ 买入失败")

# 测试持仓查询
positions = trader.positions
if "600519" in positions:
    print(f"  ✅ 持仓: {positions['600519']['amount']} 股")
else:
    print("  ❌ 持仓查询失败")

# 测试7: 估值分析器
print("\n[测试7] 估值分析器...")
evaluator = StockEvaluator()
# 模拟数据测试
test_data = [{
    'code': '600519',
    'name': '贵州茅台',
    'price': 1500.0,
    'change_pct': 1.5,
    'pe': 25.0,
    'pb': 5.0,
    'dividend': 2.5
}]
val_data = [{
    'code': '600519',
    'pe': 25.0,
    'pb': 5.0,
    'dividend': 2.5
}]

df = evaluator.evaluate(test_data, val_data)
if not df.empty:
    print(f"  ✅ 估值分析正常，找到 {len(df)} 只符合条件的股票")
else:
    print("  ⚠️ 没有符合筛选条件的股票")

# 测试8: 报告生成
print("\n[测试8] 报告生成...")
report_gen = ReportGenerator()

# 模拟数据
market_data = {
    'shanghai': {'price': 3200.0, 'change_pct': 0.5},
    'shenzhen': {'price': 11000.0, 'change_pct': 0.3},
}
recommendations = [{
    'code': '600519',
    'name': '贵州茅台',
    'price': 1500.0,
    'change_pct': 1.5,
    'pe': 25.0,
    'pb': 5.0,
    'dividend': 2.5,
    'valuation_score': 80.0,
    'recommend_reason': 'PE偏低'
}]
portfolio_summary = [{
    'code': '600519',
    'name': '贵州茅台',
    'amount': 100,
    'cost': 1500.0,
    'current_price': 1550.0,
    'profit': 5000.0,
    'profit_pct': 3.33
}]
portfolio_analysis = [{
    'code': '600519',
    'name': '贵州茅台',
    'current_price': 1550.0,
    'cost': 1500.0,
    'profit_pct': 3.33,
    'action': '持有',
    'reason': '正常波动'
}]

report = report_gen.generate_daily_report(
    market_data=market_data,
    recommendations=recommendations,
    portfolio_analysis=portfolio_analysis,
    portfolio_summary=portfolio_summary,
    portfolio_value=105000.0
)

if len(report) > 500:
    print(f"  ✅ 报告生成成功，长度: {len(report)} 字符")
    # 保存测试报告
    test_report_path = report_gen.save_report(report, "test_report.md")
    print(f"  ✅ 测试报告已保存: {test_report_path}")
else:
    print("  ❌ 报告内容异常")

# 测试9: 文件输出
print("\n[测试9] 文件输出...")
reports_dir = os.path.join(os.path.dirname(__file__), "reports")
if os.path.exists(reports_dir):
    print(f"  ✅ 报告目录存在: {reports_dir}")
else:
    print(f"  ❌ 报告目录不存在")

data_dir = os.path.join(os.path.dirname(__file__), "data")
if os.path.exists(data_dir):
    print(f"  ✅ 数据目录存在: {data_dir}")
else:
    print(f"  ⚠️ 数据目录不存在（正常，首次运行会创建）")

# 总结
print("\n" + "=" * 60)
print("验证测试完成!")
print("=" * 60)
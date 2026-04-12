"""
可视化图表模块
生成 K线图、估值区间图等
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(__file__), 
                '..', 'reports', 'charts'
            )
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_kline_html(self, stock_code: str, stock_name: str, history: List[Dict]) -> str:
        """
        生成 K线图 HTML
        使用简化的 Canvas 绘图，不需要第三方库
        """
        if not history or len(history) < 10:
            return ""
        
        # 取最近60天数据
        data = history[-60:]
        
        # 找到最高最低价
        highs = [h.get('high', 0) for h in data if h.get('high')]
        lows = [h.get('low', 0) for h in data if h.get('low')]
        
        if not highs or not lows:
            return ""
        
        max_price = max(highs)
        min_price = min(lows)
        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1
        
        # K线数据
        kline_data = []
        for h in data:
            o = h.get('open', 0)
            c = h.get('close', 0)
            high = h.get('high', 0)
            low = h.get('low', 0)
            date = h.get('date', '')[:10]
            
            kline_data.append({
                'date': date,
                'open': o,
                'close': c,
                'high': high,
                'low': low
            })
        
        # 生成 HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{stock_name} K线图</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #ddd; }}
        h2 {{ color: #fff; }}
        .chart-container {{ position: relative; height: 400px; border: 1px solid #333; }}
        canvas {{ width: 100%; height: 100%; }}
        .info {{ margin: 10px 0; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <h2>{stock_name} ({stock_code}) K线图</h2>
    <div class="info">数据来源: 东方财富 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
    <div class="chart-container">
        <canvas id="kline"></canvas>
    </div>
    <script>
    const data = {json.dumps(kline_data)};
    const maxPrice = {max_price};
    const minPrice = {min_price};
    const range = maxPrice - minPrice;
    
    const canvas = document.getElementById('kline');
    const ctx = canvas.getContext('2d');
    
    // 设置画布大小
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;
    
    // 绘制网格
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 5; i++) {{
        const y = padding + chartHeight * i / 5;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(canvas.width - padding, y);
        ctx.stroke();
        
        const price = maxPrice - range * i / 5;
        ctx.fillStyle = '#888';
        ctx.font = '10px Arial';
        ctx.fillText(price.toFixed(2), 5, y + 4);
    }}
    
    // 绘制K线
    const barWidth = chartWidth / data.length;
    
    data.forEach((d, i) => {{
        const x = padding + barWidth * i + barWidth * 0.1;
        const w = barWidth * 0.8;
        
        const isUp = d.close >= d.open;
        const color = isUp ? '#ef5350' : '#26a69a';
        
        // 影线
        const highY = padding + (maxPrice - d.high) / range * chartHeight;
        const lowY = padding + (maxPrice - d.low) / range * chartHeight;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x + w/2, highY);
        ctx.lineTo(x + w/2, lowY);
        ctx.stroke();
        
        // 实体
        const openY = padding + (maxPrice - d.open) / range * chartHeight;
        const closeY = padding + (maxPrice - d.close) / range * chartHeight;
        const bodyTop = Math.min(openY, closeY);
        const bodyHeight = Math.abs(closeY - openY) || 1;
        
        ctx.fillStyle = color;
        ctx.fillRect(x, bodyTop, w, bodyHeight);
    }});
    
    // 绘制均线（简化：20日收盘价均线）
    if (data.length >= 20) {{
        ctx.strokeStyle = '#ff9800';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        for (let i = 19; i < data.length; i++) {{
            let sum = 0;
            for (let j = i - 19; j <= i; j++) {{
                sum += data[j].close;
            }}
            const avg = sum / 20;
            const y = padding + (maxPrice - avg) / range * chartHeight;
            const x = padding + barWidth * i + barWidth / 2;
            
            if (i === 19) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();
    }}
    </script>
</body>
</html>"""
        
        return html
    
    def save_chart(self, html: str, filename: str) -> str:
        """保存图表到文件"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath
    
    def generate_valuation_chart(self, stock_code: str, stock_name: str, 
                                  current_price: float, history_data: List[Dict]) -> str:
        """
        生成估值区间图
        """
        if not history_data:
            return ""
        
        # 计算历史价格区间
        prices = [h.get('close', 0) for h in history_data if h.get('close')]
        if len(prices) < 10:
            return ""
        
        p10 = sorted(prices)[int(len(prices) * 0.1)]
        p30 = sorted(prices)[int(len(prices) * 0.3)]
        p50 = sorted(prices)[int(len(prices) * 0.5)]
        p70 = sorted(prices)[int(len(prices) * 0.7)]
        p90 = sorted(prices)[int(len(prices) * 0.9)]
        
        # 当前位置百分比
        if p90 > p10:
            position = (current_price - p10) / (p90 - p10) * 100
            position = max(0, min(100, position))
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{stock_name} 估值区间</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #ddd; }}
        h2 {{ color: #fff; }}
        .bar {{ height: 60px; background: linear-gradient(to right, #26a69a, #ef5350); border-radius: 30px; position: relative; margin: 40px 20px; }}
        .marker {{ position: absolute; top: -10px; width: 4px; height: 80px; background: #fff; }}
        .labels {{ display: flex; justify-content: space-between; margin: 10px 20px; color: #888; font-size: 12px; }}
        .current {{ text-align: center; margin: 20px; font-size: 24px; color: #fff; }}
    </style>
</head>
<body>
    <h2>{stock_name} ({stock_code}) 估值区间</h2>
    <div class="current">当前价格: ¥{current_price:.2f} ({position:.0f}%分位)</div>
    <div class="bar">
        <div class="marker" style="left: calc(20px + {(position/100) * (100% - 40px)});"></div>
    </div>
    <div class="labels">
        <span>极低 ¥{p10:.2f} (10%)</span>
        <span>偏低 ¥{p30:.2f} (30%)</span>
        <span>合理 ¥{p50:.2f} (50%)</span>
        <span>偏高 ¥{p70:.2f} (70%)</span>
        <span>极高 ¥{p90:.2f} (90%)</span>
    </div>
    <div style="text-align: center; color: #666; margin-top: 20px;">
        数据基于过去252个交易日
    </div>
</body>
</html>"""
        
        return html
    
    def generate_fund_performance_chart(self, fund_name: str, history: List[Dict]) -> str:
        """
        生成基金净值走势图
        """
        if not history:
            return ""
        
        # 提取数据
        navs = [h.get('nav', 0) for h in history if h.get('nav')]
        dates = [h.get('date', '') for h in history if h.get('nav')]
        
        if len(navs) < 2:
            return ""
        
        max_nav = max(navs)
        min_nav = min(navs)
        nav_range = max_nav - min_nav
        if nav_range == 0:
            nav_range = 1
        
        # 数据点
        points = []
        for i, (date, nav) in enumerate(zip(dates, navs)):
            points.append(f'{{date: "{date}", nav: {nav}}}')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{fund_name} 净值走势</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #ddd; }}
        h2 {{ color: #fff; }}
        canvas {{ width: 100%; height: 300px; }}
    </style>
</head>
<body>
    <h2>{fund_name} 净值走势</h2>
    <canvas id="chart"></canvas>
    <script>
    const data = [{','.join(points)}];
    const maxNav = {max_nav};
    const minNav = {min_nav};
    const range = maxNav - minNav;
    
    const canvas = document.getElementById('chart');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;
    
    // 绘制网格
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 5; i++) {{
        const y = padding + chartHeight * i / 5;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(canvas.width - padding, y);
        ctx.stroke();
        
        const nav = maxNav - range * i / 5;
        ctx.fillStyle = '#888';
        ctx.fillText(nav.toFixed(3), 5, y + 4);
    }}
    
    // 绘制折线
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    data.forEach((d, i) => {{
        const x = padding + chartWidth * i / (data.length - 1);
        const y = padding + (maxNav - d.nav) / range * chartHeight;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }});
    ctx.stroke();
    
    // 填充
    ctx.lineTo(padding + chartWidth, canvas.height - padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.closePath();
    ctx.fillStyle = 'rgba(76, 175, 80, 0.2)';
    ctx.fill();
    </script>
</body>
</html>"""
        
        return html


if __name__ == "__main__":
    generator = ChartGenerator()
    
    # 测试生成 K线图
    test_data = [
        {'date': '2024-01-01', 'open': 100, 'close': 102, 'high': 105, 'low': 99},
        {'date': '2024-01-02', 'open': 102, 'close': 98, 'high': 103, 'low': 97},
        {'date': '2024-01-03', 'open': 98, 'close': 105, 'high': 106, 'low': 97},
    ] * 20
    
    kline = generator.generate_kline_html('600519', '贵州茅台', test_data)
    if kline:
        print("K线图生成成功")
    
    val = generator.generate_valuation_chart('600519', '贵州茅台', 1500, test_data)
    if val:
        print("估值图生成成功")
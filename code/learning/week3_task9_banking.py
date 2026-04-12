# -*- coding: utf-8 -*-
"""
Week3 Task9: Banking Industry Analysis
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("="*70)
print("Banking Industry Deep Analysis")
print("="*70)

print("\n[1] Banking Business Model")
print("-"*50)
print("Income: Interest Spread + Fees + Investment")
print("Costs: Deposits Interest + Operations + Risk")

# Stock data
stocks = [
    {"name":"CIB", "code":"600036", "price":39.26, "pe":6.6, "pb":0.89, "roe":13.44, "nim":1.87, "npl":0.95, "coverage":391.79, "dividend":7.67},
    {"name":"Industrial Bank", "code":"601166", "price":18.60, "pe":5.08, "pb":0.49, "roe":9.15, "nim":1.47, "npl":0.87, "coverage":307.25, "dividend":3.14}
]

print("\n[2] Comparison")
print("-"*50)
print("Index        CIB    Industrial")
print(f"PE           {stocks[0]['pe']}    {stocks[1]['pe']}")
print(f"PB           {stocks[0]['pb']}    {stocks[1]['pb']}")
print(f"ROE          {stocks[0]['roe']}%    {stocks[1]['roe']}%")
print(f"NIM          {stocks[0]['nim']}%    {stocks[1]['nim']}%")
print(f"NPL          {stocks[0]['npl']}%    {stocks[1]['npl']}%")
print(f"Coverage     {stocks[0]['coverage']}%   {stocks[1]['coverage']}%")
print(f"Dividend     {stocks[0]['dividend']}%    {stocks[1]['dividend']}%")

print("\n[3] Interest Rate Impact")
print("-"*50)
print("Rate cuts -> NIM compression -> Pressure on profits")
print("BUT: Valuation extremely low (PB<1)")
print("Current dividends 3-8% -> Downside protection")

print("\n[4] Investment Conclusion")
print("-"*50)
print("Overall: Buy (cautiously)")
print("- CIB: Better for dividends (higher ROE/dividend)")
print("- Industrial Bank: Better for value (lower PE/PB)")
print("\nVerdict: Both undervalued, recommended to hold both")
print("="*70)

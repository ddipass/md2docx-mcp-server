import os
import subprocess

# 创建一个简单的 SVG 文件
svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:rgb(135,206,235);stop-opacity:1" />
      <stop offset="100%" style="stop-color:rgb(70,130,180);stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#grad1)" />
  <rect x="10" y="10" width="380" height="280" fill="none" stroke="darkblue" stroke-width="3"/>
  <text x="200" y="150" font-family="Arial" font-size="24" fill="darkblue" text-anchor="middle">Test Image</text>
  <text x="200" y="180" font-family="Arial" font-size="16" fill="darkblue" text-anchor="middle">LaTeX Graphics Test</text>
</svg>'''

# 写入 SVG 文件
with open('test_base.svg', 'w') as f:
    f.write(svg_content)

print("✅ 创建了基础 SVG 文件")

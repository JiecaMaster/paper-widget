#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体清晰度对比演示
"""

import tkinter as tk
from tkinter import ttk
from src.gui.main_window import PaperWidget

def create_clarity_demo():
    """创建字体清晰度对比演示"""
    
    # 启动主应用
    print("启动论文展示应用（带字体优化）...")
    app = PaperWidget()
    
    # 创建说明窗口
    demo_window = tk.Toplevel(app.root)
    demo_window.title("字体清晰度改进说明")
    demo_window.geometry("500x400")
    demo_window.transient(app.root)
    
    # 主框架
    frame = ttk.Frame(demo_window, padding="20")
    frame.pack(fill="both", expand=True)
    
    # 标题
    title = ttk.Label(frame, text="✨ 字体清晰度改进完成！", font=('Arial', 14, 'bold'))
    title.pack(pady=(0, 20))
    
    # 改进说明
    improvements = """
🔍 字体清晰度优化特性：

• 高DPI显示支持 - 自动检测并适配高分辨率显示器
• Windows DPI感知 - 启用Per-Monitor V2 DPI感知模式  
• 字体缩放优化 - 智能调整字体缩放比例（1.4x）
• ClearType支持 - 启用Windows字体平滑技术
• 抗锯齿渲染 - 优化字体边缘显示效果
• 最佳字体选择 - 使用Arial等高清晰度字体

💡 使用建议：

1. 主题切换：点击右上角按钮测试深浅主题
2. 高DPI显示器：确保Windows显示缩放设置合适
3. ClearType调整：在Windows设置中启用ClearType
4. 显示效果：文字应该看起来清晰锐利，无像素感

🎯 对比效果：

改进前：文字模糊，像素明显，影响阅读
改进后：文字清晰，边缘锐利，舒适阅读
    """
    
    text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 10), height=15)
    text_widget.insert('1.0', improvements)
    text_widget.config(state='disabled')
    text_widget.pack(fill="both", expand=True, pady=(0, 10))
    
    # 控制按钮
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x")
    
    def close_demo():
        demo_window.destroy()
    
    ttk.Button(btn_frame, text="关闭说明", command=close_demo).pack(side="right")
    ttk.Button(btn_frame, text="切换主题", command=app.toggle_theme).pack(side="right", padx=(0, 10))
    
    # 运行应用
    app.run()

if __name__ == "__main__":
    create_clarity_demo()
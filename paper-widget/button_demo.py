#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按钮字体大小对比演示
"""

import tkinter as tk
from tkinter import ttk
from src.gui.main_window import PaperWidget

def create_button_demo():
    """创建按钮字体大小对比演示"""
    
    print("启动按钮字体优化演示...")
    app = PaperWidget()
    
    # 创建对比窗口
    demo_window = tk.Toplevel(app.root)
    demo_window.title("按钮字体大小改进对比")
    demo_window.geometry("600x500")
    demo_window.transient(app.root)
    
    # 主框架
    frame = ttk.Frame(demo_window, padding="20")
    frame.pack(fill="both", expand=True)
    
    # 标题
    title = ttk.Label(frame, text="🔍 按钮字体大小改进", font=('Arial', 16, 'bold'))
    title.pack(pady=(0, 20))
    
    # 改进对比说明
    improvements = """
📊 按钮字体大小改进对比：

旧版本字体大小：
• 按钮字体：11pt（太小，难以阅读）
• 状态字体：10pt（看不清楚）
• 按钮间距：8px（过于紧密）

✨ 新版本字体大小：
• 按钮字体：14pt（增大27%，清晰易读）
• 状态字体：11pt（增大10%，更清晰）
• 按钮间距：12px（更舒适）
• 内边距：增加4px（点击区域更大）

🎯 响应式缩放：
• 小窗口(0.8x)：按钮字体 11pt
• 标准窗口(1.0x)：按钮字体 14pt  
• 大窗口(1.5x)：按钮字体 21pt
• 超大窗口(2.0x)：按钮字体 28pt

💡 用户体验提升：
• 字体更清晰，阅读无压力
• 按钮点击区域更大，操作更容易
• 间距合理，界面更美观
• 自适应缩放，适应不同显示器
    """
    
    text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 11), height=15)
    text_widget.insert('1.0', improvements)
    text_widget.config(state='disabled')
    text_widget.pack(fill="both", expand=True, pady=(0, 15))
    
    # 字体大小实时测试
    test_frame = ttk.LabelFrame(frame, text="实时字体测试", padding="15")
    test_frame.pack(fill="x", pady=(0, 15))
    
    # 获取当前字体大小
    button_font = app.theme_manager.get_font('button')
    status_font = app.theme_manager.get_font('status')
    
    info_text = f"""
当前按钮字体：{button_font[1]}pt {button_font[2]}
当前状态字体：{status_font[1]}pt {status_font[2]}
窗口缩放因子：{getattr(app, 'current_scale_factor', 1.0):.2f}x
    """
    
    info_label = ttk.Label(test_frame, text=info_text.strip(), font=('Arial', 10))
    info_label.pack(anchor="w")
    
    # 测试按钮区域
    test_buttons_frame = ttk.Frame(test_frame)
    test_buttons_frame.pack(fill="x", pady=(10, 0))
    
    # 创建测试按钮（使用应用的字体设置）
    test_btn1 = ttk.Button(
        test_buttons_frame,
        text="🔄 测试按钮1",
        style="Primary.TButton"
    )
    test_btn1.pack(side="left", padx=(0, 12), pady=2, ipady=4)
    
    test_btn2 = ttk.Button(
        test_buttons_frame,
        text="📥 测试按钮2",
        style="Secondary.TButton"
    )
    test_btn2.pack(side="left", padx=(0, 12), pady=2, ipady=4)
    
    test_btn3 = ttk.Button(
        test_buttons_frame,
        text="🌙 测试按钮3",
        style="Secondary.TButton"
    )
    test_btn3.pack(side="left", pady=2, ipady=4)
    
    # 控制按钮
    control_frame = ttk.Frame(frame)
    control_frame.pack(fill="x")
    
    def test_resize():
        """测试窗口大小调整"""
        current_geo = app.root.geometry()
        if "700x800" in current_geo or not current_geo:
            app.root.geometry("900x900")  # 变大
        else:
            app.root.geometry("700x800")  # 还原
    
    def close_demo():
        demo_window.destroy()
    
    ttk.Button(
        control_frame,
        text="测试窗口缩放",
        command=test_resize
    ).pack(side="left", padx=(0, 10))
    
    ttk.Button(
        control_frame,
        text="切换主题",
        command=app.toggle_theme
    ).pack(side="left", padx=(0, 10))
    
    ttk.Button(
        control_frame,
        text="关闭演示",
        command=close_demo
    ).pack(side="right")
    
    print("按钮字体改进演示已启动！")
    print("请对比查看按钮字体的清晰度改进效果。")
    
    # 运行应用
    app.run()

if __name__ == "__main__":
    create_button_demo()
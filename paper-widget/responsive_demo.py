#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应式布局演示工具
展示窗口大小调整时的自适应效果
"""

import tkinter as tk
from tkinter import ttk
from src.gui.main_window import PaperWidget

def create_responsive_demo():
    """创建响应式布局演示"""
    
    print("启动响应式论文展示应用...")
    app = PaperWidget()
    
    # 创建说明窗口
    demo_window = tk.Toplevel(app.root)
    demo_window.title("响应式布局使用说明")
    demo_window.geometry("450x500")
    demo_window.transient(app.root)
    
    # 主框架
    frame = ttk.Frame(demo_window, padding="20")
    frame.pack(fill="both", expand=True)
    
    # 标题
    title = ttk.Label(frame, text="🔧 响应式布局功能", font=('Arial', 14, 'bold'))
    title.pack(pady=(0, 20))
    
    # 功能说明
    instructions = """
✨ 响应式布局特性：

📏 字体大小改进：
• 标题字体：16pt（原12pt）
• 副标题字体：13pt（原10pt）  
• 正文字体：11pt（原9pt）
• 说明字体：10pt（原8pt）

📐 窗口自适应功能：
• 窗口大小检测：自动检测窗口尺寸变化
• 动态字体缩放：根据窗口大小调整字体
• 智能文本换行：自动适应窗口宽度
• 卡片间距调整：根据缩放调整边距

🎯 使用说明：

1. 拖拽窗口边缘调整大小
2. 观察卡片和文字自动缩放
3. 文本会自动换行适应宽度
4. 最小窗口：500x600像素
5. 推荐窗口：700x800像素以上

💡 缩放规律：
• 基准宽度：600像素
• 缩放范围：0.8x - 2.0x
• 更新阈值：0.1倍缩放差异

🎨 主题兼容：
• 深色/浅色主题都支持响应式
• 主题切换不影响缩放效果
    """
    
    text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 9), height=18)
    text_widget.insert('1.0', instructions)
    text_widget.config(state='disabled')
    text_widget.pack(fill="both", expand=True, pady=(0, 10))
    
    # 实时信息显示
    info_frame = ttk.LabelFrame(frame, text="实时信息", padding="10")
    info_frame.pack(fill="x", pady=(0, 10))
    
    window_info = ttk.Label(info_frame, text="窗口信息：正在检测...", font=('Arial', 9))
    window_info.pack(anchor="w")
    
    scale_info = ttk.Label(info_frame, text="缩放信息：正在检测...", font=('Arial', 9))
    scale_info.pack(anchor="w")
    
    def update_info():
        """更新实时信息"""
        try:
            width = app.root.winfo_width()
            height = app.root.winfo_height()
            scale = getattr(app, 'current_scale_factor', 1.0)
            
            window_info.config(text=f"窗口大小：{width} x {height} 像素")
            scale_info.config(text=f"当前缩放：{scale:.2f}x （字体自动调整）")
            
        except:
            pass
        
        # 每500ms更新一次
        demo_window.after(500, update_info)
    
    # 开始更新信息
    update_info()
    
    # 控制按钮
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x")
    
    def reset_size():
        app.root.geometry("700x800")
    
    def close_demo():
        demo_window.destroy()
    
    ttk.Button(btn_frame, text="重置窗口大小", command=reset_size).pack(side="left")
    ttk.Button(btn_frame, text="切换主题", command=app.toggle_theme).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="关闭说明", command=close_demo).pack(side="right")
    
    print("响应式演示已启动！")
    print("请尝试拖拽主窗口的边缘来调整大小，观察自适应效果。")
    
    # 运行应用
    app.run()

if __name__ == "__main__":
    create_responsive_demo()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体清晰度测试脚本
测试高DPI支持和字体渲染效果
"""

import tkinter as tk
from tkinter import ttk, font
from src.gui.theme_manager import ThemeManager
import sys

def create_font_demo():
    """创建字体演示窗口"""
    root = tk.Tk()
    root.title("字体清晰度测试 - Font Clarity Test")
    root.geometry("600x800")
    
    # 应用主题管理器
    theme_manager = ThemeManager(root)
    
    # 创建主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill="both", expand=True)
    
    # 标题
    title_label = ttk.Label(
        main_frame,
        text="字体清晰度对比测试",
        font=theme_manager.get_font('title')
    )
    title_label.pack(pady=(0, 20))
    
    # 系统信息
    info_frame = ttk.LabelFrame(main_frame, text="系统信息", padding="10")
    info_frame.pack(fill="x", pady=(0, 20))
    
    # 获取系统DPI信息
    try:
        dpi = root.winfo_fpixels('1i')
        scaling = root.tk.call('tk', 'scaling')
    except:
        dpi = 96
        scaling = 1.0
    
    info_text = f"""
    系统DPI: {dpi:.1f}
    Tkinter缩放: {scaling:.2f}
    Python版本: {sys.version.split()[0]}
    """
    
    ttk.Label(info_frame, text=info_text, font=theme_manager.get_font('body')).pack(anchor="w")
    
    # 字体测试区域
    font_frame = ttk.LabelFrame(main_frame, text="字体效果对比", padding="10")
    font_frame.pack(fill="both", expand=True)
    
    # 测试文本
    test_texts = [
        ("标题字体", "这是标题字体效果测试 - Title Font Test", 'title'),
        ("副标题字体", "这是副标题字体效果测试 - Subtitle Font Test", 'subtitle'), 
        ("正文字体", "这是正文字体效果测试 - Body Font Test", 'body'),
        ("说明字体", "这是说明字体效果测试 - Caption Font Test", 'caption'),
        ("按钮字体", "这是按钮字体效果测试 - Button Font Test", 'button'),
        ("状态字体", "这是状态字体效果测试 - Status Font Test", 'status')
    ]
    
    for name, text, font_type in test_texts:
        # 创建测试框架
        test_frame = ttk.Frame(font_frame)
        test_frame.pack(fill="x", pady=8)
        
        # 字体类型标签
        type_label = ttk.Label(
            test_frame,
            text=f"{name}:",
            font=theme_manager.get_font('caption'),
            width=12
        )
        type_label.pack(side="left", padx=(0, 10))
        
        # 测试文本标签
        text_label = tk.Label(
            test_frame,
            text=text,
            font=theme_manager.get_font(font_type),
            bg=theme_manager.get_current_colors()["card_bg"],
            fg=theme_manager.get_current_colors()["text_primary"],
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True)
    
    # 控制按钮
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill="x", pady=(20, 0))
    
    def toggle_theme():
        theme_manager.toggle_theme()
        # 更新所有文本标签的背景色
        colors = theme_manager.get_current_colors()
        for widget in font_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and hasattr(child, 'config'):
                        child.config(
                            bg=colors["card_bg"],
                            fg=colors["text_primary"]
                        )
    
    ttk.Button(
        control_frame,
        text="切换主题测试",
        command=toggle_theme
    ).pack(side="left", padx=(0, 10))
    
    ttk.Button(
        control_frame,
        text="关闭",
        command=root.destroy
    ).pack(side="right")
    
    # 说明文本
    help_text = """
说明：
• 如果文字看起来模糊或有锯齿，说明需要调整显示设置
• 在Windows 10/11中，建议在显示设置中启用ClearType
• 高DPI显示器用户请确保应用程序缩放设置正确
• 深浅主题切换可以测试不同背景下的字体效果
    """
    
    help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
    help_frame.pack(fill="x", pady=(20, 0))
    
    ttk.Label(
        help_frame,
        text=help_text,
        font=theme_manager.get_font('caption'),
        justify="left"
    ).pack(anchor="w")
    
    return root

def main():
    """运行字体测试"""
    try:
        print("启动字体清晰度测试...")
        root = create_font_demo()
        print("测试窗口已打开，请检查字体显示效果")
        root.mainloop()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
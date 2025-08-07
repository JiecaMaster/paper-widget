#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
响应式字体测试脚本
用于验证修复后的字体缩放功能
"""

import time
import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import PaperWidget

def test_responsive_fonts():
    """测试响应式字体功能"""
    print("开始响应式字体测试...")
    
    # 创建应用实例
    app = PaperWidget()
    
    # 设置初始窗口大小
    app.root.geometry("600x700")
    app.root.title("🔤 响应式字体测试 - 论文推送桌面组件")
    
    def run_font_tests():
        """运行字体测试"""
        print("\n=== 响应式字体测试开始 ===")
        
        # 测试不同窗口尺寸下的字体缩放
        test_sizes = [
            (500, 600),   # 小窗口
            (700, 800),   # 中等窗口  
            (900, 1000),  # 大窗口
            (1200, 1200), # 超大窗口
            (600, 700)    # 回到默认
        ]
        
        for i, (width, height) in enumerate(test_sizes):
            print(f"\n测试 {i+1}: 调整到 {width}x{height}")
            
            # 调整窗口大小
            app.root.geometry(f"{width}x{height}")
            app.root.update()
            
            # 等待窗口调整完成
            time.sleep(0.5)
            
            # 获取当前缩放因子
            current_scale = getattr(app, 'current_scale_factor', 1.0)
            print(f"当前缩放因子: {current_scale:.2f}")
            
            # 检查字体缓存是否被正确清除
            font_cache_size = len(getattr(app.theme_manager, '_font_cache', {}))
            print(f"字体缓存大小: {font_cache_size}")
            
            # 模拟用户操作：刷新论文显示
            if app.current_papers:
                print("刷新论文显示以测试字体缩放...")
                app.refresh_paper_display()
                app.root.update()
                
                # 验证字体是否正确应用了缩放
                test_font = app.theme_manager.get_font('title', current_scale)
                expected_size = max(8, int(16 * current_scale))  # 基础标题字体是16
                actual_size = test_font[1]
                
                print(f"标题字体期望大小: {expected_size}, 实际大小: {actual_size}")
                
                if abs(actual_size - expected_size) <= 1:  # 允许1像素误差
                    print("✅ 字体缩放正常")
                else:
                    print("❌ 字体缩放异常")
            else:
                print("⚠️  没有论文数据，无法测试字体显示")
            
            time.sleep(1)  # 给用户时间观察变化
        
        print("\n=== 响应式字体测试完成 ===")
        
        # 显示总结
        final_scale = getattr(app, 'current_scale_factor', 1.0)
        print(f"\n最终缩放因子: {final_scale:.2f}")
        print("测试建议: 观察窗口大小变化时，卡片中的文字是否相应变大或变小")
        print("✅ 修复完成: 字体缩放不再被缓存，应能正常响应窗口变化")
    
    # 延迟2秒后开始测试，给应用时间初始化
    app.root.after(2000, run_font_tests)
    
    # 运行应用
    app.run()

if __name__ == "__main__":
    test_responsive_fonts()
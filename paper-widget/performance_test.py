#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能测试脚本 - 测试窗口响应性和滚动性能
用于验证性能优化效果
"""

import time
import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import PaperWidget

class PerformanceMonitor:
    def __init__(self, widget_app):
        self.app = widget_app
        self.resize_times = []
        self.scroll_times = []
        self.theme_switch_times = []
        
        # Hook into resize events
        self.original_handle_resize = self.app.handle_window_resize
        self.app.handle_window_resize = self.monitor_resize
        
    def monitor_resize(self):
        start_time = time.time()
        self.original_handle_resize()
        end_time = time.time()
        
        resize_duration = (end_time - start_time) * 1000  # 转换为毫秒
        self.resize_times.append(resize_duration)
        print(f"窗口调整耗时: {resize_duration:.2f}ms")
        
    def test_resize_performance(self, test_count=10):
        """测试窗口调整性能"""
        print("=== 窗口调整性能测试 ===")
        
        original_sizes = [
            (600, 700), (800, 900), (1000, 1000), 
            (700, 800), (900, 1100), (650, 750),
            (1100, 1200), (550, 650), (850, 950), (750, 850)
        ]
        
        for i, (width, height) in enumerate(original_sizes[:test_count]):
            print(f"测试 {i+1}/{test_count}: 调整到 {width}x{height}")
            
            start_time = time.time()
            self.app.root.geometry(f"{width}x{height}")
            self.app.root.update()
            
            # 等待调整完成
            time.sleep(0.3)
            
        if self.resize_times:
            avg_time = sum(self.resize_times) / len(self.resize_times)
            max_time = max(self.resize_times)
            min_time = min(self.resize_times)
            
            print(f"\n调整性能统计:")
            print(f"平均耗时: {avg_time:.2f}ms")
            print(f"最大耗时: {max_time:.2f}ms")
            print(f"最小耗时: {min_time:.2f}ms")
            print(f"性能等级: {'优秀' if avg_time < 50 else '良好' if avg_time < 100 else '一般' if avg_time < 200 else '需优化'}")
        
    def test_scroll_smoothness(self):
        """测试滚动流畅度"""
        print("\n=== 滚动流畅度测试 ===")
        
        if hasattr(self.app, 'canvas') and self.app.current_papers:
            canvas = self.app.canvas
            
            # 模拟滚动事件
            scroll_tests = []
            
            for i in range(20):
                start_time = time.time()
                
                # 模拟向下滚动
                canvas.yview_scroll(1, "units")
                self.app.root.update()
                
                end_time = time.time()
                scroll_time = (end_time - start_time) * 1000
                scroll_tests.append(scroll_time)
                
                time.sleep(0.05)  # 模拟用户滚动频率
            
            if scroll_tests:
                avg_scroll_time = sum(scroll_tests) / len(scroll_tests)
                max_scroll_time = max(scroll_tests)
                
                print(f"滚动性能统计:")
                print(f"平均滚动耗时: {avg_scroll_time:.2f}ms")
                print(f"最大滚动耗时: {max_scroll_time:.2f}ms")
                print(f"滚动流畅度: {'优秀' if avg_scroll_time < 10 else '良好' if avg_scroll_time < 20 else '一般' if avg_scroll_time < 50 else '需优化'}")
    
    def test_theme_switch_performance(self):
        """测试主题切换性能"""
        print("\n=== 主题切换性能测试 ===")
        
        original_theme = self.app.theme_manager.current_theme
        
        # 测试多次主题切换
        switch_times = []
        
        for i in range(6):  # 3次完整的来回切换
            start_time = time.time()
            self.app.toggle_theme()
            self.app.root.update()
            end_time = time.time()
            
            switch_time = (end_time - start_time) * 1000
            switch_times.append(switch_time)
            
            theme = self.app.theme_manager.current_theme
            print(f"切换到{theme}主题耗时: {switch_time:.2f}ms")
            
            time.sleep(0.2)  # 等待切换完成
        
        if switch_times:
            avg_switch_time = sum(switch_times) / len(switch_times)
            max_switch_time = max(switch_times)
            
            print(f"\n主题切换性能统计:")
            print(f"平均切换耗时: {avg_switch_time:.2f}ms")
            print(f"最大切换耗时: {max_switch_time:.2f}ms")
            print(f"切换性能: {'优秀' if avg_switch_time < 100 else '良好' if avg_switch_time < 200 else '一般' if avg_switch_time < 500 else '需优化'}")
    
    def run_all_tests(self):
        """运行所有性能测试"""
        print("开始性能测试...\n")
        
        # 等待应用完全加载
        self.app.root.update()
        time.sleep(1)
        
        # 运行测试
        self.test_resize_performance()
        self.test_scroll_smoothness()
        self.test_theme_switch_performance()
        
        print("\n=== 性能测试完成 ===")

def main():
    print("启动性能测试...")
    
    # 创建应用实例
    app = PaperWidget()
    
    # 创建性能监控器
    monitor = PerformanceMonitor(app)
    
    # 设置测试窗口
    app.root.geometry("700x800")
    app.root.title("🔧 性能测试 - 论文推送桌面组件")
    
    def start_tests():
        """延迟启动测试"""
        app.root.after(2000, monitor.run_all_tests)
    
    # 启动测试
    start_tests()
    
    # 运行应用
    app.run()

if __name__ == "__main__":
    main()
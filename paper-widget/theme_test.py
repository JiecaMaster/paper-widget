#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题美化效果测试脚本
运行此脚本来查看新的美化效果
"""

import tkinter as tk
from src.gui.main_window import PaperWidget
import sys
import os

def test_theme_demo():
    """演示主题效果"""
    try:
        print("🎨 启动论文展示桌面组件主题演示...")
        
        # 创建应用实例
        app = PaperWidget()
        
        # 设置演示说明
        demo_info = """
        🌟 美化效果演示 🌟
        
        新功能特性：
        • ✨ 现代化界面设计 - Material Design风格
        • 🌙 深色/浅色主题切换
        • 🎨 会议标签颜色系统（AI蓝色，Security红色）
        • 📱 响应式卡片布局
        • 🔄 美化的状态指示器
        • 🎯 优化的交互体验
        
        操作指南：
        1. 点击右上角主题按钮切换深色/浅色模式
        2. 鼠标悬停在论文标题上查看交互效果
        3. 观察不同会议的颜色标识
        4. 体验现代化的按钮和状态显示
        """
        
        print(demo_info)
        print("\n🚀 界面已启动，请在窗口中体验新的美化效果!")
        print("💡 提示：点击右上角的主题切换按钮试试深色模式!")
        
        # 运行应用
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 演示结束")
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_theme_demo()
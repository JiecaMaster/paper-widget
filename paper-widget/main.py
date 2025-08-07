#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import PaperWidget
from gui.tray_icon import TrayIcon
try:
    from api.arxiv_fetcher_fuzzy import FuzzyArxivFetcher as ArxivFetcher
except ImportError:
    from api.arxiv_fetcher import ArxivFetcher

class PaperWidgetApp:
    def __init__(self):
        # 创建主窗口
        self.widget = PaperWidget()
        
        # 创建托盘图标
        self.tray_icon = TrayIcon(self.widget)
        
        # 绑定窗口关闭事件（最小化到托盘而不是退出）
        self.widget.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # 检查是否需要初始化数据
        self.check_initial_data()
        
    def hide_window(self):
        """隐藏窗口到系统托盘"""
        self.widget.root.withdraw()
        
        # 显示托盘提示（如果是第一次）
        if not hasattr(self, 'first_hide_shown'):
            self.first_hide_shown = True
            # Windows系统会自动显示托盘提示
    
    def check_initial_data(self):
        """检查是否需要初始化数据"""
        db_path = os.path.join("data", "papers_cache.db")
        
        if not os.path.exists(db_path) or os.path.getsize(db_path) < 1000:
            # 数据库不存在或为空，提示用户
            response = messagebox.askyesno(
                "初始化",
                "检测到首次运行，是否立即从arXiv获取论文数据？\n这可能需要几分钟时间。"
            )
            
            if response:
                # 在后台线程中更新数据
                def init_data():
                    try:
                        fetcher = ArxivFetcher()
                        fetcher.update_cache()
                        self.widget.root.after(0, lambda: messagebox.showinfo("完成", "论文数据初始化完成！"))
                        self.widget.root.after(0, self.widget.refresh_papers)
                    except Exception as e:
                        self.widget.root.after(0, lambda: messagebox.showerror("错误", f"初始化失败: {str(e)}"))
                
                thread = threading.Thread(target=init_data, daemon=True)
                thread.start()
    
    def run(self):
        """运行应用程序"""
        # 启动托盘图标
        self.tray_icon.run()
        
        # 运行主窗口
        self.widget.run()

def main():
    """主函数"""
    try:
        # 切换到脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # 检查配置文件
        config_path = os.path.join(script_dir, "config.json")
        if not os.path.exists(config_path):
            messagebox.showerror("错误", f"配置文件不存在: {config_path}")
            sys.exit(1)
        
        # 创建并运行应用
        app = PaperWidgetApp()
        app.run()
        
    except Exception as e:
        messagebox.showerror("错误", f"程序运行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
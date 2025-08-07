#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI测试脚本 - 测试美化效果
"""

import tkinter as tk
from src.gui.main_window import PaperWidget
import sys
import os

def main():
    """运行UI测试"""
    try:
        print("Starting Paper Widget with new UI themes...")
        
        # Create and run the application
        app = PaperWidget()
        
        print("Application started successfully!")
        print("New features:")
        print("- Modern Material Design interface")
        print("- Light/Dark theme toggle (top-right button)")
        print("- Color-coded conference badges")
        print("- Enhanced card layouts")
        print("- Improved status indicators")
        
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import ttk
import sv_ttk
import sys
import os
try:
    from tkinter import font
except ImportError:
    import tkFont as font

class ThemeManager:
    """现代化主题管理器"""
    
    def __init__(self, root):
        self.root = root
        self.current_theme = "light"
        self.style = ttk.Style()
        
        # 配置高DPI支持
        self._configure_high_dpi()
        
        # 获取最佳字体设置
        self.fonts = self._get_optimal_fonts()
        
        # 缩放因子
        self.current_scale_factor = 1.0
        
        # 定义配色方案
        self.colors = {
            "light": {
                "bg": "#FFFFFF",
                "surface": "#F8F9FA",
                "primary": "#2196F3",
                "secondary": "#FF5722",
                "text_primary": "#212121",
                "text_secondary": "#757575",
                "accent": "#4CAF50",
                "error": "#F44336",
                "warning": "#FF9800",
                "info": "#00BCD4",
                "card_bg": "#FFFFFF",
                "border": "#E0E0E0",
                "hover": "#F5F5F5"
            },
            "dark": {
                "bg": "#121212",
                "surface": "#1E1E1E",
                "primary": "#2196F3",
                "secondary": "#FF7043",
                "text_primary": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "accent": "#4CAF50",
                "error": "#F44336",
                "warning": "#FF9800",
                "info": "#00BCD4",
                "card_bg": "#2C2C2C",
                "border": "#404040",
                "hover": "#333333"
            }
        }
        
        # 会议颜色映射
        self.conference_colors = {
            "ai": {
                "light": {"bg": "#E3F2FD", "text": "#1976D2", "border": "#2196F3"},
                "dark": {"bg": "#1A237E", "text": "#64B5F6", "border": "#2196F3"}
            },
            "security": {
                "light": {"bg": "#FFEBEE", "text": "#C62828", "border": "#F44336"},
                "dark": {"bg": "#B71C1C", "text": "#EF5350", "border": "#F44336"}
            }
        }
        
        # 初始化主题
        self.apply_theme()
    
    def _configure_high_dpi(self):
        """配置高DPI支持"""
        try:
            # Windows高DPI支持
            if sys.platform.startswith('win'):
                try:
                    # 设置DPI感知
                    import ctypes
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor V2
                except:
                    try:
                        ctypes.windll.user32.SetProcessDPIAware()  # 系统DPI感知
                    except:
                        pass
                
                # 启用高DPI缩放
                self.root.tk.call('tk', 'scaling', '-displayof', '.', 1.4)
                
                # 启用字体平滑和ClearType
                try:
                    # 设置字体平滑选项
                    self.root.option_add('*Font', 'Arial')
                    self.root.option_add('*foreground', 'black')
                    
                    # 启用字体抗锯齿
                    import tkinter.font as tkfont
                    default_font = tkfont.nametofont("TkDefaultFont")
                    default_font.configure(family="Arial")
                    
                    text_font = tkfont.nametofont("TkTextFont")
                    text_font.configure(family="Arial")
                    
                    fixed_font = tkfont.nametofont("TkFixedFont")
                    fixed_font.configure(family="Consolas")
                    
                except Exception as font_error:
                    print(f"字体配置警告: {font_error}")
                
        except Exception as e:
            print(f"DPI配置警告: {e}")
    
    def _get_optimal_fonts(self):
        """获取最佳字体配置"""
        try:
            # 检测系统可用字体
            available_fonts = font.families()
            
            # 优选字体列表（按优先级）
            font_preferences = {
                'sans': ['Segoe UI', 'Arial', 'Microsoft YaHei UI'],
                'mono': ['Consolas', 'Courier New']
            }
            
            # 选择最佳字体
            best_fonts = {}
            for font_type, font_list in font_preferences.items():
                for font_name in font_list:
                    if font_name in available_fonts:
                        best_fonts[font_type] = font_name
                        break
                else:
                    # 默认字体
                    best_fonts[font_type] = font_list[-1]
            
            # 创建字体对象，启用抗锯齿
            fonts = {
                'title': font.Font(family=best_fonts['sans'], size=12, weight='bold'),
                'subtitle': font.Font(family=best_fonts['sans'], size=10, weight='bold'),
                'body': font.Font(family=best_fonts['sans'], size=9, weight='normal'),
                'caption': font.Font(family=best_fonts['sans'], size=8, weight='normal'),
                'button': font.Font(family=best_fonts['sans'], size=9, weight='normal'),
                'status': font.Font(family=best_fonts['sans'], size=8, weight='normal')
            }
            
            return fonts
            
        except Exception as e:
            print(f"字体配置警告: {e}")
            # 返回默认字体（更大尺寸，特别加大按钮字体）
            return {
                'title': ('Arial', 16, 'bold'),
                'subtitle': ('Arial', 13, 'bold'),
                'body': ('Arial', 11, 'normal'),
                'caption': ('Arial', 10, 'normal'),
                'button': ('Arial', 14, 'normal'),  # 大幅增加按钮字体
                'status': ('Arial', 11, 'normal')
            }
    
    def get_current_colors(self):
        """获取当前主题颜色"""
        return self.colors[self.current_theme]
    
    def get_conference_colors(self, conference_type):
        """获取会议类型对应的颜色"""
        return self.conference_colors.get(conference_type, {}).get(self.current_theme, {})
    
    def apply_theme(self):
        """应用当前主题"""
        colors = self.get_current_colors()
        
        # 应用 sv-ttk 主题
        if self.current_theme == "dark":
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")
        
        # 自定义样式（使用更大的字体）
        self.style.configure("Card.TFrame", 
                           background=colors["card_bg"],
                           relief="flat",
                           borderwidth=1)
        
        self.style.configure("Title.TLabel",
                           background=colors["card_bg"],
                           foreground=colors["text_primary"],
                           font=self.get_font('title'))
        
        self.style.configure("Subtitle.TLabel",
                           background=colors["card_bg"],
                           foreground=colors["text_secondary"],
                           font=self.get_font('body'))
        
        self.style.configure("Conference.TLabel",
                           background=colors["primary"],
                           foreground="#FFFFFF",
                           font=self.get_font('caption'),
                           anchor="center")
        
        # 按钮样式
        self.style.configure("Primary.TButton",
                           font=self.get_font('button'),
                           focuscolor='none')
        
        self.style.configure("Secondary.TButton",
                           font=self.get_font('button'),
                           focuscolor='none')
        
        # 状态栏样式
        self.style.configure("Status.TLabel",
                           background=colors["surface"],
                           foreground=colors["text_secondary"],
                           font=self.get_font('status'))
        
        # 设置窗口背景
        self.root.configure(bg=colors["bg"])
    
    def toggle_theme(self):
        """切换主题"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        return self.current_theme
    
    def set_theme(self, theme_name):
        """设置指定主题"""
        if theme_name in self.colors:
            self.current_theme = theme_name
            self.apply_theme()
    
    def create_card_style(self, conference_type="default"):
        """创建卡片样式"""
        colors = self.get_current_colors()
        conf_colors = self.get_conference_colors(conference_type)
        
        style_name = f"{conference_type.title()}.Card.TFrame"
        
        if conf_colors:
            self.style.configure(style_name,
                               background=conf_colors["bg"],
                               relief="solid",
                               borderwidth=1)
        else:
            self.style.configure(style_name,
                               background=colors["card_bg"],
                               relief="solid",
                               borderwidth=1)
        
        return style_name
    
    def get_font(self, font_type, scale_factor=1.0):
        """获取指定类型的字体，支持动态缩放"""
        # 增大字体大小，提升可读性（特别加大按钮字体）
        base_font_configs = {
            'title': ('Arial', 16, 'bold'),      # 12 -> 16
            'subtitle': ('Arial', 13, 'bold'),   # 10 -> 13  
            'body': ('Arial', 11, 'normal'),     # 9 -> 11
            'caption': ('Arial', 10, 'normal'),  # 8 -> 10
            'button': ('Arial', 14, 'normal'),   # 9 -> 11 -> 14 (大幅增加)
            'status': ('Arial', 11, 'normal')    # 8 -> 10 -> 11
        }
        
        base_config = base_font_configs.get(font_type, ('Arial', 11, 'normal'))
        family, size, weight = base_config
        
        # 应用缩放因子
        scaled_size = max(8, int(size * scale_factor))
        
        return (family, scaled_size, weight)
    
    def get_conference_type(self, conference_name):
        """根据会议名称判断类型"""
        ai_conferences = ["NeurIPS", "ICML", "ICLR", "AAAI", "CVPR", "ICCV", "ACL", "EMNLP"]
        security_conferences = ["IEEE S&P", "USENIX Security", "CCS", "NDSS"]
        
        if conference_name in ai_conferences:
            return "ai"
        elif conference_name in security_conferences:
            return "security"
        else:
            return "default"
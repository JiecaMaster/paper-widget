import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import json
import threading
from datetime import datetime
import sys
import os
from .theme_manager import ThemeManager

# 添加父目录到路径以导入其他模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    # 优先使用模糊匹配版本
    from api.arxiv_fetcher_fuzzy import FuzzyArxivFetcher as ArxivFetcher
except ImportError:
    from api.arxiv_fetcher import ArxivFetcher

class PaperWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✨ 论文推送桌面组件")
        
        # 加载配置
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager(self.root)
        
        # 设置窗口（增大默认尺寸）
        width = max(600, self.config['settings']['window_width'])
        height = max(700, self.config['settings']['window_height'])
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(500, 600)  # 增大最小尺寸
        
        # 设置窗口图标（可选）
        self.root.iconbitmap(default='')
        
        # 初始化数据获取器
        self.fetcher = ArxivFetcher()
        
        # 当前显示的论文
        self.current_papers = []
        
        # 响应式布局参数
        self.current_scale_factor = 1.0
        self.min_card_width = 400
        
        # 性能优化参数
        self.resize_timer = None
        self.last_window_size = (width, height)
        self.is_resizing = False
        
        # 创建UI
        self.setup_ui()
        
        # 绑定窗口尺寸变化事件（使用防抖）
        self.root.bind('<Configure>', self.on_window_resize_debounced)
        
        # 首次加载论文
        self.refresh_papers()
        
        # 设置窗口置顶（可通过右键菜单切换）
        self.is_topmost = False
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        title_label = ttk.Label(
            title_frame,
            text="📄 AI & Security Papers",
            font=self.theme_manager.get_font('title')
        )
        title_label.pack(side=tk.LEFT)
        
        # 主题切换按钮（增加内边距）
        self.theme_btn = ttk.Button(
            title_frame,
            text="🌙 深色主题",
            command=self.toggle_theme,
            style="Secondary.TButton"
        )
        self.theme_btn.pack(side=tk.RIGHT, pady=2, ipady=4)
        
        # 顶部工具栏
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 按钮容器
        btn_frame = ttk.Frame(toolbar)
        btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 刷新按钮（增大字体和内边距）
        self.refresh_btn = ttk.Button(
            btn_frame, 
            text="🔄 刷新论文", 
            command=self.refresh_papers,
            style="Primary.TButton"
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 12), pady=2, ipady=4)
        
        # 更新缓存按钮
        self.update_btn = ttk.Button(
            btn_frame,
            text="📥 更新数据库",
            command=self.update_cache_async,
            style="Secondary.TButton"
        )
        self.update_btn.pack(side=tk.LEFT, padx=(0, 12), pady=2, ipady=4)
        
        # 置顶按钮
        self.topmost_btn = ttk.Button(
            btn_frame,
            text="📌 置顶窗口",
            command=self.toggle_topmost,
            style="Secondary.TButton"
        )
        self.topmost_btn.pack(side=tk.LEFT, padx=(0, 12), pady=2, ipady=4)
        
        # 清空数据库按钮
        self.clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ 清空缓存",
            command=self.clear_database_with_confirm,
            style="Secondary.TButton"
        )
        self.clear_btn.pack(side=tk.LEFT, pady=2, ipady=4)
        
        # 状态标签
        self.status_label = ttk.Label(
            toolbar, 
            text="✅ 就绪",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # 论文显示区域
        self.papers_frame = ttk.Frame(main_frame)
        self.papers_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建Canvas和滚动条（响应式改进）
        canvas = tk.Canvas(
            self.papers_frame, 
            highlightthickness=0,
            bg=self.theme_manager.get_current_colors()["bg"]
        )
        scrollbar = ttk.Scrollbar(self.papers_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # 保存canvas引用以便后续更新
        self.canvas = canvas
        
        def on_frame_configure(event):
            """scrollable_frame尺寸变化时更新滚动区域"""
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            """canvas尺寸变化时更新内部框架宽度"""
            canvas.itemconfig(canvas_window, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮和触摸板滚动（优化版本）
        def _on_mousewheel(event):
            # 优化滚动响应速度
            try:
                delta = int(-1 * (event.delta / 120))
                canvas.yview_scroll(delta, "units")
            except:
                # 兼容性处理
                canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        
        # 绑定滚动事件仅到canvas，而非全局
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
        # 焦点管理，确保滚动可用
        canvas.focus_set()
        
        # 优化canvas更新
        def optimize_canvas_updates():
            canvas.update_idletasks()
        
        self.canvas_update_callback = optimize_canvas_updates
        
        # 底部信息栏
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        self.info_label = ttk.Label(
            info_frame, 
            text="", 
            font=self.theme_manager.get_font('status'),
            style="Status.TLabel"
        )
        self.info_label.pack(side=tk.LEFT)
        
    def create_paper_card(self, paper, index):
        """创建单个论文卡片 - Material Design风格（响应式优化版本）"""
        # 获取当前缩放因子（不缓存scale，确保响应式）
        scale = getattr(self, 'current_scale_factor', 1.0)
        
        # 缓存颜色计算（但不缓存scale）
        if not hasattr(self, '_cached_colors'):
            self._cached_colors = self.theme_manager.get_current_colors()
        
        colors = self._cached_colors
        conference_type = self.theme_manager.get_conference_type(paper['conference'])
        conf_colors = self.theme_manager.get_conference_colors(conference_type)
        
        # 计算动态内边距和间距（优化版本）
        padding_x = max(15, int(20 * scale))
        padding_y = max(8, int(12 * scale))
        card_padding = max(16, int(20 * scale))
        
        # 主卡片容器
        card_container = ttk.Frame(self.scrollable_frame)
        card_container.pack(fill="x", pady=padding_y, padx=padding_x)
        
        # 创建卡片样式
        card_style = self.theme_manager.create_card_style(conference_type)
        
        # 论文卡片框架（动态内边距）
        card_frame = ttk.Frame(
            card_container,
            style=card_style,
            padding=str(card_padding)
        )
        card_frame.pack(fill="x", expand=True)
        
        # 顶部：会议标签和发布日期
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill="x", pady=(0, max(10, int(15 * scale))))
        
        # 会议标签（动态大小）
        label_padding = max(6, int(10 * scale))
        conference_label = tk.Label(
            header_frame,
            text=f" {paper['conference']} ",
            font=self.theme_manager.get_font('caption', scale),
            bg=conf_colors.get("border", colors["primary"]),
            fg="white",
            padx=label_padding,
            pady=max(3, int(4 * scale))
        )
        conference_label.pack(side=tk.LEFT)
        
        # 发布日期
        date_label = ttk.Label(
            header_frame,
            text=f"📅 {paper['published']}",
            font=self.theme_manager.get_font('caption', scale),
            style="Subtitle.TLabel"
        )
        date_label.pack(side=tk.RIGHT)
        
        # 标题（可点击）（动态换行宽度）
        window_width = self.root.winfo_width()
        wrap_length = max(400, int(window_width * 0.75))
        title_length = max(80, int(120 * scale))
        title_text = paper['title'][:title_length] + ("..." if len(paper['title']) > title_length else "")
        
        title_label = tk.Label(
            card_frame,
            text=title_text,
            font=self.theme_manager.get_font('subtitle', scale),
            fg=colors["primary"],
            bg=colors["card_bg"],
            cursor="hand2",
            wraplength=wrap_length,
            justify="left",
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, max(6, int(10 * scale))))
        
        # 绑定点击事件和悬停效果
        title_label.bind("<Button-1>", lambda e: self.open_paper(paper['pdf_url']))
        title_label.bind("<Enter>", lambda e: title_label.config(fg=colors["secondary"]))
        title_label.bind("<Leave>", lambda e: title_label.config(fg=colors["primary"]))
        
        # 作者信息（动态换行）
        authors = paper['authors']
        author_length = max(60, int(100 * scale))
        if len(authors) > author_length:
            authors = authors[:author_length] + "..."
        authors_label = ttk.Label(
            card_frame,
            text=f"👥 {authors}",
            font=self.theme_manager.get_font('body', scale),
            style="Subtitle.TLabel",
            wraplength=wrap_length
        )
        authors_label.pack(fill="x", pady=(0, max(4, int(6 * scale))))
        
        # 底部分隔线
        if index < len(self.current_papers) - 1:
            separator = ttk.Separator(card_container, orient='horizontal')
            separator.pack(fill="x", pady=(8, 0))
        
    def refresh_papers(self):
        """刷新显示的论文"""
        self.status_label.config(text="⏳ 正在加载...")
        self.refresh_btn.config(state="disabled")
        
        # 清空当前显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 获取随机论文
        try:
            self.current_papers = self.fetcher.get_random_papers(
                self.config['settings']['papers_per_refresh']
            )
            
            if not self.current_papers:
                # 如果缓存为空，先更新缓存
                self.update_cache_async()
                return
            
            # 显示论文
            for i, paper in enumerate(self.current_papers):
                self.create_paper_card(paper, i)
            
            # 更新信息
            self.info_label.config(
                text=f"📊 显示 {len(self.current_papers)} 篇论文 | 最后刷新: {datetime.now().strftime('%H:%M:%S')}"
            )
            self.status_label.config(text="✅ 就绪")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载论文失败: {str(e)}")
            self.status_label.config(text="❌ 错误")
        finally:
            self.refresh_btn.config(state="normal")
    
    def update_cache_async(self):
        """异步更新论文缓存（智能更新版本）"""
        def update():
            self.update_btn.config(state="disabled")
            self.status_label.config(text="🔄 正在智能更新数据库...")
            
            try:
                # 优先使用智能更新方法（如果存在）
                if hasattr(self.fetcher, 'update_cache_with_clean'):
                    self.fetcher.update_cache_with_clean()
                else:
                    self.fetcher.update_cache()
                self.root.after(0, lambda: self.status_label.config(text="✅ 更新完成"))
                self.root.after(0, self.refresh_papers)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"更新失败: {str(e)}"))
                self.root.after(0, lambda: self.status_label.config(text="❌ 更新失败"))
            finally:
                self.root.after(0, lambda: self.update_btn.config(state="normal"))
        
        thread = threading.Thread(target=update, daemon=True)
        thread.start()
    
    def open_paper(self, url):
        """在浏览器中打开论文"""
        webbrowser.open(url)
    
    def toggle_theme(self):
        """切换深色/浅色主题（性能优化版本）"""
        current_theme = self.theme_manager.toggle_theme()
        
        # 更新主题按钮文本
        if current_theme == "dark":
            self.theme_btn.config(text="☀️ 浅色主题")
        else:
            self.theme_btn.config(text="🌙 深色主题")
        
        # 清除缓存的颜色
        if hasattr(self, '_cached_colors'):
            del self._cached_colors
        
        # 更新画布背景颜色
        colors = self.theme_manager.get_current_colors()
        if hasattr(self, 'canvas'):
            self.canvas.config(bg=colors["bg"])
        
        # 使用异步刷新避免阻塞UI
        self.root.after_idle(self.refresh_paper_display)
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.is_topmost = not self.is_topmost
        self.root.attributes('-topmost', self.is_topmost)
        
        if self.is_topmost:
            self.topmost_btn.config(text="📌 取消置顶")
        else:
            self.topmost_btn.config(text="📌 置顶窗口")
    
    def clear_database_with_confirm(self):
        """清空数据库（带确认对话框）"""
        # 显示确认对话框
        result = messagebox.askyesno(
            "确认清空", 
            "确定要清空所有缓存的论文吗？\n\n此操作不可恢复，所有论文数据将被删除。\n建议在清空后重新更新数据库。",
            icon='warning'
        )
        
        if result:
            self.clear_database_async()
    
    def clear_database_async(self):
        """异步清空数据库"""
        def clear():
            self.clear_btn.config(state="disabled")
            self.status_label.config(text="🗑️ 正在清空数据库...")
            
            try:
                # 调用清空数据库方法
                if hasattr(self.fetcher, 'clear_database'):
                    success = self.fetcher.clear_database(confirm=True)
                    if success:
                        self.root.after(0, lambda: self.status_label.config(text="✅ 数据库已清空"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", "数据库已清空！\n\n请点击【更新数据库】获取新论文。"))
                        # 清空当前显示
                        self.root.after(0, self.clear_display)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("错误", "清空数据库失败"))
                        self.root.after(0, lambda: self.status_label.config(text="❌ 清空失败"))
                else:
                    # 如果使用的是基础版本，手动清空
                    import sqlite3
                    import os
                    db_path = os.path.join("data", "papers_cache.db")
                    if os.path.exists(db_path):
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM papers')
                        conn.commit()
                        conn.close()
                        self.root.after(0, lambda: self.status_label.config(text="✅ 数据库已清空"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", "数据库已清空！"))
                        self.root.after(0, self.clear_display)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"清空失败: {str(e)}"))
                self.root.after(0, lambda: self.status_label.config(text="❌ 清空失败"))
            finally:
                self.root.after(0, lambda: self.clear_btn.config(state="normal"))
        
        thread = threading.Thread(target=clear, daemon=True)
        thread.start()
    
    def clear_display(self):
        """清空当前显示的论文"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.current_papers = []
        self.info_label.config(text="📋 数据库已清空，请更新数据库获取新论文")
    
    def on_window_resize_debounced(self, event):
        """窗口大小变化时的防抖响应函数"""
        # 只响应主窗口的大小变化
        if event.widget != self.root:
            return
        
        # 标记正在调整大小
        self.is_resizing = True
        
        # 取消之前的定时器
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        
        # 设置新的定时器（防抖延迟200ms）
        self.resize_timer = self.root.after(200, self.handle_window_resize)
    
    def handle_window_resize(self):
        """实际处理窗口大小变化"""
        try:
            # 获取当前窗口尺寸
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            current_size = (window_width, window_height)
            
            # 检查尺寸是否真的发生了变化
            if current_size == self.last_window_size:
                return
            
            self.last_window_size = current_size
            
            # 计算缩放因子
            base_width = 600  # 基准宽度
            scale_factor = max(0.8, min(2.0, window_width / base_width))
            
            # 如果缩放因子变化显著，更新界面
            if abs(scale_factor - self.current_scale_factor) > 0.1:
                self.current_scale_factor = scale_factor
                self.update_responsive_layout()
        
        finally:
            # 重置调整大小标记
            self.is_resizing = False
            self.resize_timer = None
    
    def update_responsive_layout(self):
        """更新响应式布局（性能优化版本）"""
        try:
            # 避免在调整大小过程中频繁更新
            if self.is_resizing:
                return
            
            # 更新字体缩放
            self.theme_manager.current_scale_factor = self.current_scale_factor
            
            # 清除颜色缓存（但不清除scale缓存，因为我们不再缓存scale）
            if hasattr(self, '_cached_colors'):
                del self._cached_colors
            
            # 清除主题管理器中的字体缓存，确保新的scale生效
            if hasattr(self.theme_manager, '_font_cache'):
                self.theme_manager._font_cache.clear()
            
            # 重新刷新论文卡片以应用新的缩放（使用异步更新）
            if self.current_papers:
                self.root.after_idle(self.refresh_paper_display)
                
        except Exception as e:
            print(f"响应式布局更新警告: {e}")
    
    def refresh_paper_display(self):
        """仅刷新论文显示（不重新获取数据）- 性能优化版本"""
        # 避免在调整大小时重复刷新
        if self.is_resizing:
            return
        
        try:
            # 暂停canvas更新以提高性能
            if hasattr(self, 'canvas'):
                self.canvas.configure(scrollregion=(0, 0, 0, 0))
            
            # 批量销毁旧控件
            children = self.scrollable_frame.winfo_children()
            for widget in children:
                widget.destroy()
            
            # 清除颜色缓存，准备重新创建
            if hasattr(self, '_cached_colors'):
                del self._cached_colors
                
            # 清除主题管理器中的字体缓存，确保响应式字体生效
            if hasattr(self.theme_manager, '_font_cache'):
                self.theme_manager._font_cache.clear()
            
            # 重新显示论文（使用当前的scale因子）
            for i, paper in enumerate(self.current_papers):
                self.create_paper_card(paper, i)
            
            # 恢复canvas滚动区域
            if hasattr(self, 'canvas'):
                self.root.after_idle(lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        except Exception as e:
            print(f"刷新显示警告: {e}")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PaperWidget()
    app.run()
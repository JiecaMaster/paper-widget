import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import json
import threading
from datetime import datetime
import sys
import os

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
        self.root.title("AI & Security Papers")
        
        # 加载配置
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 设置窗口
        width = self.config['settings']['window_width']
        height = self.config['settings']['window_height']
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(350, 400)
        
        # 设置窗口图标（可选）
        self.root.iconbitmap(default='')
        
        # 初始化数据获取器
        self.fetcher = ArxivFetcher()
        
        # 当前显示的论文
        self.current_papers = []
        
        # 创建UI
        self.setup_ui()
        
        # 首次加载论文
        self.refresh_papers()
        
        # 设置窗口置顶（可通过右键菜单切换）
        self.is_topmost = False
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 顶部工具栏
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(
            toolbar, 
            text="🔄 刷新论文", 
            command=self.refresh_papers
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 更新缓存按钮
        self.update_btn = ttk.Button(
            toolbar,
            text="📥 更新数据库",
            command=self.update_cache_async
        )
        self.update_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 置顶按钮
        self.topmost_btn = ttk.Button(
            toolbar,
            text="📌 置顶窗口",
            command=self.toggle_topmost
        )
        self.topmost_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空数据库按钮
        self.clear_btn = ttk.Button(
            toolbar,
            text="🗑️ 清空缓存",
            command=self.clear_database_with_confirm
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # 状态标签
        self.status_label = ttk.Label(toolbar, text="就绪")
        self.status_label.pack(side=tk.RIGHT)
        
        # 论文显示区域
        self.papers_frame = ttk.Frame(main_frame)
        self.papers_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建Canvas和滚动条
        canvas = tk.Canvas(self.papers_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.papers_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 底部信息栏
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, text="", font=('Arial', 9))
        self.info_label.pack(side=tk.LEFT)
        
    def create_paper_card(self, paper, index):
        """创建单个论文卡片"""
        # 论文卡片框架
        card_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text=f"  {paper['conference']}  ",
            padding="10"
        )
        card_frame.pack(fill="x", pady=5, padx=5)
        
        # 标题（可点击）
        title_label = tk.Label(
            card_frame,
            text=paper['title'][:100] + ("..." if len(paper['title']) > 100 else ""),
            font=('Arial', 10, 'bold'),
            fg="blue",
            cursor="hand2",
            wraplength=400,
            justify="left"
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # 绑定点击事件
        title_label.bind("<Button-1>", lambda e: self.open_paper(paper['pdf_url']))
        
        # 作者
        authors = paper['authors']
        if len(authors) > 60:
            authors = authors[:60] + "..."
        authors_label = ttk.Label(
            card_frame,
            text=f"作者: {authors}",
            font=('Arial', 9)
        )
        authors_label.pack(anchor="w", pady=(0, 3))
        
        # 发布日期
        date_label = ttk.Label(
            card_frame,
            text=f"发布日期: {paper['published']}",
            font=('Arial', 9),
            foreground="gray"
        )
        date_label.pack(anchor="w")
        
    def refresh_papers(self):
        """刷新显示的论文"""
        self.status_label.config(text="正在加载...")
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
                text=f"显示 {len(self.current_papers)} 篇论文 | 最后刷新: {datetime.now().strftime('%H:%M:%S')}"
            )
            self.status_label.config(text="就绪")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载论文失败: {str(e)}")
            self.status_label.config(text="错误")
        finally:
            self.refresh_btn.config(state="normal")
    
    def update_cache_async(self):
        """异步更新论文缓存（智能更新版本）"""
        def update():
            self.update_btn.config(state="disabled")
            self.status_label.config(text="正在智能更新数据库...")
            
            try:
                # 优先使用智能更新方法（如果存在）
                if hasattr(self.fetcher, 'update_cache_with_clean'):
                    self.fetcher.update_cache_with_clean()
                else:
                    self.fetcher.update_cache()
                self.root.after(0, lambda: self.status_label.config(text="更新完成"))
                self.root.after(0, self.refresh_papers)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"更新失败: {str(e)}"))
                self.root.after(0, lambda: self.status_label.config(text="更新失败"))
            finally:
                self.root.after(0, lambda: self.update_btn.config(state="normal"))
        
        thread = threading.Thread(target=update, daemon=True)
        thread.start()
    
    def open_paper(self, url):
        """在浏览器中打开论文"""
        webbrowser.open(url)
    
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
            self.status_label.config(text="正在清空数据库...")
            
            try:
                # 调用清空数据库方法
                if hasattr(self.fetcher, 'clear_database'):
                    success = self.fetcher.clear_database(confirm=True)
                    if success:
                        self.root.after(0, lambda: self.status_label.config(text="数据库已清空"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", "数据库已清空！\n\n请点击"更新数据库"获取新论文。"))
                        # 清空当前显示
                        self.root.after(0, self.clear_display)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("错误", "清空数据库失败"))
                        self.root.after(0, lambda: self.status_label.config(text="清空失败"))
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
                        self.root.after(0, lambda: self.status_label.config(text="数据库已清空"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", "数据库已清空！"))
                        self.root.after(0, self.clear_display)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"清空失败: {str(e)}"))
                self.root.after(0, lambda: self.status_label.config(text="清空失败"))
            finally:
                self.root.after(0, lambda: self.clear_btn.config(state="normal"))
        
        thread = threading.Thread(target=clear, daemon=True)
        thread.start()
    
    def clear_display(self):
        """清空当前显示的论文"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.current_papers = []
        self.info_label.config(text="数据库已清空，请更新数据库获取新论文")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PaperWidget()
    app.run()
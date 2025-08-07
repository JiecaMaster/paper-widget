import pystray
from PIL import Image, ImageDraw
import threading

class TrayIcon:
    def __init__(self, main_window):
        self.main_window = main_window
        self.icon = None
        
    def create_image(self):
        """创建托盘图标"""
        # 创建一个简单的图标
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)
        
        # 绘制一个简单的文档图标
        dc.rectangle([10, 10, 54, 54], outline='black', width=2)
        dc.rectangle([10, 10, 54, 20], fill='blue')
        dc.line([15, 30, 49, 30], fill='black', width=2)
        dc.line([15, 38, 49, 38], fill='black', width=2)
        dc.line([15, 46, 49, 46], fill='black', width=2)
        
        return image
    
    def show_window(self, icon, item):
        """显示主窗口"""
        self.main_window.root.deiconify()
        self.main_window.root.lift()
    
    def refresh_papers(self, icon, item):
        """刷新论文"""
        self.main_window.root.after(0, self.main_window.refresh_papers)
    
    def update_cache(self, icon, item):
        """更新缓存"""
        self.main_window.root.after(0, self.main_window.update_cache_async)
    
    def quit_app(self, icon, item):
        """退出应用"""
        if self.icon:
            self.icon.stop()
        self.main_window.root.quit()
    
    def create_menu(self):
        """创建托盘菜单"""
        return pystray.Menu(
            pystray.MenuItem("显示窗口", self.show_window, default=True),
            pystray.MenuItem("-", None),
            pystray.MenuItem("刷新论文", self.refresh_papers),
            pystray.MenuItem("更新数据库", self.update_cache),
            pystray.MenuItem("-", None),
            pystray.MenuItem("退出", self.quit_app)
        )
    
    def run(self):
        """运行托盘图标"""
        image = self.create_image()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            "paper_widget",
            image,
            "论文推送助手",
            menu
        )
        
        # 在新线程中运行托盘图标
        def run_icon():
            self.icon.run()
        
        thread = threading.Thread(target=run_icon, daemon=True)
        thread.start()
    
    def stop(self):
        """停止托盘图标"""
        if self.icon:
            self.icon.stop()
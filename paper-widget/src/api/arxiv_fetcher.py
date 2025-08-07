import arxiv
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

class ArxivFetcher:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 获取项目根目录的配置文件路径
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(root_dir, "config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 使用项目根目录的data文件夹
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(root_dir, "data", "papers_cache.db")
        self._init_database()
        
    def _init_database(self):
        # 确保data目录存在
        data_dir = os.path.dirname(self.db_path)
        os.makedirs(data_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT NOT NULL,
                abstract TEXT,
                published DATE NOT NULL,
                pdf_url TEXT,
                conference TEXT,
                categories TEXT,
                fetched_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_recent_papers(self, days_back: int = 90) -> List[Dict[str, Any]]:
        """获取最近指定天数内的论文"""
        categories = self.config['settings']['arxiv_categories']
        papers = []
        
        # 构建arXiv查询
        start_date = datetime.now() - timedelta(days=days_back)
        
        for category in categories:
            try:
                # 使用arxiv库搜索
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=100,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                for result in search.results():
                    # 检查发布日期
                    if result.published.replace(tzinfo=None) < start_date:
                        continue
                    
                    paper = {
                        'id': result.entry_id,
                        'title': result.title,
                        'authors': ', '.join([author.name for author in result.authors]),
                        'abstract': result.summary,
                        'published': result.published.strftime('%Y-%m-%d'),
                        'pdf_url': result.pdf_url,
                        'categories': ', '.join(result.categories),
                        'conference': self._identify_conference(result.title, result.summary)
                    }
                    
                    if paper['conference']:  # 只保存识别到会议的论文
                        papers.append(paper)
                        
            except Exception as e:
                print(f"Error fetching {category}: {e}")
                
        return papers
    
    def _identify_conference(self, title: str, abstract: str) -> str:
        """识别论文所属的顶级会议"""
        text = (title + " " + abstract).upper()
        
        all_conferences = (
            self.config['conferences']['ai'] + 
            self.config['conferences']['security']
        )
        
        for conf in all_conferences:
            for keyword in conf['keywords']:
                if keyword.upper() in text:
                    return conf['name']
        
        # 特殊模式匹配（例如年份）
        patterns = [
            (r'NEURIPS\s*\d{4}', 'NeurIPS'),
            (r'ICML\s*\d{4}', 'ICML'),
            (r'ICLR\s*\d{4}', 'ICLR'),
            (r'CVPR\s*\d{4}', 'CVPR'),
            (r'AAAI[\s-]*\d{2,4}', 'AAAI'),
            (r'ACL\s*\d{4}', 'ACL'),
            (r'CCS\s*\d{4}', 'CCS'),
            (r'USENIX\s*SECURITY\s*\d{4}', 'USENIX Security')
        ]
        
        for pattern, conf_name in patterns:
            if re.search(pattern, text):
                return conf_name
                
        return None
    
    def save_papers_to_cache(self, papers: List[Dict[str, Any]]):
        """保存论文到缓存数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for paper in papers:
            cursor.execute('''
                INSERT OR REPLACE INTO papers 
                (id, title, authors, abstract, published, pdf_url, conference, categories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper['id'],
                paper['title'],
                paper['authors'],
                paper['abstract'],
                paper['published'],
                paper['pdf_url'],
                paper['conference'],
                paper['categories']
            ))
        
        conn.commit()
        conn.close()
    
    def get_random_papers(self, count: int = 5) -> List[Dict[str, Any]]:
        """从缓存中随机获取指定数量的论文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, authors, published, pdf_url, conference
            FROM papers
            WHERE conference IS NOT NULL
            ORDER BY RANDOM()
            LIMIT ?
        ''', (count,))
        
        papers = []
        for row in cursor.fetchall():
            papers.append({
                'id': row[0],
                'title': row[1],
                'authors': row[2],
                'published': row[3],
                'pdf_url': row[4],
                'conference': row[5]
            })
        
        conn.close()
        return papers
    
    def update_cache(self):
        """更新论文缓存"""
        print("正在更新论文缓存...")
        papers = self.fetch_recent_papers(self.config['settings']['cache_days'])
        self.save_papers_to_cache(papers)
        print(f"已缓存 {len(papers)} 篇论文")
        
        # 清理过期数据
        self._clean_old_papers()
    
    def _clean_old_papers(self):
        """清理超过缓存期限的论文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=self.config['settings']['cache_days'])).strftime('%Y-%m-%d')
        
        cursor.execute('DELETE FROM papers WHERE published < ?', (cutoff_date,))
        
        conn.commit()
        conn.close()
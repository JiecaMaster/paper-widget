"""
集成模糊匹配的arXiv论文获取器
支持更智能的会议识别
"""

import arxiv
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

# 导入模糊匹配器
from fuzzy_matcher import ConferenceFuzzyMatcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FuzzyArxivFetcher:
    def __init__(self, config_path: str = None, debug: bool = False):
        if config_path is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(root_dir, "config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(root_dir, "data", "papers_cache.db")
        self.debug = debug
        
        # 初始化模糊匹配器
        self.matcher = ConferenceFuzzyMatcher()
        
        self._init_database()
    
    def _init_database(self):
        """初始化数据库，增加置信度字段"""
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
                conference_year TEXT,
                confidence REAL,
                categories TEXT,
                comment TEXT,
                fetched_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # 创建会议统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conference_stats (
                conference TEXT PRIMARY KEY,
                total_papers INTEGER,
                avg_confidence REAL,
                last_updated DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_recent_papers(self, days_back: int = 90, max_per_category: int = 200) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        获取最近的论文并使用模糊匹配识别会议
        返回：(论文列表, 统计信息)
        """
        categories = self.config['settings']['arxiv_categories']
        all_papers = []
        stats = {
            'total_fetched': 0,
            'matched': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'unmatched': 0
        }
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        for category in categories:
            try:
                logger.info(f"正在搜索类别: {category}")
                
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=max_per_category,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                category_papers = []
                
                for result in search.results():
                    if result.published.replace(tzinfo=None) < start_date:
                        continue
                    
                    stats['total_fetched'] += 1
                    
                    # 提取基本信息
                    paper = {
                        'id': result.entry_id,
                        'title': result.title,
                        'authors': ', '.join([author.name for author in result.authors]),
                        'abstract': result.summary,
                        'published': result.published.strftime('%Y-%m-%d'),
                        'pdf_url': result.pdf_url,
                        'categories': ', '.join(result.categories),
                        'comment': result.comment if hasattr(result, 'comment') else "",
                    }
                    
                    # 使用模糊匹配识别会议
                    conference_info = self.matcher.is_conference_paper(
                        paper['title'],
                        paper['abstract'],
                        paper['comment']
                    )
                    
                    if conference_info:
                        paper['conference'] = conference_info['conference']
                        paper['conference_year'] = conference_info.get('year', '')
                        paper['confidence'] = conference_info['confidence']
                        
                        # 统计置信度分布
                        stats['matched'] += 1
                        if conference_info['confidence'] >= 0.9:
                            stats['high_confidence'] += 1
                        elif conference_info['confidence'] >= 0.75:
                            stats['medium_confidence'] += 1
                        else:
                            stats['low_confidence'] += 1
                        
                        category_papers.append(paper)
                        
                        if self.debug:
                            logger.debug(f"匹配: {paper['title'][:50]}... -> {conference_info['conference']} (置信度: {conference_info['confidence']:.2f})")
                    else:
                        stats['unmatched'] += 1
                        if self.debug and 'workshop' not in paper['title'].lower():
                            # 记录可能遗漏的论文（排除workshop）
                            logger.debug(f"未匹配: {paper['title'][:50]}...")
                            if paper['comment']:
                                logger.debug(f"  Comment: {paper['comment'][:100]}")
                
                all_papers.extend(category_papers)
                logger.info(f"  {category}: 获取 {stats['total_fetched']} 篇，匹配 {len(category_papers)} 篇")
                
            except Exception as e:
                logger.error(f"获取 {category} 时出错: {e}")
        
        # 显示统计信息
        if stats['matched'] > 0:
            logger.info(f"\n统计信息:")
            logger.info(f"  总获取: {stats['total_fetched']} 篇")
            logger.info(f"  已匹配: {stats['matched']} 篇 ({stats['matched']/stats['total_fetched']*100:.1f}%)")
            logger.info(f"  - 高置信度(≥0.9): {stats['high_confidence']} 篇")
            logger.info(f"  - 中置信度(0.75-0.9): {stats['medium_confidence']} 篇")
            logger.info(f"  - 低置信度(<0.75): {stats['low_confidence']} 篇")
            logger.info(f"  未匹配: {stats['unmatched']} 篇")
        
        return all_papers, stats
    
    def search_by_conference_fuzzy(self, conference_query: str, days_back: int = 90) -> List[Dict[str, Any]]:
        """
        使用模糊匹配搜索特定会议的论文
        支持各种会议名称变体
        """
        # 先用模糊匹配器标准化会议名称
        match_result = self.matcher.fuzzy_match_conference(conference_query)
        if not match_result:
            logger.warning(f"无法识别会议: {conference_query}")
            return []
        
        conference_name, _ = match_result
        logger.info(f"识别会议: {conference_query} -> {conference_name}")
        
        # 获取该会议的所有可能变体
        conf_info = self.matcher.conference_variants.get(conference_name, {})
        search_terms = conf_info.get('aliases', []) + conf_info.get('abbreviations', [])
        
        papers = []
        seen_ids = set()
        
        for term in search_terms:
            try:
                # 构建搜索查询
                search = arxiv.Search(
                    query=term,
                    max_results=100,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                for result in search.results():
                    if result.entry_id in seen_ids:
                        continue
                    
                    # 验证是否真的是该会议的论文
                    conference_info = self.matcher.is_conference_paper(
                        result.title,
                        result.summary,
                        result.comment if hasattr(result, 'comment') else ""
                    )
                    
                    if conference_info and conference_info['conference'] == conference_name:
                        paper = {
                            'id': result.entry_id,
                            'title': result.title,
                            'authors': ', '.join([author.name for author in result.authors]),
                            'abstract': result.summary,
                            'published': result.published.strftime('%Y-%m-%d'),
                            'pdf_url': result.pdf_url,
                            'categories': ', '.join(result.categories),
                            'conference': conference_info['conference'],
                            'conference_year': conference_info.get('year', ''),
                            'confidence': conference_info['confidence'],
                            'comment': result.comment if hasattr(result, 'comment') else "",
                        }
                        papers.append(paper)
                        seen_ids.add(result.entry_id)
                
            except Exception as e:
                logger.error(f"搜索 '{term}' 时出错: {e}")
        
        logger.info(f"找到 {len(papers)} 篇 {conference_name} 论文")
        return papers
    
    def save_papers_to_cache(self, papers: List[Dict[str, Any]]):
        """保存论文到缓存数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for paper in papers:
            cursor.execute('''
                INSERT OR REPLACE INTO papers 
                (id, title, authors, abstract, published, pdf_url, 
                 conference, conference_year, confidence, categories, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper['id'],
                paper['title'],
                paper['authors'],
                paper['abstract'],
                paper['published'],
                paper['pdf_url'],
                paper.get('conference'),
                paper.get('conference_year', ''),
                paper.get('confidence', 0.0),
                paper['categories'],
                paper.get('comment', '')
            ))
        
        # 更新会议统计
        self._update_conference_stats(cursor)
        
        conn.commit()
        conn.close()
    
    def _update_conference_stats(self, cursor):
        """更新会议统计信息"""
        cursor.execute('''
            INSERT OR REPLACE INTO conference_stats (conference, total_papers, avg_confidence)
            SELECT 
                conference,
                COUNT(*) as total,
                AVG(confidence) as avg_conf
            FROM papers
            WHERE conference IS NOT NULL
            GROUP BY conference
        ''')
    
    def get_conference_statistics(self) -> Dict[str, Dict[str, Any]]:
        """获取详细的会议统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                conference,
                COUNT(*) as total,
                AVG(confidence) as avg_confidence,
                MIN(confidence) as min_confidence,
                MAX(confidence) as max_confidence,
                COUNT(CASE WHEN confidence >= 0.9 THEN 1 END) as high_conf,
                COUNT(CASE WHEN confidence >= 0.75 AND confidence < 0.9 THEN 1 END) as medium_conf,
                COUNT(CASE WHEN confidence < 0.75 THEN 1 END) as low_conf
            FROM papers
            WHERE conference IS NOT NULL
            GROUP BY conference
            ORDER BY total DESC
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'total': row[1],
                'avg_confidence': row[2],
                'min_confidence': row[3],
                'max_confidence': row[4],
                'high_confidence': row[5],
                'medium_confidence': row[6],
                'low_confidence': row[7]
            }
        
        conn.close()
        return stats
    
    def get_random_papers(self, count: int = 5, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """
        获取随机论文，可设置最低置信度阈值
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, authors, published, pdf_url, conference, confidence
            FROM papers
            WHERE conference IS NOT NULL AND confidence >= ?
            ORDER BY RANDOM()
            LIMIT ?
        ''', (min_confidence, count))
        
        papers = []
        for row in cursor.fetchall():
            papers.append({
                'id': row[0],
                'title': row[1],
                'authors': row[2],
                'published': row[3],
                'pdf_url': row[4],
                'conference': row[5],
                'confidence': row[6]
            })
        
        conn.close()
        return papers
    
    def analyze_matching_quality(self):
        """分析匹配质量，帮助调优"""
        stats = self.get_conference_statistics()
        
        print("\n" + "=" * 80)
        print("会议论文匹配质量分析")
        print("=" * 80)
        
        for conf, stat in stats.items():
            print(f"\n{conf}:")
            print(f"  总数: {stat['total']} 篇")
            print(f"  平均置信度: {stat['avg_confidence']:.3f}")
            print(f"  置信度分布:")
            print(f"    - 高(≥0.9): {stat['high_confidence']} 篇 ({stat['high_confidence']/stat['total']*100:.1f}%)")
            print(f"    - 中(0.75-0.9): {stat['medium_confidence']} 篇 ({stat['medium_confidence']/stat['total']*100:.1f}%)")
            print(f"    - 低(<0.75): {stat['low_confidence']} 篇 ({stat['low_confidence']/stat['total']*100:.1f}%)")
            print(f"  置信度范围: {stat['min_confidence']:.3f} - {stat['max_confidence']:.3f}")
    
    def clear_database(self, confirm: bool = False) -> bool:
        """
        清空数据库中的所有论文
        Args:
            confirm: 是否确认删除，防止误操作
        Returns:
            是否成功清空
        """
        if not confirm:
            logger.warning("清空数据库需要确认参数")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 清空papers表
            cursor.execute('DELETE FROM papers')
            deleted_papers = cursor.rowcount
            
            # 清空conference_stats表
            cursor.execute('DELETE FROM conference_stats')
            
            # 如果存在unmatched_papers表，也清空
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unmatched_papers'")
            if cursor.fetchone():
                cursor.execute('DELETE FROM unmatched_papers')
            
            conn.commit()
            conn.close()
            
            logger.info(f"数据库已清空，删除了 {deleted_papers} 篇论文")
            return True
            
        except Exception as e:
            logger.error(f"清空数据库失败: {e}")
            return False
    
    def clear_old_conference_papers(self, conference_name: str) -> int:
        """
        清除特定会议的论文（用于删除CRYPTO等不需要的会议）
        Args:
            conference_name: 会议名称
        Returns:
            删除的论文数量
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM papers WHERE conference = ?', (conference_name,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"已删除 {conference_name} 的 {deleted_count} 篇论文")
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除会议论文失败: {e}")
            return 0
    
    def clean_outdated_papers(self, days: int = None) -> int:
        """
        清理过时的论文
        Args:
            days: 保留最近多少天的论文，None则使用配置文件中的值
        Returns:
            删除的论文数量
        """
        if days is None:
            days = self.config['settings']['cache_days']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('DELETE FROM papers WHERE published < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"已清理 {deleted_count} 篇过时论文（{days}天前）")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理过时论文失败: {e}")
            return 0
    
    def update_cache_with_clean(self):
        """
        更新缓存，但先清理过时数据和不需要的会议
        """
        logger.info("开始智能更新缓存...")
        
        # 1. 先清理CRYPTO相关会议（如果存在）
        crypto_conferences = ['CRYPTO', 'EUROCRYPT']
        for conf in crypto_conferences:
            deleted = self.clear_old_conference_papers(conf)
            if deleted > 0:
                logger.info(f"清理了 {conf} 会议的 {deleted} 篇论文")
        
        # 2. 清理过时论文
        self.clean_outdated_papers()
        
        # 3. 获取新论文
        logger.info("正在获取新论文...")
        matched_papers, _ = self.fetch_recent_papers(
            self.config['settings']['cache_days']
        )
        
        if matched_papers:
            self.save_papers_to_cache(matched_papers)
            logger.info(f"已缓存 {len(matched_papers)} 篇新论文")
            
            # 显示统计信息
            stats = self.get_conference_statistics()
            logger.info("各会议论文数量:")
            for conf, stat in stats.items():
                logger.info(f"  {conf}: {stat['total']} 篇")
        
        logger.info("缓存更新完成！")


def test_fuzzy_fetcher():
    """测试模糊匹配获取器"""
    fetcher = FuzzyArxivFetcher(debug=True)
    
    print("测试模糊匹配搜索...")
    print("-" * 40)
    
    # 测试各种会议名称变体
    test_queries = [
        "ICLR'25",
        "neurips 2025",
        "ICML25",
        "cvpr 25",
        "Oakland",  # IEEE S&P的别名
        "ccs",
    ]
    
    for query in test_queries:
        print(f"\n搜索: '{query}'")
        papers = fetcher.search_by_conference_fuzzy(query, days_back=30)
        if papers:
            print(f"  找到 {len(papers)} 篇论文")
            print(f"  示例: {papers[0]['title'][:60]}...")
            print(f"  置信度: {papers[0]['confidence']:.2f}")


if __name__ == "__main__":
    test_fuzzy_fetcher()
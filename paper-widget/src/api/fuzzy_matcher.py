"""
模糊匹配模块 - 用于识别各种会议名称变体
支持：
- 年份变体：'25, 25, 2025, '2025
- 缩写和全称
- 空格、连字符等分隔符
- 大小写不敏感
"""

import re
from typing import Optional, List, Tuple, Dict
from datetime import datetime
import difflib

class ConferenceFuzzyMatcher:
    def __init__(self):
        self.current_year = datetime.now().year
        
        # 定义会议的所有可能变体
        self.conference_variants = {
            'NeurIPS': {
                'aliases': ['NeurIPS', 'NIPS', 'Neural Information Processing Systems'],
                'abbreviations': ['NIPS', 'NeurIPS'],
                'keywords': ['neural', 'information', 'processing'],
                'common_patterns': [r'neur.*ips', r'nips'],
            },
            'ICML': {
                'aliases': ['ICML', 'International Conference on Machine Learning'],
                'abbreviations': ['ICML'],
                'keywords': ['machine', 'learning', 'icml'],
                'common_patterns': [r'icml'],
            },
            'ICLR': {
                'aliases': ['ICLR', 'International Conference on Learning Representations'],
                'abbreviations': ['ICLR'],
                'keywords': ['learning', 'representations', 'iclr'],
                'common_patterns': [r'iclr'],
            },
            'AAAI': {
                'aliases': ['AAAI', 'Association for the Advancement of Artificial Intelligence'],
                'abbreviations': ['AAAI'],
                'keywords': ['aaai', 'artificial', 'intelligence'],
                'common_patterns': [r'aaai'],
            },
            'CVPR': {
                'aliases': ['CVPR', 'Computer Vision and Pattern Recognition', 'IEEE CVPR'],
                'abbreviations': ['CVPR'],
                'keywords': ['cvpr', 'computer', 'vision', 'pattern'],
                'common_patterns': [r'cvpr'],
            },
            'ICCV': {
                'aliases': ['ICCV', 'International Conference on Computer Vision', 'IEEE ICCV'],
                'abbreviations': ['ICCV'],
                'keywords': ['iccv', 'computer', 'vision'],
                'common_patterns': [r'iccv'],
            },
            'ECCV': {
                'aliases': ['ECCV', 'European Conference on Computer Vision'],
                'abbreviations': ['ECCV'],
                'keywords': ['eccv', 'european', 'computer', 'vision'],
                'common_patterns': [r'eccv'],
            },
            'NAACL': {
                'aliases': ['NAACL', 'North American Chapter of ACL', 'North American ACL'],
                'abbreviations': ['NAACL'],
                'keywords': ['naacl'],
                'common_patterns': [r'naacl'],
            },
            'ACL': {
                'aliases': ['ACL', 'Association for Computational Linguistics', 'Annual Meeting of ACL'],
                'abbreviations': ['ACL'],
                'keywords': ['acl', 'computational', 'linguistics'],
                'common_patterns': [r'(?<!na)acl(?!-)'],  # 避免匹配 NAACL 和 ACL-IJCNLP 等
            },
            'EMNLP': {
                'aliases': ['EMNLP', 'Empirical Methods in Natural Language Processing'],
                'abbreviations': ['EMNLP'],
                'keywords': ['emnlp', 'empirical', 'nlp'],
                'common_patterns': [r'emnlp'],
            },
            # 安全会议
            'IEEE S&P': {
                'aliases': ['IEEE S&P', 'IEEE SP', 'S&P', 'Oakland', 'IEEE Security and Privacy', 
                           'IEEE Symposium on Security and Privacy'],
                'abbreviations': ['S&P', 'SP', 'Oakland'],
                'keywords': ['ieee', 's&p', 'oakland', 'security', 'privacy'],
                'common_patterns': [r's\s*&?\s*p', r'oakland', r'ieee.*security'],
            },
            'USENIX Security': {
                'aliases': ['USENIX Security', 'USENIX SEC', 'USENIX', 'Security Symposium'],
                'abbreviations': ['USENIX', 'SEC'],
                'keywords': ['usenix', 'security'],
                'common_patterns': [r'usenix.*sec', r'security.*symp'],
            },
            'CCS': {
                'aliases': ['CCS', 'ACM CCS', 'Computer and Communications Security',
                           'Conference on Computer and Communications Security'],
                'abbreviations': ['CCS'],
                'keywords': ['ccs', 'computer', 'communications', 'security'],
                'common_patterns': [r'(?:acm\s*)?ccs(?!\w)'],  # 避免匹配 access 等词
            },
            'NDSS': {
                'aliases': ['NDSS', 'Network and Distributed System Security', 'NDSS Symposium'],
                'abbreviations': ['NDSS'],
                'keywords': ['ndss', 'network', 'distributed', 'security'],
                'common_patterns': [r'ndss'],
            },
        }
        
        # 生成所有可能的年份变体
        self._generate_year_patterns()
    
    def _generate_year_patterns(self) -> List[str]:
        """生成当前和近期年份的所有可能格式"""
        patterns = []
        for year in range(self.current_year - 2, self.current_year + 3):
            # 2025, 2024, etc.
            patterns.append(str(year))
            # 25, 24, etc.
            patterns.append(str(year)[2:])
            # '25, '24, etc.
            patterns.append(f"'{str(year)[2:]}")
            # '25, '24 with optional space
            patterns.append(f"'\\s*{str(year)[2:]}")
        
        self.year_patterns = patterns
        return patterns
    
    def normalize_text(self, text: str) -> str:
        """标准化文本：去除多余空格、统一分隔符等"""
        # 转换为大写
        text = text.upper()
        
        # 统一各种分隔符
        text = re.sub(r'[-_/\\]', ' ', text)
        
        # 处理撇号和引号
        text = re.sub(r'[''`´]', "'", text)
        
        # 压缩多个空格为一个
        text = re.sub(r'\s+', ' ', text)
        
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def extract_year(self, text: str) -> Optional[str]:
        """从文本中提取年份"""
        text = self.normalize_text(text)
        
        # 匹配各种年份格式
        year_regex = r"(?:'?\s*)?(\d{4}|\d{2})(?:\s|$|[^\d])"
        
        matches = re.findall(year_regex, text)
        for match in matches:
            if len(match) == 4:
                # 完整年份
                year = int(match)
                if 2020 <= year <= 2030:
                    return str(year)
            elif len(match) == 2:
                # 两位年份
                year = int(match)
                if 20 <= year <= 30:
                    return f"20{match}"
        
        return None
    
    def fuzzy_match_conference(self, text: str, threshold: float = 0.75) -> Optional[Tuple[str, float]]:
        """
        模糊匹配会议名称
        返回：(会议名称, 置信度) 或 None
        """
        text = self.normalize_text(text)
        best_match = None
        best_score = 0.0
        
        for conf_name, conf_info in self.conference_variants.items():
            # 1. 精确匹配缩写
            for abbr in conf_info['abbreviations']:
                # 创建各种可能的模式
                patterns = [
                    rf'\b{re.escape(abbr)}\b',  # 完整单词匹配
                    rf'{re.escape(abbr)}\s*\d{{2,4}}',  # 后跟年份
                    rf"{re.escape(abbr)}\s*[']?\d{{2}}",  # 后跟 '25 格式
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        score = 1.0
                        if score > best_score:
                            best_match = conf_name
                            best_score = score
            
            # 2. 正则表达式模式匹配
            for pattern in conf_info['common_patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    score = 0.9
                    if score > best_score:
                        best_match = conf_name
                        best_score = score
            
            # 3. 模糊字符串匹配（针对完整名称）
            for alias in conf_info['aliases']:
                # 使用 difflib 进行相似度计算
                similarity = difflib.SequenceMatcher(None, 
                    self.normalize_text(alias), text).ratio()
                
                if similarity > threshold and similarity > best_score:
                    best_match = conf_name
                    best_score = similarity
            
            # 4. 关键词匹配（多个关键词同时出现）
            keywords_found = sum(1 for kw in conf_info['keywords'] 
                                if kw.upper() in text)
            if len(conf_info['keywords']) > 0:
                keyword_score = keywords_found / len(conf_info['keywords'])
                if keyword_score > threshold and keyword_score > best_score:
                    best_match = conf_name
                    best_score = keyword_score * 0.8  # 关键词匹配置信度略低
        
        if best_match:
            return (best_match, best_score)
        return None
    
    def match_conference_with_year(self, text: str) -> Optional[Dict[str, str]]:
        """
        匹配会议名称和年份
        返回：{'conference': 'ICLR', 'year': '2025', 'confidence': 0.95}
        """
        result = self.fuzzy_match_conference(text)
        if not result:
            return None
        
        conference, confidence = result
        year = self.extract_year(text)
        
        return {
            'conference': conference,
            'year': year or str(self.current_year),
            'confidence': confidence
        }
    
    def is_conference_paper(self, title: str, abstract: str, comment: str = "") -> Optional[Dict[str, str]]:
        """
        判断是否为会议论文并识别会议
        检查标题、摘要和评论字段
        """
        # 优先检查 comment（通常包含会议信息）
        if comment:
            result = self.match_conference_with_year(comment)
            if result and result['confidence'] > 0.8:
                return result
        
        # 检查标题
        result = self.match_conference_with_year(title)
        if result and result['confidence'] > 0.85:
            return result
        
        # 检查摘要（降低置信度要求）
        result = self.match_conference_with_year(abstract[:500])  # 只检查摘要前500字符
        if result and result['confidence'] > 0.7:
            result['confidence'] *= 0.9  # 从摘要匹配的置信度略低
            return result
        
        # 组合检查（标题+摘要）
        combined = f"{title} {abstract[:200]}"
        result = self.match_conference_with_year(combined)
        if result:
            result['confidence'] *= 0.85
            return result
        
        return None
    
    def find_all_conferences(self, text: str) -> List[Dict[str, str]]:
        """
        从文本中找出所有可能的会议
        用于处理包含多个会议的情况（如 workshop）
        """
        conferences = []
        text_normalized = self.normalize_text(text)
        
        for conf_name, conf_info in self.conference_variants.items():
            for abbr in conf_info['abbreviations']:
                # 搜索所有出现的位置
                pattern = rf'\b{re.escape(abbr)}\b'
                if re.search(pattern, text_normalized, re.IGNORECASE):
                    year = self.extract_year(text_normalized)
                    conferences.append({
                        'conference': conf_name,
                        'year': year or str(self.current_year),
                        'confidence': 0.95
                    })
                    break
        
        return conferences


def test_fuzzy_matcher():
    """测试模糊匹配器"""
    matcher = ConferenceFuzzyMatcher()
    
    # 测试用例
    test_cases = [
        # 标准格式
        ("Accepted to ICLR 2025", "ICLR"),
        ("To appear in NeurIPS'25", "NeurIPS"),
        ("ICML 25 paper", "ICML"),
        
        # 变体格式
        ("Accepted at ICLR'25", "ICLR"),
        ("NeurIPS-2025 submission", "NeurIPS"),
        ("CVPR25 camera ready", "CVPR"),
        
        # 完整名称
        ("International Conference on Learning Representations", "ICLR"),
        ("Neural Information Processing Systems 2025", "NeurIPS"),
        
        # 安全会议
        ("IEEE S&P 2025", "IEEE S&P"),
        ("Oakland '25", "IEEE S&P"),
        ("USENIX Security Symposium", "USENIX Security"),
        ("ACM CCS'25", "CCS"),
        
        # 复杂情况
        ("Workshop at ICML'25", "ICML"),
        ("Rejected from ICLR, accepted to NeurIPS", "NeurIPS"),
        
        # 缩写变体
        ("NIPS 2025", "NeurIPS"),
        ("S&P25", "IEEE S&P"),
    ]
    
    print("=" * 80)
    print("模糊匹配测试")
    print("=" * 80)
    
    for text, expected in test_cases:
        result = matcher.match_conference_with_year(text)
        if result:
            status = "✓" if result['conference'] == expected else "✗"
            print(f"{status} '{text}'")
            print(f"   -> {result['conference']} {result.get('year', '')} (置信度: {result['confidence']:.2f})")
        else:
            print(f"✗ '{text}' -> 未匹配")
        print()


if __name__ == "__main__":
    test_fuzzy_matcher()
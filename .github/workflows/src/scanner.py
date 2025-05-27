#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
过期域名扫描和AI分析系统
Expired Domain Scanner with AI Analysis
"""

import os
import sys
import time
import json
import random
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
from urllib.parse import urljoin, urlparse
import tldextract

# Web scraping imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Machine learning and text analysis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

# Configuration and logging
from dotenv import load_dotenv
import yaml

class DomainAnalyzer:
    """AI域名价值分析器"""
    
    def __init__(self):
        self.high_value_keywords = [
            'ai', 'crypto', 'bitcoin', 'nft', 'tech', 'app', 'web', 'digital',
            'online', 'shop', 'store', 'market', 'finance', 'investment',
            'healthcare', 'medical', 'education', 'learning', 'consulting',
            'service', 'solution', 'platform', 'system', 'network'
        ]
        
        self.premium_tlds = ['.com', '.net', '.org', '.io', '.ai', '.co']
        
        # 初始化TF-IDF向量化器
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            stop_words='english'
        )
        
    def analyze_domain_value(self, domain_data: Dict) -> Dict:
        """
        综合分析域名价值
        
        Args:
            domain_data: 域名数据字典
            
        Returns:
            包含分析结果的字典
        """
        domain_name = domain_data.get('domain', '')
        
        # 各项评分
        scores = {
            'length_score': self._analyze_length(domain_name),
            'keyword_score': self._analyze_keywords(domain_name),
            'brandability_score': self._analyze_brandability(domain_name),
            'seo_score': self._analyze_seo_potential(domain_data),
            'technical_score': self._analyze_technical_metrics(domain_data),
            'commercial_score': self._analyze_commercial_value(domain_name)
        }
        
        # 权重计算总分
        weights = {
            'length_score': 0.15,
            'keyword_score': 0.25,
            'brandability_score': 0.20,
            'seo_score': 0.20,
            'technical_score': 0.15,
            'commercial_score': 0.05
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores)
        
        # 生成推荐等级
        recommendation = self._generate_recommendation(total_score, scores)
        
        return {
            'domain': domain_name,
            'total_score': round(total_score, 2),
            'individual_scores': scores,
            'recommendation': recommendation,
            'analysis_details': self._generate_analysis_details(domain_name, scores),
            'estimated_value': self._estimate_value(total_score, domain_data)
        }
    
    def _analyze_length(self, domain: str) -> float:
        """分析域名长度得分"""
        base_domain = domain.split('.')[0]
        length = len(base_domain)
        
        if 4 <= length <= 6:
            return 100
        elif 7 <= length <= 10:
            return 80
        elif 3 <= length <= 3 or 11 <= length <= 15:
            return 60
        elif 16 <= length <= 20:
            return 40
        else:
            return 20
    
    def _analyze_keywords(self, domain: str) -> float:
        """分析关键词价值"""
        base_domain = domain.split('.')[0].lower()
        score = 0
        
        # 检查高价值关键词
        for keyword in self.high_value_keywords:
            if keyword in base_domain:
                score += 20
        
        # 检查是否为完整单词
        words = re.findall(r'[a-zA-Z]+', base_domain)
        if len(words) >= 1:
            score += 10
        
        # 检查是否容易拼写
        if base_domain.isalpha():
            score += 15
        
        return min(score, 100)
    
    def _analyze_brandability(self, domain: str) -> float:
        """分析品牌价值"""
        base_domain = domain.split('.')[0].lower()
        score = 50  # 基础分
        
        # 易记性
        if len(base_domain) <= 8:
            score += 20
        
        # 无连字符和数字
        if base_domain.isalpha():
            score += 15
        
        # 发音简单
        vowels = 'aeiou'
        vowel_count = sum(1 for char in base_domain if char in vowels)
        if 0.2 <= vowel_count / len(base_domain) <= 0.5:
            score += 15
        
        return min(score, 100)
    
    def _analyze_seo_potential(self, domain_data: Dict) -> float:
        """分析SEO潜力"""
        score = 0
        
        # 域名年龄
        age = domain_data.get('age', 0)
        if age > 10:
            score += 30
        elif age > 5:
            score += 20
        elif age > 2:
            score += 10
        
        # 反向链接
        backlinks = domain_data.get('backlinks', 0)
        if backlinks > 1000:
            score += 25
        elif backlinks > 100:
            score += 15
        elif backlinks > 10:
            score += 10
        
        # TLD价值
        tld = '.' + domain_data.get('domain', '').split('.')[-1]
        if tld in self.premium_tlds:
            score += 25
        
        # 流量历史
        traffic = domain_data.get('traffic', 0)
        if traffic > 10000:
            score += 20
        elif traffic > 1000:
            score += 10
        
        return min(score, 100)
    
    def _analyze_technical_metrics(self, domain_data: Dict) -> float:
        """分析技术指标"""
        score = 50  # 基础分
        
        # DA/PA评分
        da = domain_data.get('domain_authority', 0)
        if da > 50:
            score += 30
        elif da > 30:
            score += 20
        elif da > 15:
            score += 10
        
        # 是否有历史内容
        if domain_data.get('wayback_snapshots', 0) > 0:
            score += 20
        
        return min(score, 100)
    
    def _analyze_commercial_value(self, domain: str) -> float:
        """分析商业价值"""
        base_domain = domain.split('.')[0].lower()
        
        commercial_keywords = [
            'shop', 'store', 'buy', 'sell', 'market', 'trade',
            'service', 'consulting', 'solution', 'platform'
        ]
        
        score = 0
        for keyword in commercial_keywords:
            if keyword in base_domain:
                score += 25
        
        return min(score, 100)
    
    def _generate_recommendation(self, total_score: float, scores: Dict) -> str:
        """生成推荐等级"""
        if total_score >= 80:
            return "🌟 强烈推荐 - 高价值域名"
        elif total_score >= 65:
            return "⭐ 推荐 - 有潜力的域名"
        elif total_score >= 50:
            return "👀 考虑 - 中等价值域名"
        elif total_score >= 35:
            return "⚠️ 谨慎 - 低价值域名"
        else:
            return "❌ 不推荐 - 价值很低"
    
    def _generate_analysis_details(self, domain: str, scores: Dict) -> List[str]:
        """生成详细分析说明"""
        details = []
        
        if scores['length_score'] >= 80:
            details.append("✓ 域名长度适中，易于记忆")
        elif scores['length_score'] < 50:
            details.append("⚠ 域名过长或过短")
        
        if scores['keyword_score'] >= 60:
            details.append("✓ 包含高价值关键词")
        
        if scores['brandability_score'] >= 70:
            details.append("✓ 品牌价值较高，适合商业用途")
        
        if scores['seo_score'] >= 60:
            details.append("✓ SEO潜力良好")
        elif scores['seo_score'] < 40:
            details.append("⚠ SEO价值较低")
        
        if scores['technical_score'] >= 70:
            details.append("✓ 技术指标优秀")
        
        return details
    
    def _estimate_value(self, total_score: float, domain_data: Dict) -> str:
        """估算域名价值"""
        base_value = total_score * 50  # 基础价值计算
        
        # 根据TLD调整
        tld = '.' + domain_data.get('domain', '').split('.')[-1]
        if tld == '.com':
            base_value *= 1.5
        elif tld in ['.net', '.org']:
            base_value *= 1.2
        elif tld in ['.io', '.ai']:
            base_value *= 1.3
        
        # 根据域名年龄调整
        age = domain_data.get('age', 0)
        if age > 10:
            base_value *= 1.3
        elif age > 5:
            base_value *= 1.1
        
        if base_value >= 5000:
            return f"${int(base_value):,}+ (高价值)"
        elif base_value >= 1000:
            return f"${int(base_value):,}+ (中高价值)"
        elif base_value >= 300:
            return f"${int(base_value):,}+ (中等价值)"
        else:
            return f"$100-{int(base_value)} (基础价值)"


class ExpiredDomainScanner:
    """过期域名扫描器主类"""
    
    def __init__(self, config_file: str = None):
        """
        初始化扫描器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.analyzer = DomainAnalyzer()
        self.session = requests.Session()
        self.driver = None
        
        # 设置日志
        self._setup_logging()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent()
        })
        
        self.logger.info("域名扫描器初始化完成")
    
    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        default_config = {
            'expired_domains': {
                'base_url': 'https://www.expireddomains.net',
                'login_url': 'https://www.expireddomains.net/login/',
                'search_url': 'https://www.expireddomains.net/domain-lists/',
                'username': os.getenv('EXPIRED_DOMAINS_USERNAME'),
                'password': os.getenv('EXPIRED_DOMAINS_PASSWORD')
            },
            'scanning': {
                'max_pages': 10,
                'delay_min': 2,
                'delay_max': 5,
                'retry_attempts': 3,
                'timeout': 30
            },
            'filters': {
                'min_domain_age': 1,
                'max_domain_length': 20,
                'min_backlinks': 5,
                'preferred_tlds': ['.com', '.net', '.org', '.io']
            },
            'output': {
                'results_dir': 'results',
                'html_output': True,
                'json_output': True,
                'csv_output': True
            }
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                # 合并配置
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        
        return default_config
    
    def _setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('domain_scanner.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)
    
    def _setup_webdriver(self) -> webdriver.Chrome:
        """设置Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={self._get_random_user_agent()}')
        
        # 在GitHub Actions环境中的特殊设置
        if os.getenv('GITHUB_ACTIONS'):
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(self.config['scanning']['timeout'])
        
        return driver
    
    def login_to_expired_domains(self) -> bool:
        """登录到ExpiredDomains.net"""
        username = self.config['expired_domains']['username']
        password = self.config['expired_domains']['password']
        
        if not username or not password:
            self.logger.error("未提供ExpiredDomains.net登录凭据")
            return False
        
        try:
            self.driver = self._setup_webdriver()
            self.driver.get(self.config['expired_domains']['login_url'])
            
            # 等待登录表单加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            
            # 输入登录信息
            username_field = self.driver.find_element(By.NAME, "login")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # 提交登录表单
            login_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
            login_button.click()
            
            # 等待登录完成
            time.sleep(3)
            
            # 检查是否登录成功
            if "logout" in self.driver.page_source.lower():
                self.logger.info("成功登录ExpiredDomains.net")
                return True
            else:
                self.logger.error("登录失败")
                return False
                
        except Exception as e:
            self.logger.error(f"登录过程中出错: {str(e)}")
            return False
    
    def scan_domains(self, max_pages: int = None) -> List[Dict]:
        """
        扫描过期域名
        
        Args:
            max_pages: 最大扫描页数
            
        Returns:
            域名数据列表
        """
        if max_pages is None:
            max_pages = self.config['scanning']['max_pages']
        
        self.logger.info(f"开始扫描过期域名，最大页数: {max_pages}")
        
        # 登录
        if not self.login_to_expired_domains():
            return []
        
        all_domains = []
        
        try:
            for page in range(1, max_pages + 1):
                self.logger.info(f"扫描第 {page} 页...")
                
                # 构建搜索URL
                search_url = f"{self.config['expired_domains']['search_url']}?start={(page-1)*25}"
                
                domains_on_page = self._scrape_page(search_url)
                if not domains_on_page:
                    self.logger.warning(f"第 {page} 页未获取到数据，停止扫描")
                    break
                
                all_domains.extend(domains_on_page)
                self.logger.info(f"第 {page} 页获取到 {len(domains_on_page)} 个域名")
                
                # 随机延迟
                delay = random.uniform(
                    self.config['scanning']['delay_min'],
                    self.config['scanning']['delay_max']
                )
                time.sleep(delay)
        
        except Exception as e:
            self.logger.error(f"扫描过程中出错: {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        self.logger.info(f"扫描完成，共获取 {len(all_domains)} 个域名")
        return all_domains
    
    def _scrape_page(self, url: str) -> List[Dict]:
        """抓取单页数据"""
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # 等待表格加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table = soup.find('table')
            
            if not table:
                return []
            
            domains = []
            rows = table.find_all('tr')[1:]  # 跳过表头
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 8:  # 确保有足够的列
                    try:
                        domain_data = {
                            'domain': cols[0].get_text(strip=True),
                            'age': self._parse_age(cols[2].get_text(strip=True)),
                            'backlinks': self._parse_number(cols[3].get_text(strip=True)),
                            'domain_authority': self._parse_number(cols[4].get_text(strip=True)),
                            'traffic': self._parse_number(cols[5].get_text(strip=True)),
                            'wayback_snapshots': self._parse_number(cols[6].get_text(strip=True)),
                            'auction_end': cols[7].get_text(strip=True),
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        # 应用过滤器
                        if self._apply_filters(domain_data):
                            domains.append(domain_data)
                            
                    except Exception as e:
                        self.logger.warning(f"解析域名数据时出错: {str(e)}")
                        continue
            
            return domains
            
        except TimeoutException:
            self.logger.error(f"页面加载超时: {url}")
            return []
        except Exception as e:
            self.logger.error(f"抓取页面时出错: {str(e)}")
            return []
    
    def _parse_age(self, age_str: str) -> int:
        """解析域名年龄"""
        try:
            # 从字符串中提取数字
            numbers = re.findall(r'\d+', age_str)
            if numbers:
                return int(numbers[0])
        except:
            pass
        return 0
    
    def _parse_number(self, num_str: str) -> int:
        """解析数字字符串"""
        try:
            # 移除逗号和其他非数字字符
            cleaned = re.sub(r'[^\d]', '', num_str)
            return int(cleaned) if cleaned else 0
        except:
            return 0
    
    def _apply_filters(self, domain_data: Dict) -> bool:
        """应用过滤条件"""
        filters = self.config['filters']
        
        # 域名年龄过滤
        if domain_data['age'] < filters['min_domain_age']:
            return False
        
        # 域名长度过滤
        domain_name = domain_data['domain'].split('.')[0]
        if len(domain_name) > filters['max_domain_length']:
            return False
        
        # 反向链接过滤
        if domain_data['backlinks'] < filters['min_backlinks']:
            return False
        
        # TLD过滤
        tld = '.' + domain_data['domain'].split('.')[-1]
        if filters['preferred_tlds'] and tld not in filters['preferred_tlds']:
            return False
        
        return True
    
    def analyze_domains(self, domains: List[Dict]) -> List[Dict]:
        """批量分析域名"""
        self.logger.info(f"开始分析 {len(domains)} 个域名...")
        
        analyzed_domains = []
        for i, domain_data in enumerate(domains):
            try:
                analysis = self.analyzer.analyze_domain_value(domain_data)
                analyzed_domains.append(analysis)
                
                if (i + 1) % 50 == 0:
                    self.logger.info(f"已分析 {i + 1}/{len(domains)} 个域名")
                    
            except Exception as e:
                self.logger.error(f"分析域名 {domain_data.get('domain', 'unknown')} 时出错: {str(e)}")
        
        # 按总分排序
        analyzed_domains.sort(key=lambda x: x['total_score'], reverse=True)
        
        self.logger.info("域名分析完成")
        return analyzed_domains
    
    def save_results(self, analyzed_domains: List[Dict]) -> Dict[str, str]:
        """保存分析结果"""
        os.makedirs(self.config['output']['results_dir'], exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        files_created = {}
        
        # 保存JSON
        if self.config['output']['json_output']:
            json_file = os.path.join(
                self.config['output']['results_dir'],
                f'domain_analysis_{timestamp}.json'
            )
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(analyzed_domains, f, ensure_ascii=False, indent=2)
            files_created['json'] = json_file
        
        # 保存CSV
        if self.config['output']['csv_output']:
            csv_file = os.path.join(
                self.config['output']['results_dir'],
                f'domain_analysis_{timestamp}.csv'
            )
            df = pd.DataFrame(analyzed_domains)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            files_created['csv'] = csv_file
        
        # 生成HTML报告
        if self.config['output']['html_output']:
            html_file = os.path.join(
                self.config['output']['results_dir'],
                'domain_analysis.html'
            )
            self._generate_html_report(analyzed_domains, html_file)
            files_created['html'] = html_file
        
        return files_created
    
    def _generate_html_report(self, analyzed_domains: List[Dict], output_file: str):
        """生成HTML报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>过期域名分析报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        .summary {{ background: #3498db; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .domain-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: #fff; }}
        .domain-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .score {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; }}
        .high-score {{ color: #27ae60; }}
        .medium-score {{ color: #f39c12; }}
        .low-score {{ color: #e74c3c; }}
        .recommendation {{ font-size: 18px; margin-bottom: 15px; padding: 10px; border-radius: 5px; }}
        .details {{ margin-top: 15px; }}
        .detail-item {{ margin: 5px 0; padding: 5px; background: #f8f9fa; border-radius: 3px; }}
        .value-estimate {{ font-size: 16px; font-weight: bold; color: #27ae60; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .filter-controls {{ margin-bottom: 20px; }}
        .filter-controls input, .filter-controls select {{ margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 过期域名AI分析报告</h1>
        
        <div class="summary">
            <h2>📊 扫描摘要</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(analyzed_domains)}</div>
                    <div class="stat-label">总域名数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([d for d in analyzed_domains if d['total_score'] >= 80])}</div>
                    <div class="stat-label">高价值域名</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([d for d in analyzed_domains if d['total_score'] >= 65])}</div>
                    <div class="stat-label">推荐域名</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                    <div class="stat-label">扫描时间</div>
                </div>
            </div>
        </div>
        
        <div class="filter-controls">
            <input type="text" id="domainFilter" placeholder="搜索域名..." onkeyup="filterDomains()">
            <select

#!/usr/bin/env python3
"""
ArXiv Paper Fetcher
自动爬取 arxiv 论文并生成 Markdown 报告
"""

import os
import sys
import re
import yaml
import arxiv
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from arxiv import HTTPError

# ArXiv 分类名称映射 - 完整的计算机科学分类
CATEGORY_NAMES = {
    # AI & Machine Learning
    'cs.AI': 'Artificial Intelligence',
    'cs.CL': 'Computation and Language',
    'cs.CV': 'Computer Vision and Pattern Recognition',
    'cs.LG': 'Machine Learning',
    'cs.NE': 'Neural and Evolutionary Computing',
    
    # Architecture & Systems
    'cs.AR': 'Architecture',
    'cs.DC': 'Distributed, Parallel, and Cluster Computing',
    'cs.NI': 'Networking and Internet Architecture',
    'cs.OS': 'Operating Systems',
    'cs.PF': 'Performance',
    'cs.DS': 'Data Structures and Algorithms',
    
    # Software Engineering & Languages
    'cs.SE': 'Software Engineering',
    'cs.PL': 'Programming Languages',
    'cs.FL': 'Formal Languages and Automata Theory',
    'cs.LO': 'Logic in Computer Science',
    
    # Security & Cryptography
    'cs.CR': 'Cryptography and Security',
    
    # Databases & Information
    'cs.DB': 'Databases',
    'cs.IR': 'Information Retrieval',
    'cs.DL': 'Digital Libraries',
    'cs.SI': 'Social and Information Networks',
    
    # Graphics & Multimedia
    'cs.GR': 'Graphics',
    'cs.MM': 'Multimedia',
    'cs.HC': 'Human-Computer Interaction',
    
    # Theory & Math
    'cs.CC': 'Computational Complexity',
    'cs.CY': 'Computers and Society',
    'cs.DM': 'Discrete Mathematics',
    'cs.GT': 'Computer Science and Game Theory',
    'cs.IT': 'Information Theory',
    'cs.SC': 'Symbolic Computation',
    'cs.NA': 'Numerical Analysis',
    
    # Robotics & Applications
    'cs.RO': 'Robotics',
    'cs.MS': 'Mathematical Software',
    
    # Other
    'cs.GL': 'General Literature',
    'cs.ET': 'Emerging Technologies',
    'cs.MA': 'Multiagent Systems',
    'cs.OH': 'Other Computer Science',
    'cs.SD': 'Sound',
    'cs.SY': 'Systems and Control',
}


def load_config(config_path):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_existing_papers(docs_dir):
    """从 docs 文件夹中提取已爬取的论文 ID"""
    existing_ids = set()
    
    import re
    pattern = r'arxiv\.org/abs/(\d+\.\d+)'
    
    # 遍历 docs 文件夹中的所有 .md 文件
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.findall(pattern, content)
                        existing_ids.update(matches)
                except Exception as e:
                    print(f"警告: 读取文件 {file_path} 时出错: {e}")
    
    return existing_ids


def filter_by_keywords(paper, keywords):
    """根据关键词过滤论文"""
    if not keywords:
        return True
    
    title_lower = paper.title.lower()
    summary_lower = paper.summary.lower()
    
    for keyword in keywords:
        if keyword.lower() in title_lower or keyword.lower() in summary_lower:
            return True
    
    return False


def escape_html_in_md(text):
    """Escape HTML special characters in markdown text to prevent Vue/VitePress parsing errors.
    
    In VitePress, markdown files are processed by Vue's template compiler, which treats
    <...> as HTML tags. Angle brackets in paper titles/abstracts (e.g., Trust<T>, <SOG_k>)
    cause 'Element is missing end tag' build errors.
    """
    text = text.replace('<', '\\<')
    text = text.replace('>', '\\>')
    return text


def truncate_summary(summary, max_length):
    """截断摘要到指定长度"""
    if len(summary) <= max_length:
        return summary
    
    # 在最近的一个句子末尾截断
    truncated = summary[:max_length]
    last_period = truncated.rfind('.')
    
    if last_period > max_length * 0.7:  # 如果句号在合理位置
        return truncated[:last_period + 1]
    else:
        return truncated[:max_length] + '...'


# ArXiv API 使用条款: 每次请求之间至少间隔 3 秒，限制为单个连接
# https://info.arxiv.org/help/api/tou.html
# 实际使用 10 秒间隔以进一步降低请求压力，避免触发 429
ARXIV_API_DELAY = 10.0      # 请求间隔（秒），保守策略降低请求压力
ARXIV_MAX_RETRIES = 5       # 429 错误最大重试次数
ARXIV_RETRY_BACKOFF = 30.0  # 429 错误初始退避时间（秒），每次翻倍


def fetch_papers_by_category(client, category, start_date, end_date, max_results, keywords):
    """获取指定分类的论文，返回 (论文列表, 最新论文的提交时间)
    
    使用共享的 arxiv.Client 实例以确保全局速率限制。
    内含 429 错误的指数退避重试机制。
    """
    print(f"正在爬取分类: {category}")
    
    # 构建搜索查询
    query = f"cat:{category}"
    
    # 添加日期范围 - 使用 YYYYMMDD 格式（ArXiv API 标准格式）
    # 结束日期加一天以确保包含当天的所有论文
    end_date_plus_one = end_date + timedelta(days=1)
    date_query = f"submittedDate:[{start_date.strftime('%Y%m%d')} TO {end_date_plus_one.strftime('%Y%m%d')}]"
    
    search = arxiv.Search(
        query=f"{query} AND {date_query}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    latest_published = None
    
    # 带有指数退避的重试机制，专门处理 429 (Too Many Requests) 错误
    retry_delay = ARXIV_RETRY_BACKOFF
    for attempt in range(ARXIV_MAX_RETRIES):
        try:
            for result in client.results(search):
                # 关键词过滤
                if filter_by_keywords(result, keywords):
                    papers.append(result)
                    # 跟踪最新论文的提交时间（因为按降序排序，第一个就是最新的）
                    if latest_published is None or result.published > latest_published:
                        latest_published = result.published
            # 成功完成，跳出重试循环
            break
        except HTTPError as e:
            if e.status == 429:
                if attempt < ARXIV_MAX_RETRIES - 1:
                    print(f"  警告: 收到 429 (请求过多)，第 {attempt + 1}/{ARXIV_MAX_RETRIES} 次重试，"
                          f"等待 {retry_delay:.0f} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"  错误: 爬取 {category} 时多次收到 429，已达到最大重试次数，跳过此分类")
            else:
                print(f"  警告: 爬取 {category} 时出错: HTTP {e.status} - {e}")
                break
        except Exception as e:
            print(f"  警告: 爬取 {category} 时出错: {e}")
            break
    
    print(f"  找到 {len(papers)} 篇论文")
    return papers, latest_published


def generate_markdown(papers_by_category, config, existing_ids=None, last_update=None):
    """生成 Markdown 内容 - 按日期分组"""
    if existing_ids is None:
        existing_ids = set()
    
    include_summary = config['output']['include_summary']
    summary_max_length = config['output']['summary_max_length']
    cat_heading = '#' * config['markdown']['category_heading_level']
    
    # 按日期分组论文
    papers_by_date = {}
    total_new = 0
    
    for category, papers in papers_by_category.items():
        if not papers:
            continue
        
        # 过滤已存在的论文
        new_papers = [p for p in papers if p.get_short_id() not in existing_ids]
        
        if not new_papers:
            continue
        
        total_new += len(new_papers)
        
        for paper in new_papers:
            date = paper.published.strftime('%Y-%m-%d')
            if date not in papers_by_date:
                papers_by_date[date] = {}
            if category not in papers_by_date[date]:
                papers_by_date[date][category] = []
            papers_by_date[date][category].append(paper)
    
    return papers_by_date, total_new


def get_template_path(output_file):
    """获取模板文件路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    template_path = os.path.join(project_root, 'README_TEMPLATE.md')
    return template_path


def create_month_index(month_dir):
    """为月份目录创建索引文件"""
    # 读取该目录下的所有日期文件
    date_files = []
    for filename in sorted(os.listdir(month_dir)):
        if filename.endswith('.md') and filename != 'index.md':
            # 只取日期部分，去掉 .md
            date_part = filename[:-3]
            date_files.append(date_part)
    
    if not date_files:
        return False
    
    # 生成索引内容
    lines = []
    month_name = os.path.basename(month_dir)
    lines.append(f"# {month_name}\n")
    lines.append(f"\n")
    lines.append("## 日期列表\n")
    lines.append("\n")
    
    # 按日期倒序排列
    for date in sorted(date_files, reverse=True):
        lines.append(f"- [{date}](./{date})\n")
    
    # 写入索引文件
    index_path = os.path.join(month_dir, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return True


def update_markdown_files_by_date(papers_by_date, config):
    """按日期生成多个 Markdown 文件到 docs 文件夹"""
    docs_dir = config['output']['dir']
    include_summary = config['output']['include_summary']
    summary_max_length = config['output']['summary_max_length']
    cat_heading = '#' * config['markdown']['category_heading_level']
    
    # 确保 docs 目录存在
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    total_files_created = 0
    total_papers = 0
    month_dirs = set()
    
    # 按日期生成文件
    for date in sorted(papers_by_date.keys(), reverse=True):
        date_str = date
        papers_by_category = papers_by_date[date]
        
        # 格式化日期为文件名友好格式
        date_parts = date_str.split('-')
        year_month = f"{date_parts[0]}-{date_parts[1]}"
        
        # 创建年月目录
        year_month_dir = os.path.join(docs_dir, year_month)
        month_dirs.add(year_month_dir)
        if not os.path.exists(year_month_dir):
            os.makedirs(year_month_dir)
        
        # 生成文件内容
        lines = []
        lines.append(f"# {date_str}\n")
        lines.append(f"\n")
        
        # 按分类添加论文
        for category in sorted(papers_by_category.keys()):
            papers = papers_by_category[category]
            if not papers:
                continue
            
            total_papers += len(papers)
            
            # 分类标题
            category_name = CATEGORY_NAMES.get(category, category)
            lines.append(f"{cat_heading} {category} - {category_name}\n")
            lines.append("")
            
            # 创建表格
            if include_summary:
                lines.append("| 标题 | 作者 | 发布日期 | PDF | 摘要 |")
                lines.append("|------|------|----------|-----|------|")
                for paper in papers:
                    title = escape_html_in_md(paper.title)
                    title_link = f"[{title}](https://arxiv.org/abs/{paper.get_short_id()})"
                    authors = ', '.join([str(author) for author in paper.authors])
                    published_date = paper.published.strftime('%Y-%m-%d')
                    pdf_link = f"[下载](https://arxiv.org/pdf/{paper.get_short_id()}.pdf)"
                    summary = truncate_summary(escape_html_in_md(paper.summary.replace('\n', ' ').replace('|', '\\|').replace('\r', '')), summary_max_length)
                    lines.append(f"| {title_link} | {authors} | {published_date} | {pdf_link} | {summary} |")
            else:
                lines.append("| 标题 | 作者 | 发布日期 | PDF |")
                lines.append("|------|------|----------|-----|")
                for paper in papers:
                    title = escape_html_in_md(paper.title)
                    title_link = f"[{title}](https://arxiv.org/abs/{paper.get_short_id()})"
                    authors = ', '.join([str(author) for author in paper.authors])
                    published_date = paper.published.strftime('%Y-%m-%d')
                    pdf_link = f"[下载](https://arxiv.org/pdf/{paper.get_short_id()}.pdf)"
                    lines.append(f"| {title_link} | {authors} | {published_date} | {pdf_link} |")
            
            lines.append("")
        
        # 写入文件
        file_path = os.path.join(year_month_dir, f"{date_str}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        total_files_created += 1
        print(f"  创建文件: {file_path} ({len(papers_by_category)} 个分类)")
    
    # 为每个月创建索引文件
    for month_dir in month_dirs:
        if create_month_index(month_dir):
            print(f"  创建索引文件: {os.path.join(month_dir, 'index.md')}")
    
    return total_files_created, total_papers


def get_state_file_path(docs_dir):
    """获取状态文件路径"""
    return os.path.join(docs_dir, '.state')


def load_state(state_file):
    """加载状态文件"""
    if not os.path.exists(state_file):
        return None
    
    try:
        with open(state_file, 'r') as f:
            return yaml.safe_load(f)
    except:
        return None


def save_state(state_file, latest_paper_date):
    """保存状态文件 - 保存最新论文的日期（天级别）"""
    # ArXiv API 只支持天级别查询，所以保存论文的日期
    # 重复论文通过论文 ID 去重来避免
    paper_date = latest_paper_date.strftime('%Y-%m-%d')
    with open(state_file, 'w') as f:
        yaml.dump({'last_run_date': paper_date}, f)


def save_last_update_time(update_time):
    """保存最后更新时间到 docs 目录"""
    # 获取 docs 目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, '..', 'docs')
    update_file = os.path.join(docs_dir, 'last_update.yml')
    
    # 确保 docs 目录存在
    os.makedirs(docs_dir, exist_ok=True)
    
    # 保存更新时间
    with open(update_file, 'w', encoding='utf-8') as f:
        f.write(f"last_update: {update_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        f.write(f"last_update_date: {update_time.strftime('%Y-%m-%d')}\n")
        f.write(f"last_update_time: {update_time.strftime('%H:%M')}\n")


def main():
    # 获取配置文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'config', 'arxiv_config.yaml')
    
    # 加载配置
    config = load_config(config_path)
    
    # 输出目录
    docs_dir = config['output']['dir']
    state_file = get_state_file_path(docs_dir)
    
    # 加载状态
    state = load_state(state_file)
    
    # 获取现有论文 ID
    existing_ids = get_existing_papers(docs_dir)
    print(f"已存在 {len(existing_ids)} 篇论文")
    
    # 确定日期范围（使用 UTC 时间）
    if state is None:
        # 首次运行：从配置的起始日期到现在（添加 UTC 时区）
        start_date = datetime.strptime(config['start_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        print(f"首次运行，从 {start_date.strftime('%Y-%m-%d')} 开始爬取")
    else:
        # 后续运行：从保存的日期开始（添加 UTC 时区）
        # 保存的是最新论文的日期，所以从该日期的 00:00:00 开始
        last_paper_date_str = state['last_run_date']
        start_date = datetime.strptime(last_paper_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        print(f"从最新论文日期 {start_date.strftime('%Y-%m-%d UTC')} 开始爬取")
    
    end_date = datetime.now(timezone.utc)
    
    # 确保日期范围合理
    if start_date > end_date:
        print("日期范围无效，退出")
        return
    
    # 创建共享的 arXiv API 客户端
    # ArXiv API 使用条款: 每次请求之间至少间隔 3 秒，限制为单个连接
    # 使用单个 Client 实例确保全局遵守速率限制，实际间隔 10 秒以降低请求压力
    client = arxiv.Client(
        page_size=100,           # 每页结果数
        delay_seconds=ARXIV_API_DELAY,  # 请求间隔 10 秒，保守策略
        num_retries=ARXIV_MAX_RETRIES   # 重试次数
    )
    
    # 获取论文
    papers_by_category = {}
    max_results = config['output']['max_papers_per_category']
    keywords = config['keywords']
    latest_paper_date = None
    
    for i, category in enumerate(config['categories']):
        papers, category_latest = fetch_papers_by_category(
            client, category, start_date, end_date, max_results, keywords
        )
        papers_by_category[category] = papers
        
        # 跟踪所有分类中最新的论文时间
        if category_latest is not None:
            if latest_paper_date is None or category_latest > latest_paper_date:
                latest_paper_date = category_latest
        
        # 分类之间额外等待，确保不超过 API 速率限制
        # Client 内部已处理分页请求的间隔，这里额外等待是分类切换的安全缓冲
        # 最后一个分类不需要等待
        if i < len(config['categories']) - 1:
            print(f"  等待 {ARXIV_API_DELAY:.0f} 秒以遵守 API 使用条款...")
            time.sleep(ARXIV_API_DELAY)
    
    # 生成 Markdown（按日期分组）
    papers_by_date, new_count = generate_markdown(
        papers_by_category, config, existing_ids
    )
    
    # 更新文件（按日期生成多个文件）
    if new_count > 0:
        files_created, total_papers = update_markdown_files_by_date(papers_by_date, config)
        print(f"✓ 成功创建 {files_created} 个文件，包含 {total_papers} 篇新论文到 {docs_dir}")
    else:
        print("✓ 没有新论文需要添加")
    
    # 保存状态 - 保存最新论文的提交日期
    # 如果有新论文，使用最新论文的日期；否则保持状态不变
    if latest_paper_date is not None:
        state_date = latest_paper_date
        print(f"保存最新论文日期: {state_date.strftime('%Y-%m-%d')}")
        save_state(state_file, state_date)
    else:
        # 如果没有新论文，保持状态不变
        print(f"没有新论文，保持状态不变: {state['last_run_date'] if state else 'N/A'}")
    
    # 保存最后更新时间到 docs 目录
    save_last_update_time(end_date)
    
    print(f"\n完成！共爬取 {new_count} 篇新论文")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
ArXiv Paper Fetcher
自动爬取 arxiv 论文并生成 Markdown 报告
"""

import os
import sys
import yaml
import arxiv
from datetime import datetime, timedelta
from pathlib import Path


def load_config(config_path):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_existing_papers(markdown_file):
    """从现有 Markdown 文件中提取已爬取的论文 ID"""
    existing_ids = set()
    
    if not os.path.exists(markdown_file):
        return existing_ids
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 从 arxiv 链接中提取论文 ID (格式: arxiv.org/abs/2301.12345)
        import re
        pattern = r'arxiv\.org/abs/(\d+\.\d+)'
        matches = re.findall(pattern, content)
        existing_ids.update(matches)
    
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


def fetch_papers_by_category(category, start_date, end_date, max_results, keywords):
    """获取指定分类的论文"""
    print(f"正在爬取分类: {category}")
    
    # 构建搜索查询
    query = f"cat:{category}"
    
    # 添加日期范围
    date_query = f"submittedDate:[{start_date.strftime('%Y%m%d%H%M%S')} TO {end_date.strftime('%Y%m%d%H%M%S')}]"
    
    search = arxiv.Search(
        query=f"{query} AND {date_query}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    client = arxiv.Client()
    
    try:
        for result in client.results(search):
            # 关键词过滤
            if filter_by_keywords(result, keywords):
                papers.append(result)
    except Exception as e:
        print(f"  警告: 爬取 {category} 时出错: {e}")
    
    print(f"  找到 {len(papers)} 篇论文")
    return papers


def generate_markdown(papers_by_category, config, existing_ids=None, last_update=None):
    """生成 Markdown 内容"""
    if existing_ids is None:
        existing_ids = set()
    
    output_file = config['output']['file']
    include_summary = config['output']['include_summary']
    summary_max_length = config['output']['summary_max_length']
    
    cat_heading = '#' * config['markdown']['category_heading_level']
    paper_heading = '#' * config['markdown']['paper_heading_level']
    
    # Markdown 头部
    lines = [
        f"# {config['markdown']['title']}\n",
        f"{config['markdown']['description']}\n",
        f"**最后更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n"
    ]
    
    # 统计信息
    total_new = 0
    
    # 按分类生成内容
    for category, papers in papers_by_category.items():
        if not papers:
            continue
        
        # 过滤已存在的论文
        new_papers = [p for p in papers if p.get_short_id() not in existing_ids]
        
        if not new_papers:
            continue
        
        total_new += len(new_papers)
        
        # 分类标题
        lines.append(f"{cat_heading} {category} - {arxiv.Category(category).name}\n")
        lines.append("")
        
        # 论文条目
        for paper in new_papers:
            # 论文标题
            lines.append(f"{paper_heading} [{paper.title}](https://arxiv.org/abs/{paper.get_short_id()})")
            lines.append("")
            
            # 作者
            authors = ', '.join([str(author) for author in paper.authors])
            lines.append(f"- **作者**: {authors}")
            
            # 发布日期
            published_date = paper.published.strftime('%Y-%m-%d')
            lines.append(f"- **发布日期**: {published_date}")
            
            # PDF 链接
            lines.append(f"- **PDF**: [下载链接](https://arxiv.org/pdf/{paper.get_short_id()}.pdf)")
            
            # 摘要（如果启用）
            if include_summary:
                summary = truncate_summary(paper.summary.replace('\n', ' '), summary_max_length)
                lines.append(f"- **摘要**: {summary}")
            
            lines.append("")
            lines.append("---")
            lines.append("")
    
    return '\n'.join(lines), total_new


def update_markdown_file(new_content, output_file):
    """更新 Markdown 文件"""
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 如果文件存在，保留之前的所有内容，在开头添加新内容
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # 分离头部和内容
        lines = existing_content.split('\n')
        header_lines = []
        content_lines = []
        in_header = True
        
        for line in lines:
            if in_header:
                header_lines.append(line)
                if line.strip() == '---':
                    in_header = False
                    header_lines.append('')
            else:
                content_lines.append(line)
        
        # 合并：新内容在头部之后
        final_content = '\n'.join(header_lines) + '\n' + new_content.split('---', 2)[-1].strip() + '\n'
    else:
        final_content = new_content
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)


def get_state_file_path(output_file):
    """获取状态文件路径"""
    state_file = output_file.replace('.md', '.state')
    return state_file


def load_state(state_file):
    """加载状态文件"""
    if not os.path.exists(state_file):
        return None
    
    try:
        with open(state_file, 'r') as f:
            return yaml.safe_load(f)
    except:
        return None


def save_state(state_file, last_run_date):
    """保存状态文件"""
    with open(state_file, 'w') as f:
        yaml.dump({'last_run_date': last_run_date.strftime('%Y-%m-%d')}, f)


def main():
    # 获取配置文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'config', 'arxiv_config.yaml')
    
    # 加载配置
    config = load_config(config_path)
    
    # 输出文件路径
    output_file = config['output']['file']
    state_file = get_state_file_path(output_file)
    
    # 加载状态
    state = load_state(state_file)
    
    # 获取现有论文 ID
    existing_ids = get_existing_papers(output_file)
    print(f"已存在 {len(existing_ids)} 篇论文")
    
    # 确定日期范围
    if state is None:
        # 首次运行：从配置的起始日期到现在
        start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
        print(f"首次运行，从 {start_date.strftime('%Y-%m-%d')} 开始爬取")
    else:
        # 后续运行：从上次运行到现在
        start_date = datetime.strptime(state['last_run_date'], '%Y-%m-%d')
        start_date = start_date + timedelta(days=1)  # 从下一天开始
        print(f"从上次运行日期 {start_date.strftime('%Y-%m-%d')} 开始爬取")
    
    end_date = datetime.now()
    
    # 确保日期范围合理
    if start_date > end_date:
        print("日期范围无效，退出")
        return
    
    # 获取论文
    papers_by_category = {}
    max_results = config['output']['max_papers_per_category']
    keywords = config['keywords']
    
    for category in config['categories']:
        papers = fetch_papers_by_category(
            category, start_date, end_date, max_results, keywords
        )
        papers_by_category[category] = papers
    
    # 生成 Markdown
    markdown_content, new_count = generate_markdown(
        papers_by_category, config, existing_ids
    )
    
    # 更新文件
    if new_count > 0:
        update_markdown_file(markdown_content, output_file)
        print(f"✓ 成功添加 {new_count} 篇新论文到 {output_file}")
    else:
        print("✓ 没有新论文需要添加")
    
    # 保存状态
    save_state(state_file, end_date)
    
    print(f"\n完成！共爬取 {new_count} 篇新论文")


if __name__ == '__main__':
    main()
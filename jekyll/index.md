---
title: ArXiv Daily Papers
layout: home
---

# 📚 ArXiv Daily Papers

欢迎使用 ArXiv Daily Papers！这是一个自动爬取和整理 arXiv 论文的网站，按日期和分类组织。

## 🎯 功能特性

- **自动爬取**：每天自动从 arXiv 爬取最新论文
- **分类整理**：按照计算机科学不同分类整理
- **日期归档**：按日期归档，方便查找历史论文
- **详细摘要**：每篇论文包含标题、作者、摘要和PDF链接

## 📂 浏览方式

### 按日期浏览

使用左侧边栏导航，选择年份和月份查看对应日期的论文。

### 论文分类

当前包含以下分类：

- **cs.AR** - Architecture (计算机体系结构)
- **cs.DC** - Distributed, Parallel, and Cluster Computing (分布式、并行和集群计算)
- **cs.NI** - Networking and Internet Architecture (网络和互联网架构)
- **cs.OS** - Operating Systems (操作系统)
- **cs.DB** - Databases (数据库)
- **cs.PF** - Performance (性能)

## 🔧 技术栈

- **GitHub Actions**：自动化爬取和部署
- **GitHub Pages**：静态网站托管
- **Jekyll**：静态站点生成器
- **Python + arxiv API**：论文爬取

## 📖 使用说明

1. 点击左侧边栏的年份和月份
2. 选择具体日期查看当天发布的论文
3. 点击论文标题查看详细信息
4. 点击"下载"按钮获取PDF文件

## 🤝 贡献

本项目由 [GitHub Actions](https://github.com/features/actions) 自动维护，每天自动更新。

---

*最后更新：{% if site.data.last_update %}{{ site.data.last_update.last_update }}{% else %}{{ site.time | date: "%Y-%m-%d %H:%M" }}{% endif %}*

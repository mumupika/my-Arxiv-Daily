# ArXiv Daily Papers Crawler 📚

自动爬取 ArXiv 论文并生成 Markdown 报告的 GitHub Actions 工具。

## ✨ 功能特性

- 🤖 **自动化爬取**：使用 GitHub Actions 定时自动爬取 ArXiv 论文
- 📊 **多分类支持**：支持配置多个 ArXiv 分类（如 cs.AR, cs.DC 等）
- 🔍 **关键词过滤**：可根据关键词过滤论文
- 📝 **Markdown 输出**：生成格式良好的 Markdown 报告
- 🔄 **增量更新**：只爬取新增论文，避免重复
- ⚙️ **灵活配置**：通过 YAML 配置文件轻松自定义

## 📦 项目结构

```
arxiv/
├── .github/
│   └── workflows/
│       └── arxiv-daily.yml          # GitHub Actions 工作流
├── config/
│   └── arxiv_config.yaml            # 配置文件
├── scripts/
│   └── fetch_arxiv.py                # 主爬取脚本
├── output/
│   └── arxiv_papers.md               # 生成的 Markdown 文件
├── requirements.txt                  # Python 依赖
├── README.md                        # 项目说明
└── .gitignore
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/arxiv.git
cd arxiv
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置爬取参数

编辑 `config/arxiv_config.yaml` 文件：

```yaml
# 配置要爬取的 ArXiv 分类
categories:
  - cs.AR      # Computer Science - Architecture
  - cs.DC      # Computer Science - Distributed, Parallel, and Cluster Computing
  - cs.NI      # Computer Science - Networking and Internet Architecture
  - cs.OS      # Computer Science - Operating Systems

# 关键词过滤（可选）
keywords:
  - machine learning
  - deep learning
  - neural network

# 首次爬取的起始日期
start_date: "2025-01-01"
```

### 4. 本地测试运行

```bash
python scripts/fetch_arxiv.py
```

生成的 Markdown 文件将保存在 `output/arxiv_papers.md`。

### 5. 推送到 GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

## ⚙️ 配置说明

### 分类配置

在 `config/arxiv_config.yaml` 中配置要爬取的 ArXiv 分类：

```yaml
categories:
  - cs.AR      # 架构
  - cs.DC      # 分布式计算
  - cs.NI      # 网络与互联网架构
  - cs.OS      # 操作系统
  # 添加更多分类...
```

更多分类请参考：[ArXiv 分类列表](https://arxiv.org/category_taxonomy)

### 关键词过滤

设置关键词过滤，只包含标题或摘要中包含这些关键词的论文：

```yaml
keywords:
  - machine learning
  - deep learning
  - AI
```

如果不想过滤关键词，设置为空列表：

```yaml
keywords: []
```

### 输出配置

```yaml
output:
  file: "output/arxiv_papers.md"           # 输出文件路径
  max_papers_per_category: 100             # 每个分类最大论文数
  include_summary: true                    # 是否包含摘要
  summary_max_length: 200                  # 摘要最大长度
```

### Markdown 格式配置

```yaml
markdown:
  title: "ArXiv Daily Papers"              # 标题
  description: "自动爬取的 arxiv 论文汇总"   # 描述
  category_heading_level: 2                 # 分类标题级别
  paper_heading_level: 3                   # 论文标题级别
```

## 🔄 GitHub Actions 自动化

### 定时执行

工作流配置为每天 UTC 时间 00:00（北京时间 08:00）自动执行：

```yaml
schedule:
  - cron: '0 0 * * *'
```

### 手动触发

你也可以手动触发工作流：

1. 进入 GitHub 仓库的 **Actions** 标签页
2. 选择 **ArXiv Daily Crawler** 工作流
3. 点击 **Run workflow** 按钮

### 首次部署

首次推送到 GitHub 后：

1. 进入 **Actions** 标签页
2. 手动触发工作流一次（首次运行会从 `start_date` 爬取到现在的所有论文）
3. 之后每天自动增量更新

## 📄 输出格式示例

生成的 Markdown 文件格式如下：

```markdown
# ArXiv Daily Papers

自动爬取的 arxiv 论文汇总

**最后更新时间**: 2026-03-06 12:00:00

---

## cs.AR - Computer Science - Architecture

### [A Novel Architecture for Deep Learning](https://arxiv.org/abs/2301.12345)

- **作者**: John Doe, Jane Smith, Bob Johnson
- **发布日期**: 2026-03-05
- **PDF**: [下载链接](https://arxiv.org/pdf/2301.12345.pdf)
- **摘要**: This paper presents a novel architecture for deep learning applications...

---

## cs.DC - Computer Science - Distributed, Parallel, and Cluster Computing

### [Scalable Distributed Systems](https://arxiv.org/abs/2301.67890)

- **作者**: Alice Wang, Charlie Brown
- **发布日期**: 2026-03-04
- **PDF**: [下载链接](https://arxiv.org/pdf/2301.67890.pdf)
- **摘要**: We propose a new approach to building scalable distributed systems...

---
```

## 🔧 高级用法

### 修改定时执行时间

编辑 `.github/workflows/arxiv-daily.yml` 中的 cron 表达式：

```yaml
schedule:
  # 每 12 小时执行一次
  - cron: '0 */12 * * *'
  
  # 或每天北京时间 20:00 执行
  - cron: '0 12 * * *'
```

Cron 表达式格式：`分 时 日 月 周`

### 本地定时执行

使用 cron 或系统调度工具定时执行脚本：

```bash
# 添加到 crontab（每小时执行）
0 * * * * cd /path/to/arxiv && python scripts/fetch_arxiv.py
```

### 自定义分类映射

在 Python 脚本中可以添加自定义的分类映射和名称。

## 🐛 故障排除

### 没有生成新论文

1. 检查配置的日期范围是否正确
2. 查看 GitHub Actions 运行日志
3. 确认关键词过滤是否过于严格

### GitHub Actions 失败

1. 检查 `requirements.txt` 中的依赖是否正确
2. 查看 Actions 的详细错误日志
3. 确认 Python 版本兼容性

### 本地运行报错

1. 确认已安装所有依赖：`pip install -r requirements.txt`
2. 检查配置文件路径是否正确
3. 查看错误信息并进行相应调整

## 📝 开发计划

- [ ] 支持多种输出格式（HTML, JSON）
- [ ] 添加论文统计和可视化
- [ ] 支持邮件通知
- [ ] 添加更多过滤选项（作者、机构等）
- [ ] 支持自定义模板

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [ArXiv](https://arxiv.org/) - 开放访问论文库
- [arxiv Python 库](https://github.com/lukasschwab/arxiv.py) - ArXiv API 客户端

---

Made with ❤️ by [Your Name]
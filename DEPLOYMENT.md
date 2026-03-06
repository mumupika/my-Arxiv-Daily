# 部署指南 🚀

本文档详细介绍如何将 ArXiv Paper Crawler 部署到 GitHub 并开始使用。

## 前置要求

- GitHub 账户
- Git 基础知识
- 本地 Python 3.9+ 环境（可选，用于本地测试）

## 部署步骤

### 1. 创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角的 `+` 按钮，选择 `New repository`
3. 填写仓库名称（例如：`arxiv-papers`）
4. 选择 Public 或 Private（推荐 Public，方便访问生成的 Markdown 文件）
5. 勾选 `Add a README file`（可选）
6. 点击 `Create repository`

### 2. 上传项目文件

#### 方法 A：使用 GitHub Web 界面

1. 在新创建的仓库中，点击 `Add file` -> `Upload files`
2. 将以下文件拖拽到上传区域：
   - `.github/workflows/arxiv-daily.yml`
   - `.gitignore`
   - `config/arxiv_config.yaml`
   - `scripts/fetch_arxiv.py`
   - `requirements.txt`
   - `README.md`
3. 填写提交信息：`Initial commit: Add arxiv paper crawler`
4. 点击 `Commit changes`

#### 方法 B：使用 Git 命令行（推荐）

```bash
# 初始化本地仓库
cd /path/to/your/project
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Add arxiv paper crawler"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/your-username/arxiv-papers.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 3. 配置 GitHub Actions

GitHub Actions 会在你推送代码后自动启用。首次运行需要手动触发：

1. 进入仓库的 **Actions** 标签页
2. 在左侧工作流列表中找到 `ArXiv Daily Crawler`
3. 点击进入工作流详情页
4. 点击右侧的 `Run workflow` 按钮
5. 确认并点击 `Run workflow` 开始执行

### 4. 首次运行说明

首次运行时会：

- 从配置的 `start_date`（默认为 2025-01-01）爬取到当前日期的所有论文
- 这可能需要较长时间（取决于时间跨度和论文数量）
- 生成的 Markdown 文件会自动提交到仓库

你可以通过以下方式查看运行进度：

1. 在 **Actions** 标签页查看工作流运行状态
2. 点击具体的运行记录查看详细日志
3. 日志中会显示爬取进度和论文数量

### 5. 验证部署

首次运行完成后：

1. 进入仓库的 **Code** 标签页
2. 查看 `output/arxiv_papers.md` 文件
3. 应该能看到按分类组织的论文列表
4. 每篇论文包含标题、作者、发布日期、PDF 链接等信息

## 日常使用

### 自动定时执行

工作流配置为每天 UTC 时间 00:00（北京时间 08:00）自动执行：

- 只爬取上次运行后的新论文
- 自动去重，避免重复
- 有新论文时会自动提交到仓库

### 手动触发

如需立即更新：

1. 进入 **Actions** 标签页
2. 选择 `ArXiv Daily Crawler` 工作流
3. 点击 `Run workflow` 按钮

### 修改配置

如需修改爬取参数：

1. 编辑 `config/arxiv_config.yaml` 文件
2. 常用修改项：
   - `categories`: 添加或删除分类
   - `keywords`: 修改关键词过滤
   - `start_date`: 修改起始日期（通常不需要修改）
3. 提交并推送更改：
   ```bash
   git add config/arxiv_config.yaml
   git commit -m "Update configuration"
   git push
   ```

## 高级配置

### 修改执行频率

编辑 `.github/workflows/arxiv-daily.yml` 中的 `schedule` 部分：

```yaml
schedule:
  # 每 12 小时执行一次
  - cron: '0 */12 * * *'
  
  # 或每天北京时间 20:00 执行
  - cron: '0 12 * * *'
```

Cron 表达式格式：`分 时 日 月 周`

示例：
- `0 0 * * *` - 每天 00:00
- `0 */6 * * *` - 每 6 小时
- `0 9 * * 1-5` - 周一到周五的 09:00
- `30 8,20 * * *` - 每天 08:30 和 20:30

### 启用 GitHub Pages（可选）

如果想在线查看生成的 Markdown 文件：

1. 进入仓库的 **Settings** 标签页
2. 在左侧菜单找到 **Pages**
3. 在 **Build and deployment** 部分：
   - Source: 选择 `Deploy from a branch`
   - Branch: 选择 `main` 分支，文件夹选择 `/ (root)`
4. 点击 `Save`

等待几分钟后，你的 GitHub Pages 网站就会生效，地址为：
`https://your-username.github.io/arxiv-papers/`

## 监控和维护

### 查看运行历史

1. 进入 **Actions** 标签页
2. 可以看到所有运行记录
3. 点击具体记录查看详细日志

### 处理运行失败

如果工作流运行失败：

1. 查看失败日志，确定错误原因
2. 常见问题：
   - 依赖安装失败：检查 `requirements.txt`
   - 网络问题：等待后重试
   - ArXiv API 限制：可能需要调整爬取频率
3. 修复后重新触发工作流

### 清理旧数据

如果需要重新开始：

1. 删除 `output/arxiv_papers.md` 和 `output/arxiv_papers.state`
2. 修改 `config/arxiv_config.yaml` 中的 `start_date`
3. 提交更改并手动触发工作流

## 常见问题

### Q: 首次运行很久没完成怎么办？

A: 首次运行从 2025-01-01 爬取到现在，可能需要较长时间。可以：
- 缩短 `start_date` 范围
- 减少 `max_papers_per_category` 数量
- 耐心等待，查看日志了解进度

### Q: 为什么没有新论文？

A: 可能原因：
- 关键词过滤太严格
- 当天确实没有新论文发布
- 查看日志了解爬取情况

### Q: 如何添加更多分类？

A: 编辑 `config/arxiv_config.yaml`，在 `categories` 列表中添加新的分类代码。

### Q: 生成的文件太大怎么办？

A: 可以：
- 减少 `max_papers_per_category` 数量
- 设置更严格的关键词过滤
- 定期清理旧数据

## 安全建议

1. **保护敏感信息**：不要在配置文件中包含敏感信息
2. **使用 Private 仓库**：如果包含私人信息，使用私有仓库
3. **定期更新依赖**：保持 Python 依赖最新版本
4. **监控资源使用**：注意 GitHub Actions 的使用限制

## 扩展功能

### 添加邮件通知

可以修改工作流，在更新后发送邮件通知：

```yaml
- name: Send email notification
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "ArXiv Papers Updated"
    body: "New papers have been added to the repository."
```

### 添加 Telegram 通知

```yaml
- name: Send Telegram notification
  uses: appleboy/telegram-action@master
  with:
    to: ${{ secrets.TELEGRAM_TO }}
    token: ${{ secrets.TELEGRAM_TOKEN }}
    message: "ArXiv papers updated successfully!"
```

## 技术支持

如遇到问题：

1. 查看 GitHub Actions 日志
2. 检查配置文件语法
3. 参考 [ArXiv API 文档](https://arxiv.org/help/api)
4. 提交 Issue 到项目仓库

---

祝使用愉快！🎉
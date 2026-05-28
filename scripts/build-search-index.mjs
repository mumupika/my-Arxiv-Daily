#!/usr/bin/env node

/**
 * 从 docs 目录下的每日 markdown 文件中提取论文数据，
 * 生成 docs/public/search-index.json 供搜索页面使用。
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const docsDir = path.resolve(__dirname, '..', 'docs')
const outputFile = path.resolve(docsDir, 'public', 'search-index.json')

// 确保输出目录存在
const publicDir = path.resolve(docsDir, 'public')
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true })
}

/**
 * 从 markdown 表格行中提取单元格内容
 */
function parseTableCells(line) {
  // 匹配 | 分隔的单元格，去除首尾空格
  const cells = line.split('|').map(c => c.trim()).filter(c => c.length > 0)
  return cells
}

/**
 * 从 markdown 链接格式 [text](url) 中提取 text 和 url
 */
function parseMarkdownLink(text) {
  const match = text.match(/\[([^\]]*)\]\(([^)]*)\)/)
  if (match) {
    return { text: match[1], url: match[2] }
  }
  return { text, url: '' }
}

/**
 * 解析单个每日 markdown 文件
 */
function parseDailyFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const lines = content.split('\n')
  const papers = []

  let currentDate = ''
  let currentCategory = ''

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    // 匹配日期标题 # YYYY-MM-DD
    const dateMatch = line.match(/^#\s+(\d{4}-\d{2}-\d{2})/)
    if (dateMatch) {
      currentDate = dateMatch[1]
      continue
    }

    // 匹配分类标题 ## cs.XX - Description
    const categoryMatch = line.match(/^##\s+(.+)/)
    if (categoryMatch) {
      currentCategory = categoryMatch[1]
      continue
    }

    // 跳过表头和分隔行
    if (line.startsWith('|') && (line.includes('---') || line.includes('标题'))) {
      continue
    }

    // 匹配表格数据行
    if (line.startsWith('|') && currentDate && currentCategory) {
      const cells = parseTableCells(line)
      if (cells.length >= 5) {
        const titleLink = parseMarkdownLink(cells[0])
        const pdfLink = parseMarkdownLink(cells[3])

        papers.push({
          date: currentDate,
          category: currentCategory,
          title: titleLink.text,
          titleUrl: titleLink.url,
          author: cells[1],
          publishDate: cells[2],
          pdfUrl: pdfLink.url,
          abstract: cells[4],
          // 用于搜索的全文（标题 + 作者 + 摘要）
          searchText: `${titleLink.text} ${cells[1]} ${cells[4]}`.toLowerCase()
        })
      }
    }
  }

  return papers
}

/**
 * 主函数：扫描所有 YYYY-MM 目录下的 YYYY-MM-DD.md 文件
 */
function buildSearchIndex() {
  const allPapers = []

  const entries = fs.readdirSync(docsDir, { withFileTypes: true })
  const monthDirs = entries
    .filter(d => d.isDirectory() && /^\d{4}-\d{2}$/.test(d.name))
    .map(d => d.name)
    .sort()

  for (const month of monthDirs) {
    const monthDir = path.join(docsDir, month)
    const files = fs.readdirSync(monthDir)

    for (const file of files) {
      if (/^\d{4}-\d{2}-\d{2}\.md$/.test(file)) {
        const filePath = path.join(monthDir, file)
        const papers = parseDailyFile(filePath)
        allPapers.push(...papers)
      }
    }
  }

  // 按日期倒序排列
  allPapers.sort((a, b) => b.date.localeCompare(a.date))

  // 写入 JSON
  const output = {
    totalCount: allPapers.length,
    generatedAt: new Date().toISOString(),
    papers: allPapers
  }

  fs.writeFileSync(outputFile, JSON.stringify(output), 'utf-8')
  console.log(`✅ 搜索索引已生成: ${allPapers.length} 篇论文 -> ${outputFile}`)
}

buildSearchIndex()
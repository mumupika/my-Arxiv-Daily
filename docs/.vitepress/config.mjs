import { defineConfig } from 'vitepress'
import katex from 'markdown-it-katex'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const docsDir = path.resolve(__dirname, '..')

/**
 * 自动扫描 docs 目录下的 YYYY-MM 文件夹，生成侧边栏配置
 * 按年份分组，年份和月份均按倒序排列
 * 最近的两个年份默认展开，更早的年份默认折叠
 */
function generateSidebar() {
  const entries = fs.readdirSync(docsDir, { withFileTypes: true })

  // 找出所有 YYYY-MM 格式的目录
  const monthDirs = entries
    .filter(d => d.isDirectory() && /^\d{4}-\d{2}$/.test(d.name))
    .map(d => d.name)
    .sort()
    .reverse() // 最新的月份排在前面

  // 按年份分组
  const yearMap = new Map()
  for (const month of monthDirs) {
    const year = month.substring(0, 4)
    if (!yearMap.has(year)) {
      yearMap.set(year, [])
    }
    yearMap.get(year).push(month)
  }

  // 年份倒序排列
  const years = [...yearMap.keys()].sort().reverse()

  // 生成侧边栏 items
  const items = years.map((year, index) => ({
    text: `${year}年`,
    collapsed: index >= 2, // 最近的两个年份展开，更早的折叠
    items: yearMap.get(year).map(month => ({
      text: month,
      link: `/${month}/`
    }))
  }))

  return items
}

export default defineConfig({
  base: '/my-Arxiv-Daily/',
  
  title: 'ArXiv Daily Papers',
  description: '自动爬取的 arxiv 论文汇总，按日期分类',
  
  // 配置LaTeX数学公式渲染
  markdown: {
    config: (md) => {
      md.use(katex)
    }
  },
  
  // 调整页面布局
  contentProps: {
    aside: true
  },
  
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: 'GitHub', link: 'https://github.com/mumupika/my-Arxiv-Daily' }
    ],

    // 启用右侧目录导航
    outline: {
      level: [2, 3],
      label: '页面导航'
    },

    sidebar: [
      {
        text: '论文归档',
        collapsed: false,
        items: generateSidebar()
      }
    ],

    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2024-present'
    }
  }
})
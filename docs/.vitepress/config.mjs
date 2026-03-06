import { defineConfig } from 'vitepress'
import katex from 'markdown-it-katex'

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
        items: [
          {
            text: '2026年',
            collapsed: false,
            items: [
              { text: '2026-03', link: '/2026-03/' },
              { text: '2026-02', link: '/2026-02/' },
              { text: '2026-01', link: '/2026-01/' }
            ]
          },
          {
            text: '2025年',
            collapsed: false,
            items: [
              { text: '2025-12', link: '/2025-12/' },
              { text: '2025-11', link: '/2025-11/' },
              { text: '2025-10', link: '/2025-10/' },
              { text: '2025-09', link: '/2025-09/' },
              { text: '2025-08', link: '/2025-08/' },
              { text: '2025-07', link: '/2025-07/' },
              { text: '2025-06', link: '/2025-06/' },
              { text: '2025-05', link: '/2025-05/' },
              { text: '2025-04', link: '/2025-04/' },
              { text: '2025-03', link: '/2025-03/' },
              { text: '2025-02', link: '/2025-02/' },
              { text: '2025-01', link: '/2025-01/' }
            ]
          },
          {
            text: '2024年',
            collapsed: true,
            items: [
              { text: '2024-12', link: '/2024-12/' },
              { text: '2024-11', link: '/2024-11/' },
              { text: '2024-10', link: '/2024-10/' },
              { text: '2024-09', link: '/2024-09/' }
            ]
          }
        ]
      }
    ],

    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2024-present'
    }
  }
})

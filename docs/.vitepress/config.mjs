import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'ArXiv Daily Papers',
  description: '自动爬取的 arxiv 论文汇总，按日期分类',
  
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: 'GitHub', link: 'https://github.com/mumupika/my-Arxiv-Daily' }
    ],

    sidebar: [
      {
        text: '论文归档',
        items: [
          {
            text: '2024年',
            collapsed: false,
            items: [
              { text: '2024-09', link: '/docs/2024-09/2024-09-01' },
              { text: '2024-10', link: '/docs/2024-10/2024-10-01' },
              { text: '2024-11', link: '/docs/2024-11/2024-11-01' },
              { text: '2024-12', link: '/docs/2024-12/2024-12-01' }
            ]
          },
          {
            text: '2025年',
            collapsed: false,
            items: [
              { text: '2025-01', link: '/docs/2025-01/2025-01-01' },
              { text: '2025-02', link: '/docs/2025-02/2025-02-01' },
              { text: '2025-03', link: '/docs/2025-03/2025-03-01' }
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
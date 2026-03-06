import { defineConfig } from 'vitepress'

export default defineConfig({
  // GitHub Pages 部署需要设置 base 路径
  base: '/my-Arxiv-Daily/',
  
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
              { text: '2024-09', link: '/2024-09/' },
              { text: '2024-10', link: '/2024-10/' },
              { text: '2024-11', link: '/2024-11/' },
              { text: '2024-12', link: '/2024-12/' }
            ]
          },
          {
            text: '2025年',
            collapsed: false,
            items: [
              { text: '2025-01', link: '/2025-01/' },
              { text: '2025-02', link: '/2025-02/' },
              { text: '2025-03', link: '/2025-03/' },
              { text: '2025-04', link: '/2025-04/' },
              { text: '2025-05', link: '/2025-05/' },
              { text: '2025-06', link: '/2025-06/' },
              { text: '2025-07', link: '/2025-07/' },
              { text: '2025-08', link: '/2025-08/' },
              { text: '2025-09', link: '/2025-09/' },
              { text: '2025-10', link: '/2025-10/' },
              { text: '2025-11', link: '/2025-11/' },
              { text: '2025-12', link: '/2025-12/' }
            ]
          },
          {
            text: '2026年',
            collapsed: false,
            items: [
              { text: '2026-01', link: '/2026-01/' },
              { text: '2026-02', link: '/2026-02/' },
              { text: '2026-03', link: '/2026-03/' }
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
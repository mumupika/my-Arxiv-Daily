import DefaultTheme from 'vitepress/theme'
import './custom.css'
import SearchPage from './SearchPage.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app, router }) {
    // 注册搜索页面组件
    app.component('SearchPage', SearchPage)

    if (typeof document !== 'undefined') {
      
      // ==========================================
      // 1. 创建视图切换按钮
      // ==========================================
      const toggleBtn = document.createElement('button')
      toggleBtn.className = 'sidebar-toggle'
      toggleBtn.innerHTML = '📖 切换视图'
      
      let isFullWidth = false
      
      const toggleView = () => {
        isFullWidth = !isFullWidth
        if (isFullWidth) {
          document.body.classList.add('full-width')
          document.body.classList.remove('sidebar-visible')
          toggleBtn.innerHTML = '◀ 显示侧栏'
        } else {
          document.body.classList.remove('full-width')
          document.body.classList.add('sidebar-visible')
          toggleBtn.innerHTML = '📖 切换视图'
        }
      }
      
      toggleBtn.addEventListener('click', toggleView)
      
      // ==========================================
      // 2. 监听鼠标滚动，实现顶栏自动收缩
      // ==========================================
      let lastScrollTop = 0;
      window.addEventListener('scroll', () => {
        let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        
        // 向下滚动超过 60px 时隐藏顶栏
        if (currentScroll > lastScrollTop && currentScroll > 60) {
          document.body.classList.add('nav-hidden');
        } else {
          // 向上滚动时显示顶栏
          document.body.classList.remove('nav-hidden');
        }
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll; // 兼容移动端回弹
      }, { passive: true });

      // ==========================================
      // 3. 页面初始化
      // ==========================================
      // 使用 router.onAfterRouteChanged 确保页面切换后也能初始化
      const initPage = () => {
        document.body.appendChild(toggleBtn)
        document.body.classList.add('sidebar-visible')
      }

      // 延迟初始化，确保 DOM 就绪
      setTimeout(initPage, 100)
    }
  }
}
import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app, router }) {
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
      setTimeout(() => {
        document.body.appendChild(toggleBtn)
        document.body.classList.add('sidebar-visible')
        
        // 修复标题
        fixNavBarTitle()
      }, 100)
    }
  }
}

// ==========================================
// 4. 修复顶栏与侧栏标题逻辑
// ==========================================
function fixNavBarTitle() {
  const navBarTitle = document.querySelector('.VPNavBarTitle .title')
  
  if (navBarTitle) {
    // 强制将顶栏文字修改为自定义标题
    navBarTitle.textContent = 'arxiv daily papers'
    
    // 【关键修复】取消之前的 display: none，让顶栏左上角的字显示出来！
    navBarTitle.style.display = 'flex' 
  }
}
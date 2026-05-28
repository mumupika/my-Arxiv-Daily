<template>
  <div class="enhanced-search">
    <!-- 搜索头部 -->
    <div class="search-header">
      <h1>🔍 论文搜索</h1>
      <p class="search-desc">在所有论文中搜索关键词，支持按时间范围筛选</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-controls">
      <div class="search-input-row">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="keyword"
            type="text"
            placeholder="输入关键词搜索论文标题、作者、摘要..."
            class="search-input"
            @input="debouncedSearch"
            @keydown.enter="doSearch"
          />
          <button v-if="keyword" class="clear-btn" @click="clearSearch">✕</button>
        </div>
        <button class="search-btn" @click="doSearch">搜索</button>
      </div>

      <!-- 时间范围筛选 -->
      <div class="date-filter">
        <span class="filter-label">📅 时间范围：</span>
        <input
          v-model="startDate"
          type="date"
          class="date-input"
          @change="doSearch"
        />
        <span class="date-separator">至</span>
        <input
          v-model="endDate"
          type="date"
          class="date-input"
          @change="doSearch"
        />
        <button class="reset-btn" @click="resetDateFilter" title="重置时间范围">重置</button>

        <!-- 快捷时间选择 -->
        <div class="quick-dates">
          <button
            v-for="qd in quickDates"
            :key="qd.label"
            class="quick-date-btn"
            :class="{ active: activeQuickDate === qd.label }"
            @click="applyQuickDate(qd)"
          >
            {{ qd.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>正在加载搜索索引...</span>
    </div>

    <!-- 搜索结果 -->
    <div v-else-if="keyword || hasFilter" class="search-results">
      <div class="results-header">
        <span class="results-count">
          找到 <strong>{{ filteredResults.length }}</strong> 篇相关论文
          <span v-if="searchTime">（耗时 {{ searchTime }}ms）</span>
        </span>
        <select v-model="sortBy" class="sort-select" @change="doSearch">
          <option value="date-desc">日期 newest → oldest</option>
          <option value="date-asc">日期 oldest → newest</option>
          <option value="relevance">相关度</option>
        </select>
      </div>

      <div v-if="filteredResults.length === 0" class="no-results">
        <div class="no-results-icon">📭</div>
        <p>未找到匹配的论文，请尝试其他关键词或调整时间范围</p>
      </div>

      <div v-else class="results-list">
        <div
          v-for="(paper, idx) in paginatedResults"
          :key="idx"
          class="paper-card"
        >
          <div class="paper-header">
            <a
              v-if="paper.titleUrl"
              :href="paper.titleUrl"
              target="_blank"
              class="paper-title"
              v-html="highlightText(paper.title)"
            ></a>
            <span v-else class="paper-title" v-html="highlightText(paper.title)"></span>
            <span class="paper-date">{{ paper.date }}</span>
          </div>

          <div class="paper-meta">
            <span class="paper-author" v-html="highlightText(paper.author)"></span>
            <span class="paper-category">{{ paper.category }}</span>
          </div>

          <div class="paper-abstract" v-html="highlightAbstract(paper.abstract)"></div>

          <div class="paper-actions">
            <a v-if="paper.pdfUrl" :href="paper.pdfUrl" target="_blank" class="paper-pdf">
              📄 下载 PDF
            </a>
            <a v-if="paper.titleUrl" :href="paper.titleUrl" target="_blank" class="paper-arxiv">
              🔗 arXiv 页面
            </a>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          ← 上一页
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页 →
        </button>
      </div>
    </div>

    <!-- 初始状态 -->
    <div v-else class="initial-state">
      <div class="initial-icon">📚</div>
      <p>输入关键词开始搜索论文</p>
      <div class="search-stats">
        <span>已索引 <strong>{{ totalCount }}</strong> 篇论文</span>
        <span v-if="generatedAt"> · 索引更新于 {{ formatDate(generatedAt) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const keyword = ref('')
    const startDate = ref('')
    const endDate = ref('')
    const sortBy = ref('date-desc')
    const loading = ref(true)
    const searchTime = ref(null)
    const currentPage = ref(1)
    const pageSize = 20
    const activeQuickDate = ref('')

    // 搜索索引数据
    const allPapers = ref([])
    const totalCount = ref(0)
    const generatedAt = ref('')

    // 快捷时间选项
    const quickDates = [
      { label: '最近7天', days: 7 },
      { label: '最近30天', days: 30 },
      { label: '最近3个月', days: 90 },
      { label: '最近半年', days: 180 },
      { label: '最近1年', days: 365 },
    ]

    // 防抖定时器
    let debounceTimer = null

    const debouncedSearch = () => {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        doSearch()
      }, 300)
    }

    const hasFilter = computed(() => {
      return startDate.value || endDate.value
    })

    // 执行搜索
    const doSearch = () => {
      currentPage.value = 1
      // searchTime 由 filteredResults 的计算触发
    }

    // 搜索结果过滤和排序
    const filteredResults = computed(() => {
      const start = performance.now()
      let results = allPapers.value

      // 关键词过滤
      const kw = keyword.value.trim().toLowerCase()
      if (kw) {
        // 支持多关键词（空格分隔，AND 逻辑）
        const keywords = kw.split(/\s+/).filter(k => k.length > 0)
        results = results.filter(paper => {
          return keywords.every(k => paper.searchText.includes(k))
        })
      }

      // 日期范围过滤
      if (startDate.value) {
        results = results.filter(p => p.date >= startDate.value)
      }
      if (endDate.value) {
        results = results.filter(p => p.date <= endDate.value)
      }

      // 排序
      if (sortBy.value === 'date-desc') {
        results.sort((a, b) => b.date.localeCompare(a.date))
      } else if (sortBy.value === 'date-asc') {
        results.sort((a, b) => a.date.localeCompare(b.date))
      } else if (sortBy.value === 'relevance' && kw) {
        // 简单相关度：标题匹配权重最高，作者其次，摘要最低
        const keywords = kw.split(/\s+/).filter(k => k.length > 0)
        results.sort((a, b) => {
          const scoreA = calcRelevance(a, keywords)
          const scoreB = calcRelevance(b, keywords)
          return scoreB - scoreA
        })
      }

      searchTime.value = Math.round(performance.now() - start)
      return results
    })

    // 计算相关度分数
    const calcRelevance = (paper, keywords) => {
      let score = 0
      for (const kw of keywords) {
        if (paper.title.toLowerCase().includes(kw)) score += 10
        if (paper.author.toLowerCase().includes(kw)) score += 5
        if (paper.abstract.toLowerCase().includes(kw)) score += 1
      }
      return score
    }

    // 分页
    const totalPages = computed(() => {
      return Math.ceil(filteredResults.value.length / pageSize)
    })

    const paginatedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      return filteredResults.value.slice(start, start + pageSize)
    })

    // 高亮关键词
    const highlightText = (text) => {
      if (!text) return ''
      const kw = keyword.value.trim()
      if (!kw) return escapeHtml(text)

      const keywords = kw.split(/\s+/).filter(k => k.length > 0)
      let result = escapeHtml(text)

      for (const k of keywords) {
        const escaped = k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        const regex = new RegExp(`(${escaped})`, 'gi')
        result = result.replace(regex, '<mark class="search-highlight">$1</mark>')
      }
      return result
    }

    // 高亮摘要（截取匹配片段）
    const highlightAbstract = (abstract) => {
      if (!abstract) return ''
      const kw = keyword.value.trim()
      const escaped = escapeHtml(abstract)

      if (!kw) {
        // 无关键词时截断显示
        return escaped.length > 300 ? escaped.substring(0, 300) + '...' : escaped
      }

      const keywords = kw.split(/\s+/).filter(k => k.length > 0)
      let result = escaped

      // 高亮所有关键词
      for (const k of keywords) {
        const kEscaped = k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        const regex = new RegExp(`(${kEscaped})`, 'gi')
        result = result.replace(regex, '<mark class="search-highlight">$1</mark>')
      }

      // 截取包含高亮关键词的片段
      const firstMark = result.indexOf('<mark')
      if (firstMark > 80) {
        // 找到第一个高亮前的合适截断点
        const beforeText = result.substring(0, firstMark)
        const lastSpace = beforeText.lastIndexOf(' ', firstMark - 40)
        const cutPoint = lastSpace > 0 ? lastSpace : firstMark - 60
        result = '...' + result.substring(cutPoint)
      }

      if (result.length > 400) {
        result = result.substring(0, 400) + '...'
      }

      return result
    }

    const escapeHtml = (text) => {
      return text
        .replace(/&/g, '\x26amp;')
        .replace(/</g, '\x26lt;')
        .replace(/>/g, '\x26gt;')
        .replace(/"/g, '\x26quot;')
    }

    const clearSearch = () => {
      keyword.value = ''
      doSearch()
    }

    const resetDateFilter = () => {
      startDate.value = ''
      endDate.value = ''
      activeQuickDate.value = ''
      doSearch()
    }

    const applyQuickDate = (qd) => {
      activeQuickDate.value = qd.label
      const now = new Date()
      const past = new Date(now.getTime() - qd.days * 24 * 60 * 60 * 1000)
      startDate.value = past.toISOString().split('T')[0]
      endDate.value = now.toISOString().split('T')[0]
      doSearch()
    }

    const formatDate = (isoStr) => {
      if (!isoStr) return ''
      const d = new Date(isoStr)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    }

    // 加载搜索索引
    onMounted(async () => {
      try {
        // VitePress base 路径
        const base = '/my-Arxiv-Daily/'
        const res = await fetch(`${base}search-index.json`)
        const data = await res.json()
        allPapers.value = data.papers || []
        totalCount.value = data.totalCount || 0
        generatedAt.value = data.generatedAt || ''
      } catch (e) {
        console.error('加载搜索索引失败:', e)
      } finally {
        loading.value = false
      }
    })

    return {
      keyword, startDate, endDate, sortBy,
      loading, searchTime, currentPage, activeQuickDate,
      totalCount, generatedAt,
      quickDates,
      hasFilter,
      filteredResults, paginatedResults, totalPages,
      doSearch, debouncedSearch,
      highlightText, highlightAbstract,
      clearSearch, resetDateFilter, applyQuickDate, formatDate,
    }
  }
}
</script>

<style scoped>
.enhanced-search {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 16px;
}

.search-header {
  text-align: center;
  margin-bottom: 32px;
}

.search-header h1 {
  font-size: 2em;
  margin-bottom: 8px;
  color: var(--vp-c-text-1);
}

.search-desc {
  color: var(--vp-c-text-2);
  font-size: 1.1em;
}

/* 搜索控件 */
.search-controls {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.search-input-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 40px;
  border: 2px solid var(--vp-c-divider);
  border-radius: 8px;
  font-size: 16px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  transition: border-color 0.2s;
  outline: none;
}

.search-input:focus {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 0 0 3px var(--vp-c-brand-soft);
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  font-size: 16px;
  color: var(--vp-c-text-3);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.clear-btn:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-soft);
}

.search-btn {
  padding: 12px 24px;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.search-btn:hover {
  background: var(--vp-c-brand-2);
}

/* 时间筛选 */
.date-filter {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.date-input {
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-size: 14px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  outline: none;
}

.date-input:focus {
  border-color: var(--vp-c-brand-1);
}

.date-separator {
  color: var(--vp-c-text-3);
  font-size: 14px;
}

.reset-btn {
  padding: 6px 12px;
  background: none;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-size: 13px;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.quick-dates {
  display: flex;
  gap: 6px;
  margin-left: auto;
  flex-wrap: wrap;
}

.quick-date-btn {
  padding: 4px 10px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 14px;
  font-size: 12px;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-date-btn:hover,
.quick-date-btn.active {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

/* 结果区域 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.results-count {
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.sort-select {
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-size: 13px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  cursor: pointer;
  outline: none;
}

/* 论文卡片 */
.paper-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.paper-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 2px 12px var(--vp-c-brand-soft);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.paper-title {
  font-size: 1.05em;
  font-weight: 600;
  color: var(--vp-c-brand-1);
  text-decoration: none;
  line-height: 1.4;
  flex: 1;
}

.paper-title:hover {
  color: var(--vp-c-brand-2);
  text-decoration: underline;
}

.paper-date {
  font-size: 0.85em;
  color: var(--vp-c-text-3);
  white-space: nowrap;
  background: var(--vp-c-bg);
  padding: 2px 8px;
  border-radius: 4px;
}

.paper-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.paper-author {
  font-size: 0.9em;
  color: var(--vp-c-text-2);
}

.paper-category {
  font-size: 0.8em;
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  padding: 2px 8px;
  border-radius: 4px;
}

.paper-abstract {
  font-size: 0.9em;
  color: var(--vp-c-text-2);
  line-height: 1.6;
  margin-bottom: 10px;
}

.paper-actions {
  display: flex;
  gap: 12px;
}

.paper-pdf,
.paper-arxiv {
  font-size: 0.85em;
  color: var(--vp-c-brand-1);
  text-decoration: none;
  padding: 4px 10px;
  border: 1px solid var(--vp-c-brand-soft);
  border-radius: 6px;
  transition: all 0.2s;
}

.paper-pdf:hover,
.paper-arxiv:hover {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
}

/* 高亮样式 */
:deep(.search-highlight) {
  background: rgba(255, 213, 0, 0.4);
  color: inherit;
  padding: 1px 2px;
  border-radius: 2px;
  border-bottom: 2px solid #f59e0b;
  font-weight: 600;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 48px;
  color: var(--vp-c-text-2);
}

.loading-spinner {
  display: inline-block;
  width: 32px;
  height: 32px;
  border: 3px solid var(--vp-c-divider);
  border-top-color: var(--vp-c-brand-1);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 无结果 */
.no-results {
  text-align: center;
  padding: 48px;
  color: var(--vp-c-text-2);
}

.no-results-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

/* 初始状态 */
.initial-state {
  text-align: center;
  padding: 64px 16px;
  color: var(--vp-c-text-2);
}

.initial-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.search-stats {
  margin-top: 12px;
  font-size: 0.9em;
  color: var(--vp-c-text-3);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px 0;
}

.page-btn {
  padding: 8px 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  color: var(--vp-c-text-1);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  color: var(--vp-c-text-2);
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .search-input-row {
    flex-direction: column;
  }

  .date-filter {
    flex-direction: column;
    align-items: flex-start;
  }

  .quick-dates {
    margin-left: 0;
    margin-top: 8px;
  }

  .paper-header {
    flex-direction: column;
  }

  .results-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>